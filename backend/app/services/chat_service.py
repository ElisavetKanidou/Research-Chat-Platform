# backend/app/services/chat_service.py

from sqlalchemy.orm import Session
from uuid import UUID
from ..db import models
from ..models import schemas
from typing import Optional


class ResearchChatEngine:
    def __init__(self, db: Session):
        self.db = db
        # Εδώ θα αρχικοποιούσες τις άλλες υπηρεσίες σου, π.χ.:
        # self.personalization_service = PersonalizationService(db)
        # self.ai_client = GoogleCloudAIService()

    def _get_or_create_conversation(self, user_id: UUID, conversation_id: Optional[UUID] = None) -> models.Conversation:
        """Βρίσκει μια υπάρχουσα συζήτηση ή δημιουργεί μια νέα."""
        if conversation_id:
            db_conversation = self.db.query(models.Conversation).filter(
                models.Conversation.id == conversation_id).first()
            if db_conversation:
                return db_conversation

        # Αν δεν βρεθεί ή δεν δόθηκε ID, δημιουργεί νέα
        new_conversation = models.Conversation(user_id=user_id)
        self.db.add(new_conversation)
        self.db.commit()
        self.db.refresh(new_conversation)
        return new_conversation

    async def process_message(self, request: schemas.ChatRequest) -> models.Message:
        """
        Κύρια μέθοδος επεξεργασίας ενός μηνύματος.
        1. Αποθηκεύει το μήνυμα του χρήστη.
        2. Καλεί το AI (προσομοίωση).
        3. Αποθηκεύει την απάντηση του AI.
        4. Επιστρέφει το αντικείμενο της απάντησης του AI.
        """
        conversation = self._get_or_create_conversation(request.user_id, request.conversation_id)

        # 1. Αποθήκευση μηνύματος χρήστη
        db_user_message = models.Message(
            conversation_id=conversation.id,
            message_type='user',
            content=request.content
        )
        self.db.add(db_user_message)
        self.db.commit()

        # 2. **PLACEHOLDER: Κλήση στο AI Service**
        # Εδώ θα καλούσες το πραγματικό AI μοντέλο σου, δίνοντάς του context.
        # ai_response_text = self.ai_client.generate(prompt=..., context=...)
        ai_response_text = f"Analyzed your idea: '{request.content}'. I found these papers: [Paper A, Paper B]. Do you agree?"

        # 3. Αποθήκευση απάντησης AI
        db_assistant_message = models.Message(
            conversation_id=conversation.id,
            message_type='assistant',
            content=ai_response_text,
            needs_confirmation=True,  # Παράδειγμα
            attachments=[]  # Θα το γέμιζε το AI service
        )
        self.db.add(db_assistant_message)
        self.db.commit()
        self.db.refresh(db_assistant_message)

        return db_assistant_message