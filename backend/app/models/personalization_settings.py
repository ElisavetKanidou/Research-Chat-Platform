"""
Personalization Settings Model - CORRECTED VERSION
app/models/personalization_settings.py
"""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import BaseModel  # ✅ CORRECT IMPORT


class PersonalizationSettings(BaseModel):
    """
    AI Personalization settings for users
    Stores user-specific AI behavior preferences
    """
    __tablename__ = "personalization_settings"

    # Foreign key to user
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    # AI Personalization Levels (1-10)
    lab_level = Column(Integer, default=7, nullable=False)
    personal_level = Column(Integer, default=8, nullable=False)
    global_level = Column(Integer, default=5, nullable=False)

    # Writing preferences
    writing_style = Column(String(50), default="academic", nullable=False)
    context_depth = Column(String(20), default="moderate", nullable=False)

    # Research focus areas (JSON array)
    research_focus = Column(JSON, default=list, nullable=False)

    # AI behavior
    suggestions_enabled = Column(Boolean, default=True, nullable=False)

    # Relationship back to User
    user = relationship("User", back_populates="personalization_settings")

    def __repr__(self):
        return (
            f"<PersonalizationSettings("
            f"user_id={self.user_id}, "
            f"lab={self.lab_level}, "
            f"personal={self.personal_level}, "
            f"global={self.global_level}"
            f")>"
        )

    def to_dict(self) -> dict:
        """Convert to dictionary with camelCase keys for frontend"""
        return {
            "id": str(self.id),
            "userId": str(self.user_id),
            "labLevel": self.lab_level,
            "personalLevel": self.personal_level,
            "globalLevel": self.global_level,
            "writingStyle": self.writing_style,
            "contextDepth": self.context_depth,
            "researchFocus": self.research_focus or [],
            "suggestionsEnabled": self.suggestions_enabled,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }

    def update_from_dict(self, data: dict) -> None:
        """Update from dictionary (accepts both camelCase and snake_case)"""
        # Map camelCase to snake_case
        field_map = {
            'labLevel': 'lab_level',
            'personalLevel': 'personal_level',
            'globalLevel': 'global_level',
            'writingStyle': 'writing_style',
            'contextDepth': 'context_depth',
            'researchFocus': 'research_focus',
            'suggestionsEnabled': 'suggestions_enabled'
        }

        for key, value in data.items():
            # Convert camelCase to snake_case if needed
            field_name = field_map.get(key, key)

            if hasattr(self, field_name) and field_name not in ['id', 'user_id', 'created_at']:
                setattr(self, field_name, value)

        from datetime import datetime
        self.updated_at = datetime.utcnow()