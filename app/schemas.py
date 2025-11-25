"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime


# Operator schemas
class OperatorCreate(BaseModel):
    """Schema for creating operator."""
    
    name: str
    is_active: bool = True
    max_load_limit: int


class OperatorUpdate(BaseModel):
    """Schema for updating operator."""
    
    is_active: Optional[bool] = None
    max_load_limit: Optional[int] = None


class Operator(BaseModel):
    """Schema for operator response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    is_active: bool
    max_load_limit: int


# Source schemas
class SourceCreate(BaseModel):
    """Schema for creating source."""
    
    name: str
    description: Optional[str] = None


class Source(BaseModel):
    """Schema for source response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str] = None


# Operator-Source weight schemas
class SourceOperatorWeight(BaseModel):
    """Schema for operator weight in source."""
    
    operator_id: int
    weight: int


class SourceOperatorWeightsUpdate(BaseModel):
    """Schema for updating operator weights for source."""
    
    operators: List[SourceOperatorWeight]


class OperatorSourceWeight(BaseModel):
    """Schema for operator-source weight response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    operator_id: int
    source_id: int
    weight: int


# Lead schemas
class LeadCreate(BaseModel):
    """Schema for creating lead."""
    
    email: EmailStr


class Lead(BaseModel):
    """Schema for lead response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str


# Contact schemas
class ContactCreate(BaseModel):
    """Schema for creating contact."""
    
    email: EmailStr
    source_id: int


class Contact(BaseModel):
    """Schema for contact response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    lead_id: int
    source_id: int
    operator_id: Optional[int] = None
    status: str
    created_at: datetime


class LeadWithContacts(BaseModel):
    """Schema for lead with contacts."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    contacts: List[Contact]

