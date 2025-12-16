"""
Google Drive integration service
backend/app/services/google_drive_service.py
"""
import os
from typing import Optional, List, Dict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
import io


class GoogleDriveService:
    """Service for Google Drive integration"""

    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/drive.file']

    def get_drive_service(self, access_token: str, refresh_token: Optional[str] = None):
        """Create Google Drive service with credentials"""
        credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            scopes=self.scopes
        )

        # Refresh token if expired
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        return build('drive', 'v3', credentials=credentials)

    async def upload_paper(
        self,
        access_token: str,
        paper_title: str,
        file_path: str,
        folder_id: Optional[str] = None
    ) -> Dict:
        """Upload a paper to Google Drive"""
        try:
            service = self.get_drive_service(access_token)

            # File metadata
            file_metadata = {
                'name': f"{paper_title}.docx",
                'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }

            # If folder_id provided, set parent folder
            if folder_id:
                file_metadata['parents'] = [folder_id]

            # Upload file
            media = MediaFileUpload(
                file_path,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                resumable=True
            )

            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()

            return {
                'file_id': file.get('id'),
                'name': file.get('name'),
                'web_link': file.get('webViewLink'),
                'success': True
            }

        except Exception as e:
            print(f"❌ Failed to upload to Google Drive: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def download_paper(
        self,
        access_token: str,
        file_id: str,
        output_path: str
    ) -> Dict:
        """Download a paper from Google Drive"""
        try:
            service = self.get_drive_service(access_token)

            # Get file
            request = service.files().get_media(fileId=file_id)

            # Download to file
            fh = io.FileIO(output_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            return {
                'success': True,
                'file_path': output_path
            }

        except Exception as e:
            print(f"❌ Failed to download from Google Drive: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def list_papers(
        self,
        access_token: str,
        folder_id: Optional[str] = None
    ) -> List[Dict]:
        """List all papers in Google Drive"""
        try:
            service = self.get_drive_service(access_token)

            # Build query
            query = "mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'"
            if folder_id:
                query += f" and '{folder_id}' in parents"

            # List files
            results = service.files().list(
                q=query,
                pageSize=100,
                fields="files(id, name, modifiedTime, webViewLink)"
            ).execute()

            files = results.get('files', [])

            return [
                {
                    'file_id': f.get('id'),
                    'name': f.get('name'),
                    'modified': f.get('modifiedTime'),
                    'web_link': f.get('webViewLink')
                }
                for f in files
            ]

        except Exception as e:
            print(f"❌ Failed to list Google Drive files: {str(e)}")
            return []

    async def delete_paper(
        self,
        access_token: str,
        file_id: str
    ) -> Dict:
        """Delete a paper from Google Drive"""
        try:
            service = self.get_drive_service(access_token)

            service.files().delete(fileId=file_id).execute()

            return {
                'success': True,
                'file_id': file_id
            }

        except Exception as e:
            print(f"❌ Failed to delete from Google Drive: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def create_research_folder(
        self,
        access_token: str,
        folder_name: str = "Research Papers"
    ) -> Dict:
        """Create a dedicated folder for research papers"""
        try:
            service = self.get_drive_service(access_token)

            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            folder = service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()

            return {
                'folder_id': folder.get('id'),
                'name': folder.get('name'),
                'web_link': folder.get('webViewLink'),
                'success': True
            }

        except Exception as e:
            print(f"❌ Failed to create folder in Google Drive: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


google_drive_service = GoogleDriveService()
