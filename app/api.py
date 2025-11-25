"""FastAPI routers for CRM API."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Operator, Source, Contact, Lead, OperatorSourceWeight
from app.schemas import (
    OperatorCreate, OperatorUpdate, Operator as OperatorSchema,
    SourceCreate, Source as SourceSchema,
    SourceOperatorWeightsUpdate,
    ContactCreate, Contact as ContactSchema,
    LeadWithContacts
)
from app.services import create_contact

router = APIRouter()


# Operator endpoints
@router.post("/operators", response_model=OperatorSchema, status_code=201)
def create_operator(operator: OperatorCreate, db: Session = Depends(get_db)):
    """Create new operator."""
    db_operator = Operator(**operator.model_dump())
    db.add(db_operator)
    db.commit()
    db.refresh(db_operator)
    return db_operator


@router.get("/operators", response_model=List[OperatorSchema])
def get_operators(db: Session = Depends(get_db)):
    """Get all operators."""
    return db.query(Operator).all()


@router.patch("/operators/{operator_id}", response_model=OperatorSchema)
def update_operator(operator_id: int, operator_update: OperatorUpdate, db: Session = Depends(get_db)):
    """Update operator (is_active and/or max_load_limit)."""
    db_operator = db.query(Operator).filter_by(id=operator_id).first()
    if not db_operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    
    update_data = operator_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_operator, field, value)
    
    db.commit()
    db.refresh(db_operator)
    return db_operator


# Source endpoints
@router.post("/sources", response_model=SourceSchema, status_code=201)
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    """Create new source."""
    db_source = Source(**source.model_dump())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


@router.get("/sources", response_model=List[SourceSchema])
def get_sources(db: Session = Depends(get_db)):
    """Get all sources."""
    return db.query(Source).all()


@router.post("/sources/{source_id}/operators", status_code=201)
def set_source_operators(source_id: int, weights_update: SourceOperatorWeightsUpdate, db: Session = Depends(get_db)):
    """Set operators and weights for source."""
    source = db.query(Source).filter_by(id=source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Delete existing weights for this source
    db.query(OperatorSourceWeight).filter_by(source_id=source_id).delete()
    
    # Create new weights
    for op_weight in weights_update.operators:
        # Validate operator exists
        operator = db.query(Operator).filter_by(id=op_weight.operator_id).first()
        if not operator:
            raise HTTPException(status_code=404, detail=f"Operator with id {op_weight.operator_id} not found")
        
        weight_obj = OperatorSourceWeight(
            operator_id=op_weight.operator_id,
            source_id=source_id,
            weight=op_weight.weight
        )
        db.add(weight_obj)
    
    db.commit()
    return {"message": "Operators and weights updated successfully"}


# Contact endpoints
@router.post("/contacts", response_model=ContactSchema, status_code=201)
def register_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    """Register new contact (appeal)."""
    try:
        created_contact = create_contact(db, contact.email, contact.source_id)
        return created_contact
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/contacts", response_model=List[ContactSchema])
def get_contacts(db: Session = Depends(get_db)):
    """Get all contacts."""
    return db.query(Contact).all()


# Lead endpoints
@router.get("/leads", response_model=List[LeadWithContacts])
def get_leads(db: Session = Depends(get_db)):
    """Get all leads with their contacts."""
    leads = db.query(Lead).all()
    return leads

