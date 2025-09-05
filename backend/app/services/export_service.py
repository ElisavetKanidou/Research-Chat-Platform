"""
Export Service (app/services/export_service.py)
"""
from typing import List, Optional, Dict, Any, BinaryIO
from sqlalchemy.ext.asyncio import AsyncSession
import json
import csv
import io
from datetime import datetime
import tempfile
import zipfile

from app.models.paper import Paper, PaperSection
from app.schemas.paper import ExportFormat
from app.core.exceptions import NotFoundException, ValidationException


class ExportService:
    """Service for exporting papers and data"""

    async def export_paper(
            self,
            db: AsyncSession,
            paper_id: str,
            user_id: str,
            format: ExportFormat,
            include_sections: List[str] = None,
            include_comments: bool = False
    ) -> Dict[str, Any]:
        """Export paper in specified format"""

        paper = await db.get(Paper, paper_id)
        if not paper or not paper.is_viewable_by(user_id):
            raise NotFoundException("Paper")

        # Filter sections if specified
        sections = paper.sections
        if include_sections:
            sections = [s for s in sections if str(s.id) in include_sections]

        if format == ExportFormat.JSON:
            return await self._export_to_json(paper, sections, include_comments)
        elif format == ExportFormat.MARKDOWN:
            return await self._export_to_markdown(paper, sections)
        elif format == ExportFormat.LATEX:
            return await self._export_to_latex(paper, sections)
        elif format == ExportFormat.PDF:
            return await self._export_to_pdf(paper, sections)
        else:
            raise ValidationException(f"Unsupported export format: {format}")

    async def _export_to_json(
            self,
            paper: Paper,
            sections: List[PaperSection],
            include_comments: bool
    ) -> Dict[str, Any]:
        """Export paper to JSON format"""

        export_data = {
            "title": paper.title,
            "abstract": paper.abstract,
            "status": paper.status.value,
            "research_area": paper.research_area,
            "tags": paper.tags,
            "co_authors": paper.co_authors,
            "created_at": paper.created_at.isoformat(),
            "updated_at": paper.updated_at.isoformat(),
            "word_count": paper.current_word_count,
            "target_word_count": paper.target_word_count,
            "progress": paper.progress,
            "sections": [
                {
                    "title": section.title,
                    "content": section.content,
                    "status": section.status.value,
                    "order": section.order,
                    "word_count": section.word_count
                }
                for section in sorted(sections, key=lambda x: x.order)
            ],
            "export_metadata": {
                "format": "json",
                "exported_at": datetime.utcnow().isoformat(),
                "version": "1.0"
            }
        }

        if include_comments:
            export_data["comments"] = [
                {
                    "content": comment.content,
                    "author": comment.author.name,
                    "created_at": comment.created_at.isoformat(),
                    "section_title": comment.section.title if comment.section else None,
                    "is_resolved": comment.is_resolved
                }
                for comment in paper.comments
            ]

        return {
            "content": json.dumps(export_data, indent=2),
            "filename": f"{paper.title.replace(' ', '_')}.json",
            "content_type": "application/json"
        }

    async def _export_to_markdown(
            self,
            paper: Paper,
            sections: List[PaperSection]
    ) -> Dict[str, Any]:
        """Export paper to Markdown format"""

        content = f"# {paper.title}\n\n"

        if paper.abstract:
            content += "## Abstract\n\n"
            content += f"{paper.abstract}\n\n"

        if paper.co_authors:
            content += "## Authors\n\n"
            content += ", ".join(paper.co_authors) + "\n\n"

        # Add sections
        for section in sorted(sections, key=lambda x: x.order):
            content += f"## {section.title}\n\n"
            if section.content:
                content += f"{section.content}\n\n"

        # Add metadata
        content += "---\n\n"
        content += f"**Research Area:** {paper.research_area}\n\n"
        content += f"**Status:** {paper.status.value}\n\n"
        content += f"**Progress:** {paper.progress}%\n\n"
        content += f"**Word Count:** {paper.current_word_count} / {paper.target_word_count}\n\n"

        if paper.tags:
            content += f"**Tags:** {', '.join(paper.tags)}\n\n"

        return {
            "content": content,
            "filename": f"{paper.title.replace(' ', '_')}.md",
            "content_type": "text/markdown"
        }

    async def _export_to_latex(
            self,
            paper: Paper,
            sections: List[PaperSection]
    ) -> Dict[str, Any]:
        """Export paper to LaTeX format"""

        content = "\\documentclass{article}\n"
        content += "\\usepackage[utf8]{inputenc}\n"
        content += "\\usepackage{amsmath}\n"
        content += "\\usepackage{graphicx}\n\n"

        content += f"\\title{{{paper.title}}}\n"
        if paper.co_authors:
            content += f"\\author{{{', '.join(paper.co_authors)}}}\n"
        content += "\\date{\\today}\n\n"

        content += "\\begin{document}\n\n"
        content += "\\maketitle\n\n"

        if paper.abstract:
            content += "\\begin{abstract}\n"
            content += f"{paper.abstract}\n"
            content += "\\end{abstract}\n\n"

        # Add sections
        for section in sorted(sections, key=lambda x: x.order):
            content += f"\\section{{{section.title}}}\n\n"
            if section.content:
                content += f"{section.content}\n\n"

        content += "\\end{document}\n"

        return {
            "content": content,
            "filename": f"{paper.title.replace(' ', '_')}.tex",
            "content_type": "application/x-latex"
        }

    async def _export_to_pdf(
            self,
            paper: Paper,
            sections: List[PaperSection]
    ) -> Dict[str, Any]:
        """Export paper to PDF format"""

        # This would require a PDF generation library like weasyprint or reportlab
        # For now, return a placeholder
        raise ValidationException("PDF export not yet implemented")

    async def export_user_data(
            self,
            db: AsyncSession,
            user_id: str,
            include_papers: bool = True,
            include_analytics: bool = False
    ) -> Dict[str, Any]:
        """Export all user data"""

        from sqlalchemy import select
        from app.models.user import User

        user = await db.get(User, user_id)
        if not user:
            raise NotFoundException("User")

        export_data = {
            "user_profile": {
                "name": user.name,
                "email": user.email,
                "affiliation": user.affiliation,
                "research_interests": user.research_interests,
                "created_at": user.created_at.isoformat()
            },
            "export_metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "format": "json",
                "version": "1.0"
            }
        }

        if include_papers:
            papers_query = select(Paper).where(Paper.owner_id == user_id)
            papers_result = await db.execute(papers_query)
            papers = papers_result.scalars().all()

            export_data["papers"] = []
            for paper in papers:
                paper_data = await self._export_to_json(paper, paper.sections, False)
                export_data["papers"].append(json.loads(paper_data["content"]))

        return {
            "content": json.dumps(export_data, indent=2),
            "filename": f"user_data_{user_id}.json",
            "content_type": "application/json"
        }


# Create service instance
export_service = ExportService()
