# backend/app/models/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime

# --- Βασικά Schemas ---
class ChatRequest(BaseModel):
    content: str
    conversation_id: Optional[UUID] = None
    # Προσωρινά, θα το παίρνουμε από το request. Αργότερα θα έρχεται από authentication.
    user_id: UUID

class Attachment(BaseModel):
    type: str # 'excel', 'pdf', 'references'
    name: str
    size: str

class ChatResponse(BaseModel):
    message_id: UUID
    conversation_id: UUID
    response_content: str
    needs_confirmation: bool
    attachments: List[Attachment] = []
    created_at: datetime

# --- Schemas για εσωτερική χρήση (π.χ. επιστροφή από DB) ---
class Message(BaseModel):
    id: UUID
    conversation_id: UUID
    message_type: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True # Επιτρέπει τη δημιουργία του schema από ORM model