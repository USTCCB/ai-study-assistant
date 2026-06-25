"""ORM 模型"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime
from app.core.db import Base


class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(512))
    source = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow)


class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(UUID(as_uuid=True))
    content = Column(Text)
    embedding = Column(Vector(1536))  # text-embedding-3-small
    chunk_index = Column(Integer)
