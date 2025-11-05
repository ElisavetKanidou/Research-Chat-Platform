"""
Analytics service for research productivity tracking and insights
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from collections import defaultdict

from app.models.user import User
from app.models.paper import Paper, PaperSection, PaperStatus, SectionStatus
from app.core.exceptions import NotFoundException


class AnalyticsService:
    """Service for generating analytics and insights"""

    async def get_user_analytics(
            self,
            db: AsyncSession,
            user_id: str,
            timeframe: str = "month"
    ) -> Dict[str, Any]:
        """Get comprehensive user analytics"""

        # Calculate date range
        end_date = datetime.utcnow()
        if timeframe == "week":
            start_date = end_date - timedelta(days=7)
        elif timeframe == "month":
            start_date = end_date - timedelta(days=30)
        elif timeframe == "quarter":
            start_date = end_date - timedelta(days=90)
        elif timeframe == "year":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)

        # Get all user papers
        result = await db.execute(
            select(Paper)
            .where(Paper.owner_id == user_id)
        )
        papers = result.scalars().all()

        # Calculate basic metrics
        total_papers = len(papers)
        published_papers = len([p for p in papers if p.status == PaperStatus.PUBLISHED])
        draft_papers = len([p for p in papers if p.status == PaperStatus.DRAFT])
        in_progress_papers = len([p for p in papers if p.status in [
            PaperStatus.IN_PROGRESS, PaperStatus.IN_REVIEW, PaperStatus.REVISION
        ]])

        # Calculate word count metrics
        total_words = sum(p.current_word_count for p in papers)

        # Calculate average progress
        avg_progress = sum(p.progress for p in papers) / total_papers if total_papers > 0 else 0

        # Get unique collaborators
        all_collaborators = set()
        for paper in papers:
            all_collaborators.update(paper.co_authors)
        total_collaborators = len(all_collaborators)

        # Get unique research areas
        research_areas = len(set(p.research_area for p in papers if p.research_area))

        # Calculate average completion time
        completed_papers = [p for p in papers if p.status in [PaperStatus.COMPLETED, PaperStatus.PUBLISHED]]
        if completed_papers:
            completion_times = [
                (p.updated_at - p.created_at).days
                for p in completed_papers
                if p.updated_at and p.created_at
            ]
            avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        else:
            avg_completion_time = 0

        # Calculate productivity score (0-100)
        productivity_score = self._calculate_productivity_score(
            papers, timeframe, start_date, end_date
        )

        return {
            "user_id": user_id,
            "timeframe": timeframe,
            "total_papers": total_papers,
            "published_papers": published_papers,
            "draft_papers": draft_papers,
            "in_progress_papers": in_progress_papers,
            "total_words": total_words,
            "avg_progress": round(avg_progress, 1),
            "total_collaborators": total_collaborators,
            "research_areas": research_areas,
            "avg_completion_time": round(avg_completion_time, 1),
            "productivity_score": productivity_score,
            "last_updated": datetime.utcnow().isoformat()
        }

    async def get_paper_analytics(
            self,
            db: AsyncSession,
            paper_id: str
    ) -> Dict[str, Any]:
        """Get detailed analytics for a specific paper"""

        # Get paper with sections
        result = await db.execute(
            select(Paper)
            .where(Paper.id == paper_id)
        )
        paper = result.scalar_one_or_none()

        if not paper:
            raise NotFoundException("Paper")

        # Calculate section progress
        section_progress = []
        for section in paper.sections:
            target_words = paper.target_word_count // len(paper.sections) if paper.sections else 0
            section_progress.append({
                "section_id": str(section.id),
                "title": section.title,
                "word_count": section.word_count,
                "status": section.status.value,
                "progress": min(100, (section.word_count / target_words * 100)) if target_words > 0 else 0,
                "last_modified": section.updated_at.isoformat()
            })

        # Calculate reading time (average 200 words per minute)
        reading_time = paper.current_word_count // 200

        # Estimate completion time based on current progress
        if paper.progress > 0:
            days_so_far = (datetime.utcnow() - paper.created_at).days
            estimated_total_days = days_so_far / (paper.progress / 100)
            estimated_completion_time = max(0, estimated_total_days - days_so_far)
        else:
            estimated_completion_time = 0

        # Get collaborator count
        collaborator_count = len(paper.co_authors)

        # Calculate revision count (simplified - would need version tracking)
        revision_count = len(paper.sections)

        return {
            "paper_id": paper_id,
            "word_count": paper.current_word_count,
            "reading_time": reading_time,
            "estimated_completion_time": round(estimated_completion_time, 1),
            "collaborator_count": collaborator_count,
            "section_progress": section_progress,
            "revision_count": revision_count,
            "created_at": paper.created_at.isoformat(),
            "last_modified": paper.updated_at.isoformat()
        }

    async def get_productivity_metrics(
            self,
            db: AsyncSession,
            user_id: str,
            days: int = 30
    ) -> Dict[str, Any]:
        """Get detailed productivity metrics over time"""

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get papers modified in timeframe
        result = await db.execute(
            select(Paper)
            .where(
                and_(
                    Paper.owner_id == user_id,
                    Paper.updated_at >= start_date
                )
            )
        )
        papers = result.scalars().all()

        # Generate daily metrics
        daily_metrics = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")

            # Count papers worked on this day
            papers_on_date = [
                p for p in papers
                if p.updated_at.date() == date.date()
            ]

            # Calculate words written (simplified - would need change tracking)
            words_written = sum(p.current_word_count for p in papers_on_date) // len(
                papers_on_date) if papers_on_date else 0

            daily_metrics.append({
                "date": date_str,
                "words_written": words_written,
                "papers_worked_on": len(papers_on_date),
                "sessions_count": len(papers_on_date),  # Simplified
                "focus_score": self._calculate_focus_score(papers_on_date)
            })

        return {
            "daily": daily_metrics,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }

    async def get_collaboration_analytics(
            self,
            db: AsyncSession,
            user_id: str
    ) -> List[Dict[str, Any]]:
        """Get collaboration analytics"""

        # Get papers with collaborators
        result = await db.execute(
            select(Paper)
            .where(Paper.owner_id == user_id)
        )
        papers = result.scalars().all()

        # Aggregate collaborator data
        collaborator_data = defaultdict(lambda: {
            "shared_papers": 0,
            "total_words": 0,
            "research_areas": set()
        })

        for paper in papers:
            for author in paper.co_authors:
                collaborator_data[author]["shared_papers"] += 1
                collaborator_data[author]["total_words"] += paper.current_word_count
                if paper.research_area:
                    collaborator_data[author]["research_areas"].add(paper.research_area)

        # Format output
        collaboration_list = []
        for author, data in collaborator_data.items():
            collaboration_list.append({
                "collaborator_name": author,
                "shared_papers": data["shared_papers"],
                "total_words": data["total_words"],
                "research_areas": list(data["research_areas"]),
                "collaboration_strength": min(100, data["shared_papers"] * 20)
            })

        # Sort by collaboration strength
        collaboration_list.sort(key=lambda x: x["collaboration_strength"], reverse=True)

        return collaboration_list

    async def get_research_trends(
            self,
            db: AsyncSession,
            user_id: str
    ) -> List[Dict[str, Any]]:
        """Get research trends by area"""

        result = await db.execute(
            select(Paper)
            .where(Paper.owner_id == user_id)
        )
        papers = result.scalars().all()

        # Group by research area
        area_data = defaultdict(lambda: {
            "papers": [],
            "total_words": 0,
            "collaborators": set(),
            "published": 0
        })

        for paper in papers:
            area = paper.research_area or "Uncategorized"
            area_data[area]["papers"].append(paper)
            area_data[area]["total_words"] += paper.current_word_count
            area_data[area]["collaborators"].update(paper.co_authors)
            if paper.status == PaperStatus.PUBLISHED:
                area_data[area]["published"] += 1

        # Format output
        trends = []
        for area, data in area_data.items():
            avg_progress = sum(p.progress for p in data["papers"]) / len(data["papers"])

            trends.append({
                "area": area,
                "paper_count": len(data["papers"]),
                "word_count": data["total_words"],
                "average_progress": round(avg_progress, 1),
                "collaborators": list(data["collaborators"]),
                "publications": data["published"]
            })

        # Sort by paper count
        trends.sort(key=lambda x: x["paper_count"], reverse=True)

        return trends

    async def get_writing_patterns(
            self,
            db: AsyncSession,
            user_id: str
    ) -> Dict[str, Any]:
        """Analyze writing patterns"""

        result = await db.execute(
            select(Paper)
            .where(Paper.owner_id == user_id)
        )
        papers = result.scalars().all()

        if not papers:
            return {
                "average_words_per_paper": 0,
                "average_sections_per_paper": 0,
                "most_productive_status": "draft",
                "consistency_score": 0
            }

        # Calculate averages
        avg_words = sum(p.current_word_count for p in papers) / len(papers)
        avg_sections = sum(len(p.sections) for p in papers) / len(papers)

        # Find most productive status
        status_counts = defaultdict(int)
        for paper in papers:
            status_counts[paper.status.value] += 1

        most_productive_status = max(status_counts.items(), key=lambda x: x[1])[0] if status_counts else "draft"

        # Calculate consistency (how regular is writing activity)
        if len(papers) > 1:
            update_dates = [p.updated_at for p in papers]
            update_dates.sort()
            gaps = [(update_dates[i + 1] - update_dates[i]).days for i in range(len(update_dates) - 1)]
            avg_gap = sum(gaps) / len(gaps) if gaps else 0
            consistency_score = max(0, min(100, 100 - avg_gap))
        else:
            consistency_score = 50

        return {
            "average_words_per_paper": round(avg_words, 0),
            "average_sections_per_paper": round(avg_sections, 1),
            "most_productive_status": most_productive_status,
            "consistency_score": round(consistency_score, 1),
            "total_writing_days": len(set(p.updated_at.date() for p in papers))
        }

    async def get_insights(
            self,
            db: AsyncSession,
            user_id: str
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered insights"""

        # Get user analytics
        analytics = await self.get_user_analytics(db, user_id, "month")
        writing_patterns = await self.get_writing_patterns(db, user_id)

        insights = []

        # Productivity insight
        if analytics["productivity_score"] >= 75:
            insights.append({
                "type": "productivity",
                "title": "Great Productivity!",
                "description": f"You're in the top tier with a productivity score of {analytics['productivity_score']}. Keep up the excellent work!",
                "severity": "info",
                "actionable": False
            })
        elif analytics["productivity_score"] < 50:
            insights.append({
                "type": "productivity",
                "title": "Productivity Opportunity",
                "description": f"Your productivity score is {analytics['productivity_score']}. Consider setting daily writing goals to improve consistency.",
                "severity": "warning",
                "actionable": True,
                "suggestions": [
                    "Set a daily word count goal",
                    "Schedule dedicated writing time",
                    "Use the AI assistant for writing support"
                ]
            })

        # Collaboration insight
        if analytics["total_collaborators"] == 0:
            insights.append({
                "type": "collaboration",
                "title": "Collaboration Opportunity",
                "description": "Consider inviting collaborators to enhance your research impact.",
                "severity": "info",
                "actionable": True,
                "suggestions": [
                    "Invite co-authors to your papers",
                    "Share your work for feedback",
                    "Join research groups in your field"
                ]
            })

        # Writing consistency insight
        if writing_patterns["consistency_score"] < 60:
            insights.append({
                "type": "writing",
                "title": "Improve Writing Consistency",
                "description": "Regular writing habits lead to better productivity. Try to write more consistently.",
                "severity": "info",
                "actionable": True,
                "suggestions": [
                    "Set up a daily writing routine",
                    "Use progress tracking to stay motivated",
                    "Enable deadline reminders"
                ]
            })

        # Papers in progress insight
        if analytics["in_progress_papers"] > 5:
            insights.append({
                "type": "workflow",
                "title": "Many Papers In Progress",
                "description": f"You have {analytics['in_progress_papers']} papers in progress. Consider focusing on completing some before starting new ones.",
                "severity": "warning",
                "actionable": True,
                "suggestions": [
                    "Prioritize papers closest to completion",
                    "Set completion milestones",
                    "Archive papers that are no longer active"
                ]
            })

        return insights

    def _calculate_productivity_score(
            self,
            papers: List[Paper],
            timeframe: str,
            start_date: datetime,
            end_date: datetime
    ) -> int:
        """Calculate productivity score (0-100)"""

        if not papers:
            return 0

        # Factors contributing to productivity
        recent_activity = len([p for p in papers if p.updated_at >= start_date])
        completion_rate = len([p for p in papers if p.status in [PaperStatus.COMPLETED, PaperStatus.PUBLISHED]]) / len(
            papers)
        avg_progress = sum(p.progress for p in papers) / len(papers)

        # Weighted score
        activity_score = min(100, (recent_activity / len(papers)) * 100)
        completion_score = completion_rate * 100
        progress_score = avg_progress

        # Combined weighted score
        productivity_score = (
                activity_score * 0.3 +
                completion_score * 0.3 +
                progress_score * 0.4
        )

        return round(productivity_score)

    def _calculate_focus_score(self, papers: List[Paper]) -> int:
        """Calculate focus score based on consistent work patterns"""

        if not papers:
            return 0

        # Simple heuristic: more papers = more distributed focus
        if len(papers) == 1:
            return 100
        elif len(papers) <= 3:
            return 75
        elif len(papers) <= 5:
            return 50
        else:
            return 25


# Create global analytics service instance
analytics_service = AnalyticsService()