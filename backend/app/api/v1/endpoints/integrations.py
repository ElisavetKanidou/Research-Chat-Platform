"""
External integrations API endpoints (Google Drive, Dropbox, Zotero, Mendeley)
backend/app/api/v1/endpoints/integrations.py
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Request, File, UploadFile
from fastapi.responses import RedirectResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import os
import secrets
import tempfile

from app.api.v1.endpoints.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.paper import Paper
from app.core.config import settings
from app.services.google_drive_service import google_drive_service
from app.services.dropbox_service import dropbox_service
from app.services.zotero_service import zotero_service
from app.services.latex_export_service import latex_export_service

router = APIRouter()


# ==================== PYDANTIC MODELS ====================

class PaperSyncRequest(BaseModel):
    paper_id: str
    folder_id: Optional[str] = None


class ReferenceImportRequest(BaseModel):
    collection_id: Optional[str] = None


class LaTeXExportRequest(BaseModel):
    paper_id: str
    document_class: str = "article"
    include_bibliography: bool = True


# ==================== GOOGLE DRIVE OAUTH ====================

@router.get("/google-drive/authorize")
async def google_drive_authorize(
    current_user: User = Depends(get_current_user),
):
    """Initiate Google Drive OAuth2 flow"""
    try:
        # Google OAuth2 configuration
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        redirect_uri = f"{settings.FRONTEND_URL}/settings/integrations/google-drive/callback"

        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google Drive integration not configured"
            )

        # Generate state token for security
        state = secrets.token_urlsafe(32)

        # TODO: Store state token in session/redis for verification

        # Build Google OAuth URL
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope=https://www.googleapis.com/auth/drive.file&"
            f"state={state}&"
            f"access_type=offline&"
            f"prompt=consent"
        )

        return {"auth_url": auth_url}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate Google Drive OAuth: {str(e)}"
        )


@router.post("/google-drive/callback")
async def google_drive_callback(
    code: str,
    state: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Handle Google Drive OAuth2 callback"""
    try:
        from app.services.oauth_service import oauth_service

        # TODO: Verify state token against stored value

        # Exchange authorization code for access token
        await oauth_service.exchange_google_code(
            code=code,
            db=db,
            user_id=str(current_user.id)
        )

        # Update user preferences to mark as connected
        if not current_user.preferences:
            current_user.preferences = {}

        if "integrations" not in current_user.preferences:
            current_user.preferences["integrations"] = {}

        current_user.preferences["integrations"]["googleDrive"] = True

        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(current_user, "preferences")

        await db.commit()

        return {
            "message": "Google Drive connected successfully",
            "integration": "googleDrive",
            "connected": True
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete Google Drive OAuth: {str(e)}"
        )


@router.post("/google-drive/disconnect")
async def google_drive_disconnect(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect Google Drive integration"""
    try:
        from app.services.oauth_service import oauth_service

        # Revoke and delete OAuth token
        await oauth_service.revoke_token(
            db=db,
            user_id=str(current_user.id),
            service="google_drive"
        )

        # Update preferences
        if current_user.preferences and "integrations" in current_user.preferences:
            current_user.preferences["integrations"]["googleDrive"] = False

            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(current_user, "preferences")

            await db.commit()

        return {
            "message": "Google Drive disconnected successfully",
            "integration": "googleDrive",
            "connected": False
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect Google Drive: {str(e)}"
        )


# ==================== DROPBOX OAUTH ====================

@router.get("/dropbox/authorize")
async def dropbox_authorize(
    current_user: User = Depends(get_current_user),
):
    """Initiate Dropbox OAuth2 flow"""
    try:
        app_key = os.getenv("DROPBOX_APP_KEY")
        redirect_uri = f"{settings.FRONTEND_URL}/settings/integrations/dropbox/callback"

        if not app_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Dropbox integration not configured"
            )

        # Generate state token
        state = secrets.token_urlsafe(32)

        # Build Dropbox OAuth URL
        auth_url = (
            f"https://www.dropbox.com/oauth2/authorize?"
            f"client_id={app_key}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"state={state}&"
            f"token_access_type=offline"
        )

        return {"auth_url": auth_url}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate Dropbox OAuth: {str(e)}"
        )


@router.post("/dropbox/callback")
async def dropbox_callback(
    code: str,
    state: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Handle Dropbox OAuth2 callback"""
    try:
        from app.services.oauth_service import oauth_service

        # Exchange authorization code for access token
        await oauth_service.exchange_dropbox_code(
            code=code,
            db=db,
            user_id=str(current_user.id)
        )

        # Mark as connected in preferences
        if not current_user.preferences:
            current_user.preferences = {}

        if "integrations" not in current_user.preferences:
            current_user.preferences["integrations"] = {}

        current_user.preferences["integrations"]["dropbox"] = True

        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(current_user, "preferences")

        await db.commit()

        return {
            "message": "Dropbox connected successfully",
            "integration": "dropbox",
            "connected": True
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete Dropbox OAuth: {str(e)}"
        )


@router.post("/dropbox/disconnect")
async def dropbox_disconnect(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect Dropbox integration"""
    try:
        from app.services.oauth_service import oauth_service

        # Revoke and delete OAuth token
        await oauth_service.revoke_token(
            db=db,
            user_id=str(current_user.id),
            service="dropbox"
        )

        if current_user.preferences and "integrations" in current_user.preferences:
            current_user.preferences["integrations"]["dropbox"] = False

            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(current_user, "preferences")

            await db.commit()

        return {
            "message": "Dropbox disconnected successfully",
            "integration": "dropbox",
            "connected": False
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect Dropbox: {str(e)}"
        )


# ==================== ZOTERO API ====================

@router.post("/zotero/connect")
async def zotero_connect(
    api_key: str,
    user_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Connect Zotero with API key"""
    try:
        from app.services.oauth_service import oauth_service

        # TODO: Verify API key with Zotero API

        # Store API key securely
        await oauth_service.store_zotero_key(
            db=db,
            user_id=str(current_user.id),
            api_key=api_key,
            zotero_user_id=user_id
        )

        # Mark as connected in preferences
        if not current_user.preferences:
            current_user.preferences = {}

        if "integrations" not in current_user.preferences:
            current_user.preferences["integrations"] = {}

        current_user.preferences["integrations"]["zotero"] = True

        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(current_user, "preferences")

        await db.commit()

        return {
            "message": "Zotero connected successfully",
            "integration": "zotero",
            "connected": True
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect Zotero: {str(e)}"
        )


@router.post("/zotero/disconnect")
async def zotero_disconnect(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect Zotero integration"""
    try:
        from app.services.oauth_service import oauth_service

        # Delete Zotero API key
        await oauth_service.revoke_token(
            db=db,
            user_id=str(current_user.id),
            service="zotero"
        )

        if current_user.preferences and "integrations" in current_user.preferences:
            current_user.preferences["integrations"]["zotero"] = False

            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(current_user, "preferences")

            await db.commit()

        return {
            "message": "Zotero disconnected successfully",
            "integration": "zotero",
            "connected": False
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect Zotero: {str(e)}"
        )


# ==================== MENDELEY OAUTH ====================

@router.get("/mendeley/authorize")
async def mendeley_authorize(
    current_user: User = Depends(get_current_user),
):
    """Initiate Mendeley OAuth2 flow"""
    try:
        client_id = os.getenv("MENDELEY_CLIENT_ID")
        redirect_uri = f"{settings.FRONTEND_URL}/settings/integrations/mendeley/callback"

        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Mendeley integration not configured"
            )

        # Generate state token
        state = secrets.token_urlsafe(32)

        # Build Mendeley OAuth URL
        auth_url = (
            f"https://api.mendeley.com/oauth/authorize?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope=all&"
            f"state={state}"
        )

        return {"auth_url": auth_url}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate Mendeley OAuth: {str(e)}"
        )


@router.post("/mendeley/callback")
async def mendeley_callback(
    code: str,
    state: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Handle Mendeley OAuth2 callback"""
    try:
        from app.services.oauth_service import oauth_service

        # Exchange authorization code for access token
        await oauth_service.exchange_mendeley_code(
            code=code,
            db=db,
            user_id=str(current_user.id)
        )

        # Mark as connected in preferences
        if not current_user.preferences:
            current_user.preferences = {}

        if "integrations" not in current_user.preferences:
            current_user.preferences["integrations"] = {}

        current_user.preferences["integrations"]["mendeley"] = True

        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(current_user, "preferences")

        await db.commit()

        return {
            "message": "Mendeley connected successfully",
            "integration": "mendeley",
            "connected": True
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete Mendeley OAuth: {str(e)}"
        )


@router.post("/mendeley/disconnect")
async def mendeley_disconnect(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect Mendeley integration"""
    try:
        from app.services.oauth_service import oauth_service

        # Revoke and delete OAuth token
        await oauth_service.revoke_token(
            db=db,
            user_id=str(current_user.id),
            service="mendeley"
        )

        if current_user.preferences and "integrations" in current_user.preferences:
            current_user.preferences["integrations"]["mendeley"] = False

            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(current_user, "preferences")

            await db.commit()

        return {
            "message": "Mendeley disconnected successfully",
            "integration": "mendeley",
            "connected": False
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect Mendeley: {str(e)}"
        )

# ==================== GOOGLE DRIVE FUNCTIONALITY ====================

@router.post("/google-drive/sync-paper")
async def sync_paper_to_google_drive(
    request: PaperSyncRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync a paper to Google Drive"""
    try:
        # TODO: Get access token from database
        # For now, return error asking for OAuth
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete Google Drive OAuth first"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync to Google Drive: {str(e)}"
        )


# ==================== DROPBOX FUNCTIONALITY ====================

@router.post("/dropbox/backup-paper")
async def backup_paper_to_dropbox(
    request: PaperSyncRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Backup a paper to Dropbox"""
    try:
        # TODO: Get access token from database
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete Dropbox OAuth first"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to backup to Dropbox: {str(e)}"
        )


# ==================== ZOTERO FUNCTIONALITY ====================

@router.post("/zotero/import-references")
async def import_zotero_references(
    request: ReferenceImportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Import references from Zotero"""
    try:
        # TODO: Get Zotero API key and user ID from database
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please connect Zotero first"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import from Zotero: {str(e)}"
        )


# ==================== LATEX EXPORT FUNCTIONALITY ====================

@router.post("/latex/export")
async def export_paper_to_latex(
    request: LaTeXExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export a paper to LaTeX format"""
    try:
        # Get paper from database
        paper_query = select(Paper).where(Paper.id == request.paper_id)
        result = await db.execute(paper_query)
        paper = result.scalar_one_or_none()

        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paper not found"
            )

        # Check if user owns paper or is collaborator
        if paper.owner_id != current_user.id:
            # TODO: Check if user is collaborator
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this paper"
            )

        # Prepare paper data for LaTeX export
        paper_data = {
            'title': paper.title,
            'authors': [current_user.name],  # TODO: Add all authors
            'abstract': paper.abstract or '',
            'sections': [],  # TODO: Get sections from paper
            'references': []  # TODO: Get references
        }

        # Export to LaTeX
        latex_content = latex_export_service.export_paper_to_latex(
            paper_data,
            document_class=request.document_class,
            include_bibliography=request.include_bibliography
        )

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False, encoding='utf-8') as f:
            f.write(latex_content)
            temp_path = f.name

        # Return file
        filename = f"{paper.title.replace(' ', '_')}.tex"
        
        return FileResponse(
            temp_path,
            media_type='application/x-latex',
            filename=filename,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export to LaTeX: {str(e)}"
        )
