"""
Zotero integration service
backend/app/services/zotero_service.py
"""
import aiohttp
from typing import List, Dict, Optional


class ZoteroService:
    """Service for Zotero integration"""

    def __init__(self):
        self.base_url = "https://api.zotero.org"

    async def verify_api_key(self, api_key: str, user_id: Optional[str] = None) -> Dict:
        """Verify Zotero API key"""
        try:
            headers = {
                'Zotero-API-Key': api_key,
                'Zotero-API-Version': '3'
            }

            # Test API key by getting user info
            async with aiohttp.ClientSession() as session:
                if user_id:
                    url = f"{self.base_url}/users/{user_id}/items?limit=1"
                else:
                    # Try to get key info
                    url = f"{self.base_url}/keys/current"

                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'valid': True,
                            'user_id': data.get('userID') if not user_id else user_id
                        }
                    else:
                        return {
                            'valid': False,
                            'error': 'Invalid API key'
                        }

        except Exception as e:
            print(f"❌ Failed to verify Zotero API key: {str(e)}")
            return {
                'valid': False,
                'error': str(e)
            }

    async def get_user_items(
        self,
        api_key: str,
        user_id: str,
        item_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get user's Zotero items (papers, articles, etc.)"""
        try:
            headers = {
                'Zotero-API-Key': api_key,
                'Zotero-API-Version': '3'
            }

            # Build query parameters
            params = {'limit': limit}
            if item_type:
                params['itemType'] = item_type

            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/users/{user_id}/items"

                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        items = await response.json()
                        return [self._format_item(item) for item in items]
                    else:
                        print(f"❌ Zotero API error: {response.status}")
                        return []

        except Exception as e:
            print(f"❌ Failed to get Zotero items: {str(e)}")
            return []

    async def get_collections(
        self,
        api_key: str,
        user_id: str
    ) -> List[Dict]:
        """Get user's Zotero collections"""
        try:
            headers = {
                'Zotero-API-Key': api_key,
                'Zotero-API-Version': '3'
            }

            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/users/{user_id}/collections"

                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        collections = await response.json()
                        return [
                            {
                                'id': c.get('key'),
                                'name': c.get('data', {}).get('name'),
                                'parent': c.get('data', {}).get('parentCollection'),
                                'item_count': c.get('meta', {}).get('numItems', 0)
                            }
                            for c in collections
                        ]
                    else:
                        return []

        except Exception as e:
            print(f"❌ Failed to get Zotero collections: {str(e)}")
            return []

    async def import_references(
        self,
        api_key: str,
        user_id: str,
        collection_id: Optional[str] = None
    ) -> Dict:
        """Import references from Zotero"""
        try:
            # Get items
            items = await self.get_user_items(api_key, user_id)

            # Filter by collection if specified
            if collection_id:
                items = [
                    item for item in items
                    if collection_id in item.get('collections', [])
                ]

            # Convert to our reference format
            references = []
            for item in items:
                ref = {
                    'title': item.get('title'),
                    'authors': item.get('authors'),
                    'year': item.get('year'),
                    'publication': item.get('publication'),
                    'doi': item.get('doi'),
                    'url': item.get('url'),
                    'abstract': item.get('abstract'),
                    'type': item.get('item_type'),
                    'zotero_id': item.get('id')
                }
                references.append(ref)

            return {
                'success': True,
                'count': len(references),
                'references': references
            }

        except Exception as e:
            print(f"❌ Failed to import Zotero references: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def export_to_zotero(
        self,
        api_key: str,
        user_id: str,
        references: List[Dict],
        collection_id: Optional[str] = None
    ) -> Dict:
        """Export references to Zotero"""
        try:
            headers = {
                'Zotero-API-Key': api_key,
                'Zotero-API-Version': '3',
                'Content-Type': 'application/json'
            }

            # Convert our references to Zotero format
            zotero_items = []
            for ref in references:
                item = {
                    'itemType': ref.get('type', 'journalArticle'),
                    'title': ref.get('title'),
                    'creators': [
                        {'creatorType': 'author', 'name': author}
                        for author in ref.get('authors', [])
                    ],
                    'date': str(ref.get('year', '')),
                    'publicationTitle': ref.get('publication'),
                    'DOI': ref.get('doi'),
                    'url': ref.get('url'),
                    'abstractNote': ref.get('abstract')
                }

                if collection_id:
                    item['collections'] = [collection_id]

                zotero_items.append(item)

            # Post to Zotero
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/users/{user_id}/items"

                async with session.post(url, headers=headers, json=zotero_items) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'success': True,
                            'count': len(result.get('successful', [])),
                            'failed': len(result.get('failed', []))
                        }
                    else:
                        return {
                            'success': False,
                            'error': f'Zotero API error: {response.status}'
                        }

        except Exception as e:
            print(f"❌ Failed to export to Zotero: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _format_item(self, item: Dict) -> Dict:
        """Format Zotero item to our structure"""
        data = item.get('data', {})

        # Extract authors
        authors = []
        for creator in data.get('creators', []):
            if 'name' in creator:
                authors.append(creator['name'])
            elif 'lastName' in creator:
                name = creator.get('firstName', '') + ' ' + creator.get('lastName', '')
                authors.append(name.strip())

        return {
            'id': item.get('key'),
            'title': data.get('title'),
            'authors': authors,
            'year': data.get('date', '')[:4] if data.get('date') else None,
            'publication': data.get('publicationTitle'),
            'doi': data.get('DOI'),
            'url': data.get('url'),
            'abstract': data.get('abstractNote'),
            'item_type': data.get('itemType'),
            'collections': data.get('collections', [])
        }


zotero_service = ZoteroService()
