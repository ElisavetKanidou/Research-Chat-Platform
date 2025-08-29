# backend/app/db/models.py

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, JSON, Boolean, Text, Integer, ARRAY, ForeignKey,
    PrimaryKeyConstraint, CheckConstraint, Float
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, BYTEA
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from .database import Base

# --- Core User and Research Management Models ---

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    lab_affiliation = Column(String(255), nullable=True)
    research_domains = Column(ARRAY(Text), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    last_active = Column(DateTime, server_default=func.now(), onupdate=func.now())
    personalization_settings = Column(JSONB, nullable=False, server_default=text("""
        '{ "lab_level": 7, "personal_level": 8, "global_level": 5 }'::jsonb
    """))

    # Relationships
    lab_associations = relationship("UserLab", back_populates="user", cascade="all, delete-orphan")
    papers = relationship("Paper", back_populates="owner", foreign_keys="[Paper.owner_user_id]")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    research_projects = relationship("ResearchProject", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("UserFeedback", back_populates="user", cascade="all, delete-orphan")
    writing_styles = relationship("WritingStyle", back_populates="user", cascade="all, delete-orphan")

class Lab(Base):
    __tablename__ = "labs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=True)
    research_focus = Column(ARRAY(Text), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user_associations = relationship("UserLab", back_populates="lab", cascade="all, delete-orphan")
    papers = relationship("Paper", back_populates="lab", foreign_keys="[Paper.owner_lab_id]")

class UserLab(Base):
    __tablename__ = "user_labs"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    lab_id = Column(UUID(as_uuid=True), ForeignKey("labs.id"), primary_key=True)
    role = Column(String(50), default='member')
    joined_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="lab_associations")
    lab = relationship("Lab", back_populates="user_associations")

class Paper(Base):
    __tablename__ = "papers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    authors = Column(ARRAY(Text), nullable=True)
    abstract = Column(Text, nullable=True)
    full_text = Column(Text, nullable=True)
    publication_year = Column(Integer, nullable=True)
    journal = Column(String(255), nullable=True)
    doi = Column(String(255), nullable=True)
    paper_type = Column(String(50), default='personal')
    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    owner_lab_id = Column(UUID(as_uuid=True), ForeignKey("labs.id"), nullable=True)
    upload_date = Column(DateTime, server_default=func.now())
    processing_status = Column(String(50), default='pending')
    style_features = Column(JSONB, nullable=True)
    citation_count = Column(Integer, default=0)
    keywords = Column(ARRAY(Text), nullable=True)

    # Relationships
    owner = relationship("User", back_populates="papers", foreign_keys=[owner_user_id])
    lab = relationship("Lab", back_populates="papers", foreign_keys=[owner_lab_id])
    citations_made = relationship("Citation", foreign_keys="[Citation.paper_id]", back_populates="citing_paper", cascade="all, delete-orphan")
    cited_by = relationship("Citation", foreign_keys="[Citation.cited_paper_id]", back_populates="cited_paper", cascade="all, delete-orphan")

# --- Conversation and Interaction Models ---

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True)
    research_topic = Column(String(255), nullable=True)
    current_phase = Column(String(50), default='ideation')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    personalization_snapshot = Column(JSONB, nullable=True)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    research_projects = relationship("ResearchProject", back_populates="conversation")
    literature_searches = relationship("LiteratureSearch", back_populates="conversation", cascade="all, delete-orphan")
    generated_documents = relationship("GeneratedDocument", back_populates="conversation", cascade="all, delete-orphan")
    research_gaps = relationship("ResearchGap", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    message_type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    needs_confirmation = Column(Boolean, default=False)
    confirmation_status = Column(String(20), nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    ai_model_used = Column(String(50), nullable=True)
    personalization_context = Column(JSONB, nullable=True)
    attachments = Column(JSONB, nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    feedback = relationship("UserFeedback", back_populates="message", cascade="all, delete-orphan")

# --- Research Artifact Models ---

class ResearchProject(Base):
    __tablename__ = "research_projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    research_questions = Column(ARRAY(Text), nullable=True)
    methodology = Column(Text, nullable=True)
    current_status = Column(String(50), default='planning')
    target_venue = Column(String(255), nullable=True)
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    paper_structure = Column(JSONB, nullable=True)

    # Relationships
    user = relationship("User", back_populates="research_projects")
    conversation = relationship("Conversation", back_populates="research_projects")

class LiteratureSearch(Base):
    __tablename__ = "literature_searches"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    query = Column(Text, nullable=False)
    search_parameters = Column(JSONB, nullable=True)
    results = Column(JSONB, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    relevance_confirmed = Column(Boolean, nullable=True)
    selected_papers = Column(ARRAY(UUID(as_uuid=True)), nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="literature_searches")

class GeneratedDocument(Base):
    __tablename__ = "generated_documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    document_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=True)
    content = Column(BYTEA, nullable=True)
    file_path = Column(String(500), nullable=True)
    document_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    download_count = Column(Integer, default=0)

    # Relationships
    conversation = relationship("Conversation", back_populates="generated_documents")

class ResearchGap(Base):
    __tablename__ = "research_gaps"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    gap_title = Column(String(255), nullable=True)
    gap_description = Column(Text, nullable=True)
    supporting_evidence = Column(ARRAY(Text), nullable=True)
    potential_impact = Column(Text, nullable=True)
    research_questions = Column(ARRAY(Text), nullable=True)
    confidence_score = Column(Float, nullable=True)
    user_confirmed = Column(Boolean, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="research_gaps")

# --- Metadata and Learning Models ---

class UserFeedback(Base):
    __tablename__ = "user_feedback"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=True)
    feedback_type = Column(String(50), nullable=True)
    rating = Column(Integer, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (CheckConstraint('rating >= 1 AND rating <= 5', name='rating_check'),)

    # Relationships
    user = relationship("User", back_populates="feedback")
    message = relationship("Message", back_populates="feedback")

class Citation(Base):
    __tablename__ = "citations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id"), nullable=False)
    cited_paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id"), nullable=False)
    citation_context = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    citing_paper = relationship("Paper", foreign_keys=[paper_id], back_populates="citations_made")
    cited_paper = relationship("Paper", foreign_keys=[cited_paper_id], back_populates="cited_by")

class WritingStyle(Base):
    __tablename__ = "writing_styles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id"), nullable=True)
    style_features = Column(JSONB, nullable=False)
    extracted_at = Column(DateTime, server_default=func.now())
    model_version = Column(String(50), nullable=True)

    # Relationships
    user = relationship("User", back_populates="writing_styles")
    paper = relationship("Paper")