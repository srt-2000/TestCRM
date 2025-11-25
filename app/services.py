"""Business logic for contact distribution."""

import random
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Lead, Contact, Operator, OperatorSourceWeight, Source


def get_or_create_lead(db: Session, email: str) -> Lead:
    """
    Find lead by email or create new one.
    
    Args:
        db: Database session
        email: Lead email
        
    Returns:
        Lead: Found or created lead
        
    Raises:
        ValueError: If email is invalid
    """
    if not email or not email.strip():
        raise ValueError("Email cannot be empty")
    
    lead = db.query(Lead).filter_by(email=email).first()
    if not lead:
        lead = Lead(email=email)
        db.add(lead)
        db.commit()
        db.refresh(lead)
    return lead


def get_available_operators(db: Session, source_id: int) -> List[Tuple[Operator, int]]:
    """
    Get available operators for source with their weights.
    
    Args:
        db: Database session
        source_id: Source ID
        
    Returns:
        List of tuples (Operator, weight) for available operators
    """
    # Check if source exists
    source = db.query(Source).filter_by(id=source_id).first()
    if not source:
        return []
    
    # Get all operator-source weights for this source
    weights = db.query(OperatorSourceWeight).filter_by(source_id=source_id).all()
    
    if not weights:
        return []
    
    available_operators = []
    
    for weight_obj in weights:
        operator = db.query(Operator).filter_by(id=weight_obj.operator_id).first()
        
        if not operator:
            continue
        
        # Check if operator is active
        if not operator.is_active:
            continue
        
        # Count current active contacts for this operator
        current_load = db.query(func.count(Contact.id)).filter_by(
            operator_id=operator.id,
            status="active"
        ).scalar()
        
        # Check if operator has capacity
        if current_load < operator.max_load_limit:
            available_operators.append((operator, weight_obj.weight))
    
    return available_operators


def select_operator_by_weights(operators_with_weights: List[Tuple[Operator, int]]) -> Optional[Operator]:
    """
    Select operator probabilistically based on weights.
    
    Args:
        operators_with_weights: List of tuples (Operator, weight)
        
    Returns:
        Selected operator or None if list is empty
    """
    if not operators_with_weights:
        return None
    
    if len(operators_with_weights) == 1:
        return operators_with_weights[0][0]
    
    operators = [op for op, _ in operators_with_weights]
    weights = [w for _, w in operators_with_weights]
    
    selected = random.choices(operators, weights=weights, k=1)[0]
    return selected


def create_contact(db: Session, email: str, source_id: int) -> Contact:
    """
    Create contact and assign operator based on distribution rules.
    
    Args:
        db: Database session
        email: Lead email
        source_id: Source ID
        
    Returns:
        Created contact
        
    Raises:
        ValueError: If source not found or invalid data
    """
    # Validate source exists
    source = db.query(Source).filter_by(id=source_id).first()
    if not source:
        raise ValueError(f"Source with id {source_id} not found")
    
    # Get or create lead
    lead = get_or_create_lead(db, email)
    
    # Get available operators
    available_operators = get_available_operators(db, source_id)
    
    # Select operator by weights
    operator = None
    if available_operators:
        operator = select_operator_by_weights(available_operators)
    
    # Create contact (operator_id can be None if no available operators)
    contact = Contact(
        lead_id=lead.id,
        source_id=source_id,
        operator_id=operator.id if operator else None,
        status="active"
    )
    
    db.add(contact)
    db.commit()
    db.refresh(contact)
    
    return contact

