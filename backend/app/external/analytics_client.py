
"""
Analytics Client (app/external/analytics_client.py)
"""
import httpx
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from app.core.config import settings
from app.core.exceptions import ExternalServiceException

logger = logging.getLogger(__name__)


class AnalyticsClient:
    """External analytics service client"""

    def __init__(self):
        self.api_key = getattr(settings, 'ANALYTICS_API_KEY', None)
        self.base_url = getattr(settings, 'ANALYTICS_BASE_URL', None)
        self.enabled = bool(self.api_key and self.base_url)

        if not self.enabled:
            logger.warning("Analytics service not configured")

    async def track_event(
            self,
            user_id: str,
            event_name: str,
            properties: Dict[str, Any],
            timestamp: Optional[datetime] = None
    ) -> bool:
        """Track user event"""

        if not self.enabled:
            return False

        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "user_id": user_id,
                    "event": event_name,
                    "properties": properties,
                    "timestamp": (timestamp or datetime.utcnow()).isoformat()
                }

                response = await client.post(
                    f"{self.base_url}/track",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=5.0
                )

                return response.status_code == 200

        except Exception as e:
            logger.error(f"Analytics tracking failed: {e}")
            return False

    async def get_user_analytics(
            self,
            user_id: str,
            start_date: datetime,
            end_date: datetime
    ) -> Optional[Dict[str, Any]]:
        """Get user analytics data"""

        if not self.enabled:
            return None

        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "user_id": user_id,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }

                response = await client.get(
                    f"{self.base_url}/users/{user_id}/analytics",
                    params=params,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0
                )

                if response.status_code == 200:
                    return response.json()

                return None

        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            return None

    async def create_dashboard(
            self,
            user_id: str,
            dashboard_config: Dict[str, Any]
    ) -> Optional[str]:
        """Create custom analytics dashboard"""

        if not self.enabled:
            return None

        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "user_id": user_id,
                    "config": dashboard_config
                }

                response = await client.post(
                    f"{self.base_url}/dashboards",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0
                )

                if response.status_code == 201:
                    return response.json().get("dashboard_id")

                return None

        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")
            return None


# Create client instance
analytics_client = AnalyticsClient()
