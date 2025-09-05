
"""
Export Endpoints (app/api/v1/endpoints/export.py)
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.api.v1.endpoints.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.paper import PaperExportRequest, ExportFormat
from app.services.export_service import export_service
from app.core.exceptions import NotFoundException, ValidationException

router = APIRouter()


@router.post("/papers/{paper_id}")
async def export_paper(
        paper_id: str,
        export_request: PaperExportRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Export paper in specified format"""

    try:
        export_data = await export_service.export_paper(
            db=db,
            paper_id=paper_id,
            user_id=current_user.id,
            format=export_request.format,
            include_sections=export_request.include_sections,
            include_comments=export_request.include_comments
        )

        # Return file as download
        content = export_data["content"].encode() if isinstance(export_data["content"], str) else export_data["content"]

        return StreamingResponse(
            io.BytesIO(content),
            media_type=export_data["content_type"],
            headers={"Content-Disposition": f"attachment; filename={export_data['filename']}"}
        )

    except (NotFoundException, ValidationException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/papers/{paper_id}/formats")
async def get_export_formats(
        paper_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get available export formats for paper"""

    from app.models.paper import Paper

    paper = await db.get(Paper, paper_id)
    if not paper or not paper.is_viewable_by(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    formats = [
        {
            "format": "json",
            "name": "JSON",
            "description": "Structured data format",
            "supports_comments": True
        },
        {
            "format": "markdown",
            "name": "Markdown",
            "description": "Plain text format with formatting",
            "supports_comments": False
        },
        {
            "format": "latex",
            "name": "LaTeX",
            "description": "Academic document format",
            "supports_comments": False
        },
        {
            "format": "pdf",
            "name": "PDF",
            "description": "Portable document format",
            "supports_comments": False,
            "available": False,
            "note": "Coming soon"
        }
    ]

    return {"formats": formats}


@router.post("/user-data")
async def export_user_data(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        include_papers: bool = Query(True),
        include_analytics: bool = Query(False)
):
    """Export all user data"""

    try:
        export_data = await export_service.export_user_data(
            db=db,
            user_id=current_user.id,
            include_papers=include_papers,
            include_analytics=include_analytics
        )

        content = export_data["content"].encode()

        return StreamingResponse(
            io.BytesIO(content),
            media_type=export_data["content_type"],
            headers={"Content-Disposition": f"attachment; filename={export_data['filename']}"}
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )


@router.get("/templates")
async def get_export_templates():
    """Get available export templates"""

    templates = [
        {
            "id": "academic_paper",
            "name": "Academic Paper",
            "description": "Standard academic paper format",
            "sections": ["Abstract", "Introduction", "Methods", "Results", "Discussion", "Conclusion"],
            "formats": ["latex", "pdf"]
        },
        {
            "id": "conference_paper",
            "name": "Conference Paper",
            "description": "Short conference paper format",
            "sections": ["Abstract", "Introduction", "Approach", "Evaluation", "Conclusion"],
            "formats": ["latex", "pdf"]
        },
        {
            "id": "thesis_chapter",
            "name": "Thesis Chapter",
            "description": "Individual thesis chapter",
            "sections": ["Introduction", "Literature Review", "Methodology", "Results", "Discussion"],
            "formats": ["latex", "markdown"]
        }
    ]

    return {"templates": templates}