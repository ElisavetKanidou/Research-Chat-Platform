"""
Section Content Service - PRODUCTION READY
backend/app/services/section_content_service.py

Service for managing paper section content operations
"""
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import logging

from app.models.paper import Paper, PaperSection
from app.core.exceptions import NotFoundException, AuthorizationException, ValidationException

logger = logging.getLogger(__name__)


class SectionContentService:
    """Service for managing content operations on paper sections"""

    # Section type to title mapping
    SECTION_TITLES = {
        "abstract": "Abstract",
        "introduction": "Introduction",
        "literature_review": "Literature Review",
        "methodology": "Methodology",
        "results": "Results",
        "discussion": "Discussion",
        "conclusion": "Conclusion",
        "references": "References"
    }

    async def add_chat_content_to_section(
            self,
            db: AsyncSession,
            user_id: str,
            paper_id: str,
            section_type: str,
            content: str,
            message_id: Optional[str] = None,
            append: bool = True
    ) -> Dict:
        """Add chat-generated content to a specific paper section."""

        # ✅ ADD THIS AT THE START:
        logger.info(f"Adding content to {section_type} for paper {paper_id}")

        # FIX: Eager load paper WITH sections
        result = await db.execute(
            select(Paper)
            .options(selectinload(Paper.sections))  # ✅ KEY FIX!
            .where(Paper.id == UUID(paper_id))
        )
        paper = result.scalar_one_or_none()

        if not paper:
            raise NotFoundException(f"Paper not found")

        if not paper.is_viewable_by(user_id):
            raise AuthorizationException("No permission")
        # ✅ END OF FIX
        # Find or create section
        section = await self._get_or_create_section(
            db, paper, section_type
        )

        # Update content
        old_content = section.content or ""

        if append and old_content:
            # Append with proper spacing
            new_content = old_content.rstrip() + "\n\n" + content.strip()
        else:
            # Replace
            new_content = content.strip()

        section.content = new_content
        section.word_count = len(new_content.split())

        # Update section status based on content
        if section.word_count > 0:
            if section.status == "not-started":
                section.status = "in-progress"

        # Update paper word count and progress
        await self._update_paper_metrics(db, paper)

        await db.commit()
        await db.refresh(section)

        logger.info(
            f"Successfully added {section.word_count} words to {section_type} "
            f"for paper {paper_id}"
        )

        return {
            "sectionId": str(section.id),
            "sectionType": section_type,
            "title": section.title,
            "content": section.content,
            "wordCount": section.word_count,
            "status": section.status,
            "updatedAt": section.updated_at.isoformat() if section.updated_at else None
        }

    async def get_section_content(
            self,
            db: AsyncSession,
            paper_id: str,
            section_type: str,
            user_id: str
    ) -> Optional[str]:
        """
        Get content of a specific section.

        Args:
            db: Database session
            paper_id: Paper ID
            section_type: Section type
            user_id: User ID requesting content

        Returns:
            Section content or None if not found

        Raises:
            AuthorizationException: If user doesn't have view permission
        """

        paper = await db.get(Paper, UUID(paper_id))

        if not paper:
            return None

        if not paper.is_viewable_by(user_id):
            raise AuthorizationException(
                "You don't have permission to view this paper"
            )

        # Find section
        section_title = self.SECTION_TITLES.get(section_type)
        if not section_title:
            return None

        for section in paper.sections:
            if section.title == section_title:
                return section.content

        return None

    async def get_all_section_contents(
            self,
            db: AsyncSession,
            paper_id: str,
            user_id: str
    ) -> List[Dict]:
        """
        Get content of all sections for a paper.

        Args:
            db: Database session
            paper_id: Paper ID
            user_id: User ID requesting content

        Returns:
            List of section dictionaries

        Raises:
            NotFoundException: If paper not found
            AuthorizationException: If user doesn't have view permission
        """

        paper = await db.get(Paper, UUID(paper_id))

        if not paper:
            raise NotFoundException(f"Paper with ID {paper_id} not found")

        if not paper.is_viewable_by(user_id):
            raise AuthorizationException(
                "You don't have permission to view this paper"
            )

        sections_data = []

        for section in sorted(paper.sections, key=lambda s: s.order):
            # Find section type from title
            section_type = None
            for stype, title in self.SECTION_TITLES.items():
                if section.title == title:
                    section_type = stype
                    break

            sections_data.append({
                "sectionId": str(section.id),
                "sectionType": section_type or "unknown",
                "title": section.title,
                "content": section.content or "",
                "wordCount": section.word_count,
                "status": section.status,
                "order": section.order
            })

        return sections_data

    async def _get_or_create_section(
            self,
            db: AsyncSession,
            paper: Paper,
            section_type: str
    ) -> PaperSection:
        """
        Get existing section or create new one.

        Args:
            db: Database session
            paper: Paper object
            section_type: Section type

        Returns:
            PaperSection object
        """

        section_title = self.SECTION_TITLES[section_type]

        # Try to find existing section
        for section in paper.sections:
            if section.title == section_title:
                return section

        # Create new section
        # Determine order based on section type
        section_order_map = {
            "abstract": 0,
            "introduction": 1,
            "literature_review": 2,
            "methodology": 3,
            "results": 4,
            "discussion": 5,
            "conclusion": 6,
            "references": 7
        }

        new_section = PaperSection(
            paper_id=paper.id,
            title=section_title,
            content="",
            order=section_order_map.get(section_type, 99),
            status="not-started",
            word_count=0
        )

        db.add(new_section)
        paper.sections.append(new_section)

        logger.info(f"Created new section {section_title} for paper {paper.id}")

        return new_section

    async def _update_paper_metrics(
            self,
            db: AsyncSession,
            paper: Paper
    ):
        """
        Update paper's total word count and progress.

        Args:
            db: Database session
            paper: Paper object
        """

        # Calculate total word count
        total_words = sum(
            section.word_count for section in paper.sections
        )

        paper.current_word_count = total_words

        # Calculate progress based on target
        if paper.target_word_count and paper.target_word_count > 0:
            progress = min(
                100,
                int((total_words / paper.target_word_count) * 100)
            )
            paper.progress = progress
        else:
            # If no target, base on sections completed
            total_sections = len(paper.sections)
            if total_sections > 0:
                completed = sum(
                    1 for s in paper.sections
                    if s.status == "completed"
                )
                paper.progress = int((completed / total_sections) * 100)

        logger.debug(
            f"Updated paper {paper.id} metrics: "
            f"{total_words} words, {paper.progress}% progress"
        )


# Create singleton instance
section_content_service = SectionContentService()