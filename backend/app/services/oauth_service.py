"""
OAuth service for handling third-party integrations
backend/app/services/oauth_service.py
"""
import os
import httpx
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.oauth_token import OAuthToken
from app.core.config import settings

logger = logging.getLogger(__name__)


class OAuthService:
    """Service for managing OAuth tokens and exchanges"""

    async def exchange_google_code(
        self,
        code: str,
        db: AsyncSession,
        user_id: str
    ) -> Dict:
        """
        Exchange Google OAuth authorization code for access token

        Args:
            code: Authorization code from Google
            db: Database session
            user_id: User ID

        Returns:
            Dict with token information
        """
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        redirect_uri = f"{settings.FRONTEND_URL}/settings/integrations/google-drive/callback"

        if not client_id or not client_secret:
            raise ValueError("Google OAuth credentials not configured")

        token_url = "https://oauth2.googleapis.com/token"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url,
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                }
            )

            if response.status_code != 200:
                logger.error(f"Google token exchange failed: {response.text}")
                raise ValueError(f"Failed to exchange code: {response.text}")

            token_data = response.json()

        # Store token in database
        await self.store_token(
            db=db,
            user_id=user_id,
            service="google_drive",
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_in=token_data.get("expires_in", 3600)
        )

        logger.info(f"✅ Google Drive OAuth token stored for user {user_id}")
        return token_data

    async def exchange_dropbox_code(
        self,
        code: str,
        db: AsyncSession,
        user_id: str
    ) -> Dict:
        """
        Exchange Dropbox OAuth authorization code for access token

        Args:
            code: Authorization code from Dropbox
            db: Database session
            user_id: User ID

        Returns:
            Dict with token information
        """
        app_key = os.getenv("DROPBOX_APP_KEY")
        app_secret = os.getenv("DROPBOX_APP_SECRET")
        redirect_uri = f"{settings.FRONTEND_URL}/settings/integrations/dropbox/callback"

        if not app_key or not app_secret:
            raise ValueError("Dropbox OAuth credentials not configured")

        token_url = "https://api.dropbox.com/oauth2/token"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url,
                data={
                    "code": code,
                    "client_id": app_key,
                    "client_secret": app_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                },
                auth=(app_key, app_secret)
            )

            if response.status_code != 200:
                logger.error(f"Dropbox token exchange failed: {response.text}")
                raise ValueError(f"Failed to exchange code: {response.text}")

            token_data = response.json()

        # Store token in database
        await self.store_token(
            db=db,
            user_id=user_id,
            service="dropbox",
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_in=token_data.get("expires_in", 14400)  # Dropbox default: 4 hours
        )

        logger.info(f"✅ Dropbox OAuth token stored for user {user_id}")
        return token_data

    async def exchange_mendeley_code(
        self,
        code: str,
        db: AsyncSession,
        user_id: str
    ) -> Dict:
        """
        Exchange Mendeley OAuth authorization code for access token

        Args:
            code: Authorization code from Mendeley
            db: Database session
            user_id: User ID

        Returns:
            Dict with token information
        """
        client_id = os.getenv("MENDELEY_CLIENT_ID")
        client_secret = os.getenv("MENDELEY_CLIENT_SECRET")
        redirect_uri = f"{settings.FRONTEND_URL}/settings/integrations/mendeley/callback"

        if not client_id or not client_secret:
            raise ValueError("Mendeley OAuth credentials not configured")

        token_url = "https://api.mendeley.com/oauth/token"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url,
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                }
            )

            if response.status_code != 200:
                logger.error(f"Mendeley token exchange failed: {response.text}")
                raise ValueError(f"Failed to exchange code: {response.text}")

            token_data = response.json()

        # Store token in database
        await self.store_token(
            db=db,
            user_id=user_id,
            service="mendeley",
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_in=token_data.get("expires_in", 3600)
        )

        logger.info(f"✅ Mendeley OAuth token stored for user {user_id}")
        return token_data

    async def store_zotero_key(
        self,
        db: AsyncSession,
        user_id: str,
        api_key: str,
        zotero_user_id: Optional[str] = None
    ) -> None:
        """
        Store Zotero API key (Zotero uses API keys, not OAuth)

        Args:
            db: Database session
            user_id: User ID
            api_key: Zotero API key
            zotero_user_id: Optional Zotero user ID
        """
        # Store as a "token" for consistency
        await self.store_token(
            db=db,
            user_id=user_id,
            service="zotero",
            access_token=api_key,
            refresh_token=None,
            expires_in=None,  # API keys don't expire
            token_metadata=f'{{"zotero_user_id": "{zotero_user_id}"}}' if zotero_user_id else None
        )

        logger.info(f"✅ Zotero API key stored for user {user_id}")

    async def store_token(
        self,
        db: AsyncSession,
        user_id: str,
        service: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: Optional[int] = None,
        token_metadata: Optional[str] = None
    ) -> OAuthToken:
        """
        Store or update OAuth token in database

        Args:
            db: Database session
            user_id: User ID
            service: Service name (google_drive, dropbox, etc.)
            access_token: Access token
            refresh_token: Optional refresh token
            expires_in: Token expiration in seconds
            token_metadata: Optional metadata JSON string

        Returns:
            OAuthToken instance
        """
        from uuid import UUID

        # Check if token already exists
        query = select(OAuthToken).where(
            OAuthToken.user_id == UUID(user_id),
            OAuthToken.service == service
        )
        result = await db.execute(query)
        existing_token = result.scalar_one_or_none()

        # Calculate expiration time
        expires_at = None
        if expires_in:
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        if existing_token:
            # Update existing token
            existing_token.access_token = access_token
            if refresh_token:
                existing_token.refresh_token = refresh_token
            existing_token.expires_at = expires_at
            if token_metadata:
                existing_token.token_metadata = token_metadata
            existing_token.updated_at = datetime.utcnow()

            token = existing_token
        else:
            # Create new token
            token = OAuthToken(
                user_id=UUID(user_id),
                service=service,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                token_metadata=token_metadata
            )
            db.add(token)

        await db.commit()
        await db.refresh(token)

        return token

    async def get_token(
        self,
        db: AsyncSession,
        user_id: str,
        service: str
    ) -> Optional[OAuthToken]:
        """
        Get OAuth token for a service

        Args:
            db: Database session
            user_id: User ID
            service: Service name

        Returns:
            OAuthToken if found, None otherwise
        """
        from uuid import UUID

        query = select(OAuthToken).where(
            OAuthToken.user_id == UUID(user_id),
            OAuthToken.service == service
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def revoke_token(
        self,
        db: AsyncSession,
        user_id: str,
        service: str
    ) -> bool:
        """
        Revoke and delete OAuth token

        Args:
            db: Database session
            user_id: User ID
            service: Service name

        Returns:
            True if token was deleted, False if not found
        """
        token = await self.get_token(db, user_id, service)
        if not token:
            return False

        # TODO: Call provider's revoke endpoint if available

        await db.delete(token)
        await db.commit()

        logger.info(f"🗑️ OAuth token revoked for user {user_id}, service {service}")
        return True

    async def refresh_token_if_needed(
        self,
        db: AsyncSession,
        user_id: str,
        service: str
    ) -> Optional[OAuthToken]:
        """
        Refresh token if it's expired

        Args:
            db: Database session
            user_id: User ID
            service: Service name

        Returns:
            Updated OAuthToken or None if refresh failed
        """
        token = await self.get_token(db, user_id, service)
        if not token:
            return None

        # Check if token is expired
        if not token.is_expired():
            return token

        if not token.refresh_token:
            logger.warning(f"⚠️ Token expired and no refresh token available for {service}")
            return None

        # Refresh based on service
        try:
            if service == "google_drive":
                await self._refresh_google_token(db, token)
            elif service == "dropbox":
                await self._refresh_dropbox_token(db, token)
            elif service == "mendeley":
                await self._refresh_mendeley_token(db, token)

            await db.refresh(token)
            return token

        except Exception as e:
            logger.error(f"❌ Failed to refresh {service} token: {e}")
            return None

    async def _refresh_google_token(self, db: AsyncSession, token: OAuthToken) -> None:
        """Refresh Google OAuth token"""
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": token.refresh_token,
                    "grant_type": "refresh_token"
                }
            )

            if response.status_code == 200:
                data = response.json()
                token.access_token = data["access_token"]
                token.expires_at = datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600))
                token.updated_at = datetime.utcnow()
                await db.commit()
                logger.info("✅ Google token refreshed")
            else:
                raise ValueError(f"Failed to refresh token: {response.text}")

    async def _refresh_dropbox_token(self, db: AsyncSession, token: OAuthToken) -> None:
        """Refresh Dropbox OAuth token"""
        app_key = os.getenv("DROPBOX_APP_KEY")
        app_secret = os.getenv("DROPBOX_APP_SECRET")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.dropbox.com/oauth2/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": token.refresh_token
                },
                auth=(app_key, app_secret)
            )

            if response.status_code == 200:
                data = response.json()
                token.access_token = data["access_token"]
                token.expires_at = datetime.utcnow() + timedelta(seconds=data.get("expires_in", 14400))
                token.updated_at = datetime.utcnow()
                await db.commit()
                logger.info("✅ Dropbox token refreshed")
            else:
                raise ValueError(f"Failed to refresh token: {response.text}")

    async def _refresh_mendeley_token(self, db: AsyncSession, token: OAuthToken) -> None:
        """Refresh Mendeley OAuth token"""
        client_id = os.getenv("MENDELEY_CLIENT_ID")
        client_secret = os.getenv("MENDELEY_CLIENT_SECRET")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.mendeley.com/oauth/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": token.refresh_token,
                    "grant_type": "refresh_token"
                }
            )

            if response.status_code == 200:
                data = response.json()
                token.access_token = data["access_token"]
                token.expires_at = datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600))
                token.updated_at = datetime.utcnow()
                await db.commit()
                logger.info("✅ Mendeley token refreshed")
            else:
                raise ValueError(f"Failed to refresh token: {response.text}")


# Global instance
oauth_service = OAuthService()
