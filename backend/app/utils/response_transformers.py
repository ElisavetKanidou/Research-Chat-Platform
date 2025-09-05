
"""
Frontend-Compatible Response Transformers (app/utils/response_transformers.py)
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.models.paper import Paper
from app.models.user import User


def transform_paper_for_frontend(paper: Paper) -> Dict[str, Any]:
    """Transform Paper model to frontend-compatible format"""
    return {
        "id": str(paper.id),
        "title": paper.title,
        "abstract": paper.abstract,
        "status": paper.status.value if hasattr(paper.status, 'value') else paper.status,
        "createdAt": paper.created_at.isoformat(),
        "lastModified": paper.updated_at.isoformat(),
        "progress": paper.progress,
        "targetWordCount": paper.target_word_count,
        "currentWordCount": paper.current_word_count,
        "coAuthors": paper.co_authors or [],
        "researchArea": paper.research_area or "",
        "sections": [
            {
                "id": str(section.id),
                "title": section.title,
                "content": section.content,
                "status": section.status.value if hasattr(section.status, 'value') else section.status,
                "lastModified": section.updated_at.isoformat(),
                "wordCount": section.word_count,
                "order": section.order
            }
            for section in sorted(paper.sections, key=lambda x: x.order)
        ],
        "tags": paper.tags or [],
        "isPublic": paper.is_public,
        "owner": {
            "id": str(paper.owner_id),
            "name": paper.owner.name if paper.owner else "Unknown",
            "email": paper.owner.email if paper.owner else "",
        } if hasattr(paper, 'owner') and paper.owner else None
    }


def transform_user_for_frontend(user: User) -> Dict[str, Any]:
    """Transform User model to frontend-compatible format"""
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "avatar": user.avatar_url,
        "createdAt": user.created_at.isoformat(),
        "lastLoginAt": user.last_login_at.isoformat() if user.last_login_at else None,
        "isActive": user.is_active,
        "personalInfo": {
            "name": user.name,
            "email": user.email,
            "affiliation": user.affiliation or "",
            "researchInterests": user.research_interests or [],
            "orcidId": user.orcid_id
        }
    }