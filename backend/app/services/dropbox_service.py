"""
Dropbox integration service
backend/app/services/dropbox_service.py
"""
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError
from typing import Optional, List, Dict
import os


class DropboxService:
    """Service for Dropbox integration"""

    def __init__(self):
        self.research_folder = "/Research Papers"

    def get_client(self, access_token: str) -> dropbox.Dropbox:
        """Create Dropbox client with access token"""
        return dropbox.Dropbox(access_token)

    async def upload_paper(
        self,
        access_token: str,
        paper_title: str,
        file_path: str,
        folder_path: Optional[str] = None
    ) -> Dict:
        """Upload a paper to Dropbox"""
        try:
            dbx = self.get_client(access_token)

            # Determine upload path
            if folder_path:
                dropbox_path = f"{folder_path}/{paper_title}.docx"
            else:
                dropbox_path = f"{self.research_folder}/{paper_title}.docx"

            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Upload to Dropbox
            result = dbx.files_upload(
                file_data,
                dropbox_path,
                mode=WriteMode('overwrite'),
                autorename=True
            )

            # Get shareable link
            try:
                shared_link = dbx.sharing_create_shared_link_with_settings(dropbox_path)
                web_link = shared_link.url
            except ApiError:
                # Link might already exist
                links = dbx.sharing_list_shared_links(path=dropbox_path)
                web_link = links.links[0].url if links.links else None

            return {
                'file_id': result.id,
                'name': result.name,
                'path': result.path_display,
                'web_link': web_link,
                'success': True
            }

        except Exception as e:
            print(f"❌ Failed to upload to Dropbox: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def download_paper(
        self,
        access_token: str,
        dropbox_path: str,
        output_path: str
    ) -> Dict:
        """Download a paper from Dropbox"""
        try:
            dbx = self.get_client(access_token)

            # Download file
            metadata, response = dbx.files_download(dropbox_path)

            # Save to local file
            with open(output_path, 'wb') as f:
                f.write(response.content)

            return {
                'success': True,
                'file_path': output_path,
                'name': metadata.name
            }

        except Exception as e:
            print(f"❌ Failed to download from Dropbox: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def list_papers(
        self,
        access_token: str,
        folder_path: Optional[str] = None
    ) -> List[Dict]:
        """List all papers in Dropbox folder"""
        try:
            dbx = self.get_client(access_token)

            # List folder
            path = folder_path or self.research_folder
            result = dbx.files_list_folder(path)

            papers = []
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    # Get shareable link
                    try:
                        links = dbx.sharing_list_shared_links(path=entry.path_display)
                        web_link = links.links[0].url if links.links else None
                    except:
                        web_link = None

                    papers.append({
                        'file_id': entry.id,
                        'name': entry.name,
                        'path': entry.path_display,
                        'modified': entry.client_modified.isoformat(),
                        'size': entry.size,
                        'web_link': web_link
                    })

            return papers

        except Exception as e:
            print(f"❌ Failed to list Dropbox files: {str(e)}")
            return []

    async def delete_paper(
        self,
        access_token: str,
        dropbox_path: str
    ) -> Dict:
        """Delete a paper from Dropbox"""
        try:
            dbx = self.get_client(access_token)

            dbx.files_delete_v2(dropbox_path)

            return {
                'success': True,
                'path': dropbox_path
            }

        except Exception as e:
            print(f"❌ Failed to delete from Dropbox: {str(e)}")
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
            dbx = self.get_client(access_token)

            folder_path = f"/{folder_name}"

            # Create folder
            result = dbx.files_create_folder_v2(folder_path)

            return {
                'folder_id': result.metadata.id,
                'name': result.metadata.name,
                'path': result.metadata.path_display,
                'success': True
            }

        except ApiError as e:
            if 'conflict' in str(e):
                # Folder already exists
                return {
                    'success': True,
                    'path': folder_path,
                    'message': 'Folder already exists'
                }
            else:
                print(f"❌ Failed to create folder in Dropbox: {str(e)}")
                return {
                    'success': False,
                    'error': str(e)
                }

    async def sync_paper(
        self,
        access_token: str,
        paper_title: str,
        local_file_path: str
    ) -> Dict:
        """Sync a paper to Dropbox (upload or update)"""
        try:
            dbx = self.get_client(access_token)

            dropbox_path = f"{self.research_folder}/{paper_title}.docx"

            # Check if file exists
            try:
                metadata = dbx.files_get_metadata(dropbox_path)
                # File exists, upload new version
                action = "updated"
            except ApiError:
                # File doesn't exist
                action = "uploaded"

            # Upload file
            result = await self.upload_paper(
                access_token,
                paper_title,
                local_file_path
            )

            if result['success']:
                result['action'] = action

            return result

        except Exception as e:
            print(f"❌ Failed to sync to Dropbox: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


dropbox_service = DropboxService()
