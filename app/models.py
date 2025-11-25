"""SQLAlchemy models for CRM system."""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from app.database import Base


def utc_now():
    """Get current UTC datetime."""
    return datetime.now(UTC)


class Operator(Base):
    """Operator model."""
    
    __tablename__ = "operators"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    max_load_limit = Column(Integer, nullable=False)
    
    # Relationships
    source_weights = relationship("OperatorSourceWeight", back_populates="operator", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="operator")


class Source(Base):
    """Source (bot) model."""
    
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Relationships
    operator_weights = relationship("OperatorSourceWeight", back_populates="source", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="source")


class OperatorSourceWeight(Base):
    """Operator-Source weight relationship."""
    
    __tablename__ = "operator_source_weights"
    
    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    weight = Column(Integer, nullable=False)
    
    __table_args__ = (UniqueConstraint("operator_id", "source_id", name="uq_operator_source"),)
    
    # Relationships
    operator = relationship("Operator", back_populates="source_weights")
    source = relationship("Source", back_populates="operator_weights")


class Lead(Base):
    """Lead (client) model."""
    
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    
    # Relationships
    contacts = relationship("Contact", back_populates="lead")


class Contact(Base):
    """Contact (appeal) model."""
    
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=utc_now)
    
    # Relationships
    lead = relationship("Lead", back_populates="contacts")
    source = relationship("Source", back_populates="contacts")
    operator = relationship("Operator", back_populates="contacts")

