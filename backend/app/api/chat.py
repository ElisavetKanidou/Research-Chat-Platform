# backend/app/api/chat.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import schemas
from ..db.database import get_db
from ..services.chat_service import ResearchChatEngine

router = APIRouter()

@router.post("/message", response_model=schemas.ChatResponse)
async def post_message(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint για την αποστολή ενός μηνύματος και τη λήψη απάντησης από το AI.
    """
    try:
        engine = ResearchChatEngine(db=db)
        assistant_message = await engine.process_message(request)

        return schemas.ChatResponse(
            message_id=assistant_message.id,
            conversation_id=assistant_message.conversation_id,
            response_content=assistant_message.content,
            needs_confirmation=assistant_message.needs_confirmation,
            attachments=assistant_message.attachments or [],
            created_at=assistant_message.created_at
        )
    except Exception as e:
        # Γενικό error handling για την περίπτωση που κάτι πάει στραβά
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")