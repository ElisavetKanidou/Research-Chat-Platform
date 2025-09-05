"""
Paper management service for business logic operations
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from datetime import datetime
import uuid

from app.models.paper import Paper, PaperSection, PaperStatus, SectionStatus, PaperCollaborator
from app.models.user import User
from app.schemas.paper import (
    PaperCreate, PaperUpdate, PaperSectionCreate, PaperSectionUpdate
)
from app.core.exceptions import (
    NotFoundException, ValidationException, AuthorizationException
)


class PaperService:
    """Service for paper management operations"""

    async def create_paper(
            self,
            db: AsyncSession,
            user_id: str,
            paper_data: PaperCreate
    ) -> Paper:
        """Create a new paper with default sections"""

        # Create paper instance
        paper = Paper(
            title=paper_data.title,
            abstract=paper_data.abstract,
            status=paper_data.status,
            research_area=paper_data.research_area,
            target_word_count=paper_data.target_word_count,
            tags=paper_data.tags or [],
            co_authors=paper_data.co_authors or [],
            is_public=paper_data.is_public,
            owner_id=user_id
        )

        db.add(paper)
        await db.flush()  # Get the paper ID

        # Create default sections if not provided
        sections_data = paper_data.sections or [
            PaperSectionCreate(title="Introduction", order=1),
            PaperSectionCreate(title="Literature Review", order=2),
            PaperSectionCreate(title="Methodology", order=3),
            PaperSectionCreate(title="Results", order=4),
            PaperSectionCreate(title="Discussion", order=5),
            PaperSectionCreate(title="Conclusion", order=6),
        ]

        # Create sections
        for section_data in sections_data:
            section = PaperSection(
                title=section_data.title,
                content=section_data.content,
                status=section_data.status,
                order=section_data.order,
                paper_id=paper.id
            )
            db.add(section)

        await db.commit()
        await db.refresh(paper, ['sections'])

        return paper

    async def get_paper_by_id(
            self,
            db: AsyncSession,
            paper_id: str,
            include_sections: bool = True
    ) -> Optional[Paper]:
        """Get paper by ID with optional sections"""

        query = select(Paper).where(Paper.id == paper_id)

        if include_sections:
            query = query.options(
                selectinload(Paper.sections),
                selectinload(Paper.collaborators)
            )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_papers(
            self,
            db: AsyncSession,
            user_id: str,
            status_filter: Optional[str] = None,
            research_area: Optional[str] = None,
            search: Optional[str] = None,
            skip: int = 0,
            limit: int = 50,
            include_collaborations: bool = True
    ) -> List[Paper]:
        """Get user's papers with filtering options"""

        # Base query for owned papers
        owned_query = select(Paper).where(Paper.owner_id == user_id)

        queries = [owned_query]

        # Add collaboration query if requested
        if include_collaborations:
            collab_query = select(Paper).join(PaperCollaborator).where(
                and_(
                    PaperCollaborator.user_id == user_id,
                    PaperCollaborator.status == "accepted"
                )
            )
            queries.append(collab_query)

        # Combine queries
        if len(queries) > 1:
            query = queries[0].union(*queries[1:])
        else:
            query = queries[0]

        # Apply filters
        conditions = []

        if status_filter and status_filter != "all":
            try:
                status_enum = PaperStatus(status_filter)
                conditions.append(Paper.status == status_enum)
            except ValueError:
                raise ValidationException(f"Invalid status: {status_filter}")

        if research_area and research_area != "all":
            conditions.append(Paper.research_area.ilike(f"%{research_area}%"))

        if search and search.strip():
            search_term = f"%{search.strip()}%"
            search_conditions = or_(
                Paper.title.ilike(search_term),
                Paper.abstract.ilike(search_term),
                Paper.research_area.ilike(search_term)
            )
            conditions.append(search_conditions)

        if conditions:
            query = query.where(and_(*conditions))

        # Add pagination and ordering
        query = query.order_by(desc(Paper.updated_at)).offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def update_paper(
            self,
            db: AsyncSession,
            paper_id: str,
            updates: PaperUpdate
    ) -> Paper:
        """Update paper with provided data"""

        paper = await self.get_paper_by_id(db, paper_id)
        if not paper:
            raise NotFoundException("Paper")

        # Update fields
        update_data = updates.dict(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(paper, field):
                setattr(paper, field, value)

        paper.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(paper, ['sections'])

        return paper

    async def delete_paper(self, db: AsyncSession, paper_id: str) -> bool:
        """Delete paper and all related data"""

        paper = await self.get_paper_by_id(db, paper_id, include_sections=False)
        if not paper:
            raise NotFoundException("Paper")

        await db.delete(paper)
        await db.commit()

        return True

    async def duplicate_paper(
            self,
            db: AsyncSession,
            original_paper_id: str,
            new_owner_id: str,
            new_title: Optional[str] = None
    ) -> Paper:
        """Create a duplicate of an existing paper"""

        original = await self.get_paper_by_id(db, original_paper_id)
        if not original:
            raise NotFoundException("Paper")

        # Create new paper
        new_paper = Paper(
            title=new_title or f"{original.title} (Copy)",
            abstract=original.abstract,
            status=PaperStatus.DRAFT,
            research_area=original.research_area,
            target_word_count=original.target_word_count,
            tags=original.tags.copy() if original.tags else [],
            co_authors=original.co_authors.copy() if original.co_authors else [],
            is_public=False,  # Duplicates start as private
            owner_id=new_owner_id
        )

        db.add(new_paper)
        await db.flush()

        # Duplicate sections
        for original_section in original.sections:
            new_section = PaperSection(
                title=original_section.title,
                content=original_section.content,
                status=SectionStatus.NOT_STARTED,  # Reset status
                order=original_section.order,
                paper_id=new_paper.id
            )
            db.add(new_section)

        await db.commit()
        await db.refresh(new_paper, ['sections'])

        return new_paper

    async def create_section(
            self,
            db: AsyncSession,
            paper_id: str,
            section_data: PaperSectionCreate
    ) -> PaperSection:
        """Add a new section to a paper"""

        # Verify paper exists
        paper = await self.get_paper_by_id(db, paper_id, include_sections=False)
        if not paper:
            raise NotFoundException("Paper")

        # Create section
        section = PaperSection(
            title=section_data.title,
            content=section_data.content,
            status=section_data.status,
            order=section_data.order,
            paper_id=paper_id
        )

        db.add(section)
        await db.commit()
        await db.refresh(section)

        return section

    async def update_section(
            self,
            db: AsyncSession,
            section_id: str,
            updates: PaperSectionUpdate
    ) -> PaperSection:
        """Update a paper section"""

        # Get section
        result = await db.execute(
            select(PaperSection).where(PaperSection.id == section_id)
        )
        section = result.scalar_one_or_none()

        if not section:
            raise NotFoundException("Paper section")

        # Update fields
        update_data = updates.dict(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(section, field):
                setattr(section, field, value)

        # Update word count if content changed
        if 'content' in update_data:
            section.update_word_count()

        section.updated_at = datetime.utcnow()

        # Update parent paper's progress and word count
        await self._update_paper_metrics(db, section.paper_id)

        await db.commit()
        await db.refresh(section)

        return section

    async def delete_section(self, db: AsyncSession, section_id: str) -> bool:
        """Delete a paper section"""

        # Get section
        result = await db.execute(
            select(PaperSection).where(PaperSection.id == section_id)
        )
        section = result.scalar_one_or_none()

        if not section:
            raise NotFoundException("Paper section")

        paper_id = section.paper_id

        await db.delete(section)

        # Update parent paper metrics
        await self._update_paper_metrics(db, paper_id)

        await db.commit()

        return True

    async def get_paper_statistics(
            self,
            db: AsyncSession,
            user_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive paper statistics for a user"""

        # Count papers by status
        status_query = select(
            Paper.status,
            func.count(Paper.id).label('count')
        ).where(
            Paper.owner_id == user_id
        ).group_by(Paper.status)

        status_result = await db.execute(status_query)
        status_counts = {row.status.value: row.count for row in status_result}

        # Total word count
        word_count_query = select(
            func.sum(Paper.current_word_count).label('total_words')
        ).where(Paper.owner_id == user_id)

        word_result = await db.execute(word_count_query)
        total_words = word_result.scalar() or 0

        # Average progress
        progress_query = select(
            func.avg(Paper.progress).label('avg_progress')
        ).where(
            and_(
                Paper.owner_id == user_id,
                Paper.status != PaperStatus.ARCHIVED
            )
        )

        progress_result = await db.execute(progress_query)
        avg_progress = progress_result.scalar() or 0

        # Research areas
        areas_query = select(
            Paper.research_area,
            func.count(Paper.id).label('count')
        ).where(
            and_(
                Paper.owner_id == user_id,
                Paper.research_area.isnot(None),
                Paper.research_area != ""
            )
        ).group_by(Paper.research_area)

        areas_result = await db.execute(areas_query)
        research_areas = {row.research_area: row.count for row in areas_result}

        return {
            "total_papers": sum(status_counts.values()),
            "status_breakdown": status_counts,
            "total_words": int(total_words),
            "average_progress": round(float(avg_progress), 2),
            "published_papers": status_counts.get("published", 0),
            "active_papers": (
                    status_counts.get("in-progress", 0) +
                    status_counts.get("draft", 0) +
                    status_counts.get("in-review", 0) +
                    status_counts.get("revision", 0)
            ),
            "research_areas": research_areas
        }

    async def _update_paper_metrics(self, db: AsyncSession, paper_id: str):
        """Update paper progress and word count based on sections"""

        paper = await self.get_paper_by_id(db, paper_id)
        if not paper:
            return

        # Calculate progress and word count
        paper.calculate_progress()
        paper.calculate_word_count()

        # Save changes
        await db.commit()

    async def search_papers(
            self,
            db: AsyncSession,
            user_id: str,
            query: str,
            filters: Optional[Dict[str, Any]] = None,
            limit: int = 20
    ) -> List[Paper]:
        """Advanced paper search with full-text capabilities"""

        base_query = select(Paper).where(
            or_(
                Paper.owner_id == user_id,
                and_(
                    Paper.is_public == True,
                    Paper.status == PaperStatus.PUBLISHED
                )
            )
        )

        # Search conditions
        search_conditions = []

        if query and query.strip():
            search_term = f"%{query.strip()}%"
            search_conditions.append(
                or_(
                    Paper.title.ilike(search_term),
                    Paper.abstract.ilike(search_term),
                    Paper.research_area.ilike(search_term)
                )
            )

        # Apply filters
        if filters:
            if filters.get('status'):
                search_conditions.append(Paper.status == filters['status'])

            if filters.get('research_area'):
                search_conditions.append(
                    Paper.research_area.ilike(f"%{filters['research_area']}%")
                )

            if filters.get('date_from'):
                search_conditions.append(Paper.created_at >= filters['date_from'])

            if filters.get('date_to'):
                search_conditions.append(Paper.created_at <= filters['date_to'])

        if search_conditions:
            base_query = base_query.where(and_(*search_conditions))

        # Order by relevance (updated_at for now, could implement ranking)
        base_query = base_query.order_by(desc(Paper.updated_at)).limit(limit)

        result = await db.execute(base_query)
        return result.scalars().all()

    async def add_collaborator(
            self,
            db: AsyncSession,
            paper_id: str,
            user_id: str,
            role: str = "viewer"
    ) -> PaperCollaborator:
        """Add a collaborator to a paper"""

        # Check if collaboration already exists
        existing = await db.execute(
            select(PaperCollaborator).where(
                and_(
                    PaperCollaborator.paper_id == paper_id,
                    PaperCollaborator.user_id == user_id
                )
            )
        )

        if existing.scalar_one_or_none():
            raise ValidationException("User is already a collaborator")

        # Create collaboration
        collaboration = PaperCollaborator(
            paper_id=paper_id,
            user_id=user_id,
            role=role,
            status="accepted"  # Direct add without invitation
        )

        collaboration.accept_invitation()

        db.add(collaboration)
        await db.commit()
        await db.refresh(collaboration)

        return collaboration

    async def remove_collaborator(
            self,
            db: AsyncSession,
            paper_id: str,
            user_id: str
    ) -> bool:
        """Remove a collaborator from a paper"""

        collaboration = await db.execute(
            select(PaperCollaborator).where(
                and_(
                    PaperCollaborator.paper_id == paper_id,
                    PaperCollaborator.user_id == user_id
                )
            )
        )

        collab = collaboration.scalar_one_or_none()
        if not collab:
            raise NotFoundException("Collaboration")

        await db.delete(collab)
        await db.commit()

        return True


# Create global service instance
paper_service = PaperService()