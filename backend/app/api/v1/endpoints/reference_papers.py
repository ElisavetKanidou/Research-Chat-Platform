"""
API endpoints for Reference Papers management
Upload and manage papers used for AI personalization
"""
import logging
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from datetime import datetime
import uuid

from app.core.config import settings
from app.database.session import get_db
from app.models.user import User
from app.models.reference_paper import ReferencePaper, PaperType
from app.schemas.reference_paper import (
    ReferencePaperCreate,
    ReferencePaperResponse,
    ReferencePaperListResponse,
    ReferencePaperUploadResponse,
    ReferencePaperUpdate
)
from app.api.v1.endpoints.auth import get_current_user
from app.services.pdf_analyzer import pdf_analyzer

router = APIRouter()
logger = logging.getLogger(__name__)

# File upload settings
UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "reference_papers"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/upload", response_model=ReferencePaperUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_reference_paper(
    file: UploadFile = File(...),
    title: str = Form(...),
    paper_type: str = Form(...),
    authors: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    journal: Optional[str] = Form(None),
    doi: Optional[str] = Form(None),
    research_area: Optional[str] = Form(None),
    abstract: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a reference paper (PDF) for AI personalization

    The paper will be analyzed to extract writing style features that
    influence AI responses based on personalization settings.
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Only PDF files are allowed."
            )

        # Validate paper type
        if paper_type not in ['lab', 'personal', 'literature']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="paper_type must be 'lab', 'personal', or 'literature'"
            )

        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Check file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024}MB"
            )

        # Generate unique filename
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}{file_ext}"
        file_path = UPLOAD_DIR / safe_filename

        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)

        logger.info(f"📄 Saved reference paper: {file_path}")

        # Extract text from PDF
        extracted_text = pdf_analyzer.extract_text_from_pdf(str(file_path))

        # Analyze writing style
        writing_features = {}
        is_analyzed = False
        if extracted_text:
            writing_features = pdf_analyzer.analyze_writing_style(extracted_text)
            is_analyzed = True
            logger.info(f"✅ Analyzed paper writing style")

        # Create database record
        reference_paper = ReferencePaper(
            id=uuid.uuid4(),
            user_id=current_user.id,
            title=title,
            authors=authors,
            year=year,
            journal=journal,
            doi=doi,
            paper_type=PaperType(paper_type),
            research_area=research_area,
            file_url=str(file_path),
            file_size=file_size,
            original_filename=file.filename,
            content_text=extracted_text,
            abstract=abstract,
            is_analyzed=is_analyzed,
            writing_style_features=writing_features,
            paper_metadata={
                "uploaded_at": datetime.utcnow().isoformat(),
                "file_ext": file_ext,
            }
        )

        if is_analyzed:
            reference_paper.analysis_date = datetime.utcnow().isoformat()

        db.add(reference_paper)
        await db.commit()
        await db.refresh(reference_paper)

        logger.info(f"✅ Created reference paper record: {reference_paper.id}")

        return ReferencePaperUploadResponse(
            id=reference_paper.id,
            title=reference_paper.title,
            paper_type=reference_paper.paper_type.value,
            file_url=reference_paper.file_url,
            original_filename=reference_paper.original_filename,
            is_analyzed=reference_paper.is_analyzed,
            message=f"Paper uploaded successfully and {'analyzed' if is_analyzed else 'saved'}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to upload reference paper: {str(e)}")
        # Clean up file if it was saved
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload paper: {str(e)}"
        )


@router.get("/", response_model=ReferencePaperListResponse)
async def get_reference_papers(
    paper_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all reference papers for the current user

    Optionally filter by paper type (lab, personal, literature)
    """
    try:
        # Build query
        query = select(ReferencePaper).where(ReferencePaper.user_id == current_user.id)

        if paper_type:
            if paper_type not in ['lab', 'personal', 'literature']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="paper_type must be 'lab', 'personal', or 'literature'"
                )
            query = query.where(ReferencePaper.paper_type == PaperType(paper_type))

        query = query.order_by(ReferencePaper.created_at.desc())

        result = await db.execute(query)
        papers = result.scalars().all()

        # Count by type
        lab_count_query = select(func.count()).select_from(ReferencePaper).where(
            ReferencePaper.user_id == current_user.id,
            ReferencePaper.paper_type == PaperType.LAB
        )
        personal_count_query = select(func.count()).select_from(ReferencePaper).where(
            ReferencePaper.user_id == current_user.id,
            ReferencePaper.paper_type == PaperType.PERSONAL
        )
        literature_count_query = select(func.count()).select_from(ReferencePaper).where(
            ReferencePaper.user_id == current_user.id,
            ReferencePaper.paper_type == PaperType.LITERATURE
        )

        lab_count = await db.scalar(lab_count_query)
        personal_count = await db.scalar(personal_count_query)
        literature_count = await db.scalar(literature_count_query)

        return ReferencePaperListResponse(
            papers=[ReferencePaperResponse.model_validate(p) for p in papers],
            total=len(papers),
            lab_papers_count=lab_count or 0,
            personal_papers_count=personal_count or 0,
            literature_papers_count=literature_count or 0
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get reference papers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve papers: {str(e)}"
        )


@router.get("/{paper_id}", response_model=ReferencePaperResponse)
async def get_reference_paper(
    paper_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific reference paper by ID"""
    query = select(ReferencePaper).where(
        ReferencePaper.id == paper_id,
        ReferencePaper.user_id == current_user.id
    )
    result = await db.execute(query)
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference paper not found"
        )

    return ReferencePaperResponse.model_validate(paper)


@router.patch("/{paper_id}", response_model=ReferencePaperResponse)
async def update_reference_paper(
    paper_id: uuid.UUID,
    paper_update: ReferencePaperUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update reference paper metadata"""
    query = select(ReferencePaper).where(
        ReferencePaper.id == paper_id,
        ReferencePaper.user_id == current_user.id
    )
    result = await db.execute(query)
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference paper not found"
        )

    # Update fields
    update_data = paper_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(paper, field, value)

    paper.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(paper)

    return ReferencePaperResponse.model_validate(paper)


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reference_paper(
    paper_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a reference paper"""
    query = select(ReferencePaper).where(
        ReferencePaper.id == paper_id,
        ReferencePaper.user_id == current_user.id
    )
    result = await db.execute(query)
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference paper not found"
        )

    # Delete file
    file_path = Path(paper.file_url)
    if file_path.exists():
        file_path.unlink()
        logger.info(f"🗑️ Deleted file: {file_path}")

    # Delete database record
    await db.delete(paper)
    await db.commit()

    logger.info(f"✅ Deleted reference paper: {paper_id}")

    return None


@router.post("/{paper_id}/reanalyze", response_model=ReferencePaperResponse)
async def reanalyze_reference_paper(
    paper_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Re-analyze a reference paper's writing style"""
    query = select(ReferencePaper).where(
        ReferencePaper.id == paper_id,
        ReferencePaper.user_id == current_user.id
    )
    result = await db.execute(query)
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference paper not found"
        )

    # Re-extract text if needed
    if not paper.content_text:
        extracted_text = pdf_analyzer.extract_text_from_pdf(paper.file_url)
        paper.content_text = extracted_text

    # Re-analyze writing style
    if paper.content_text:
        writing_features = pdf_analyzer.analyze_writing_style(paper.content_text)
        paper.mark_as_analyzed(writing_features)
        await db.commit()
        await db.refresh(paper)
        logger.info(f"✅ Re-analyzed paper: {paper_id}")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from PDF"
        )

    return ReferencePaperResponse.model_validate(paper)
