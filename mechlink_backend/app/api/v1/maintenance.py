from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from app.config.database import get_db
from app.models.maintenance import MaintenanceRecord, MaintenanceReminder
from app.models.vehicle import Vehicle
from app.models.user import User
from app.schemas.maintenance_schemas import (
    MaintenanceRecordCreate, MaintenanceRecordResponse, MaintenanceRecordUpdate,
    MaintenanceRecordWithVehicle, MaintenanceReminderCreate, MaintenanceReminderResponse,
    MaintenanceReport, MaintenanceStats
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/maintenance", tags=["maintenance"])

# === MAINTENANCE RECORDS ===

@router.post("/records", response_model=MaintenanceRecordResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance_record(
    record_data: MaintenanceRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new maintenance record"""
    
    # Verify that the vehicle belongs to the user
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == record_data.vehicle_id,
        Vehicle.user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found or doesn't belong to user"
        )
    
    # Create record
    db_record = MaintenanceRecord(**record_data.dict())
    db.add(db_record)
    
    # Update vehicle mileage if it's higher
    if record_data.mileage_at_service > vehicle.current_mileage:
        vehicle.current_mileage = record_data.mileage_at_service
    
    db.commit()
    db.refresh(db_record)
    
    return db_record

@router.get("/records", response_model=List[MaintenanceRecordResponse])
def get_maintenance_records(
    skip: int = 0,
    limit: int = 20,
    vehicle_id: Optional[str] = Query(None, description="Filter by vehicle"),
    service_type: Optional[str] = Query(None, description="Filter by service type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve user's maintenance records"""
    
    # Get only user's vehicles
    user_vehicles = db.query(Vehicle.id).filter(Vehicle.user_id == current_user.id).subquery()
    
    query = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.vehicle_id.in_(user_vehicles)
    )
    
    # Apply filters
    if vehicle_id:
        query = query.filter(MaintenanceRecord.vehicle_id == vehicle_id)
    if service_type:
        query = query.filter(MaintenanceRecord.service_type.ilike(f"%{service_type}%"))
    
    records = query.order_by(desc(MaintenanceRecord.service_date)).offset(skip).limit(limit).all()
    return records

@router.get("/records/vehicle/{vehicle_id}", response_model=List[MaintenanceRecordResponse])
def get_vehicle_maintenance_history(
    vehicle_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve complete maintenance history for a vehicle"""
    
    # Verify that the vehicle belongs to the user
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    records = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.vehicle_id == vehicle_id
    ).order_by(desc(MaintenanceRecord.service_date)).all()
    
    return records

@router.get("/records/{record_id}", response_model=MaintenanceRecordWithVehicle)
def get_maintenance_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve specific record with vehicle information"""
    
    record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found"
        )
    
    # Verify that the vehicle belongs to the user
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == record.vehicle_id,
        Vehicle.user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    record_dict = {
        **record.__dict__,
        "vehicle": {
            "id": vehicle.id,
            "make": vehicle.make,
            "model": vehicle.model,
            "year": vehicle.year,
            "license_plate": vehicle.license_plate
        }
    }
    
    return record_dict

@router.put("/records/{record_id}", response_model=MaintenanceRecordResponse)
def update_maintenance_record(
    record_id: str,
    record_update: MaintenanceRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update maintenance record"""
    
    record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found"
        )
    
    # Verify permissions
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == record.vehicle_id,
        Vehicle.user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update fields
    for field, value in record_update.dict(exclude_unset=True).items():
        setattr(record, field, value)
    
    db.commit()
    db.refresh(record)
    return record

@router.delete("/records/{record_id}")
def delete_maintenance_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete maintenance record"""
    
    record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found"
        )
    
    # Verify permissions
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == record.vehicle_id,
        Vehicle.user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    db.delete(record)
    db.commit()
    
    return {"message": "Maintenance record deleted successfully"}

# === REMINDERS ===

@router.post("/reminders", response_model=MaintenanceReminderResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance_reminder(
    reminder_data: MaintenanceReminderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a maintenance reminder"""
    
    # Verify that the vehicle belongs to the user
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == reminder_data.vehicle_id,
        Vehicle.user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Create reminder
    db_reminder = MaintenanceReminder(
        **reminder_data.dict(),
        user_id=current_user.id
    )
    
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    
    return db_reminder

@router.get("/reminders", response_model=List[MaintenanceReminderResponse])
def get_maintenance_reminders(
    active_only: bool = Query(True, description="Only active reminders"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve user's maintenance reminders"""
    
    query = db.query(MaintenanceReminder).filter(
        MaintenanceReminder.user_id == current_user.id
    )
    
    if active_only:
        query = query.filter(MaintenanceReminder.is_active == True)
    
    reminders = query.order_by(MaintenanceReminder.due_date).all()
    return reminders

@router.get("/reminders/due", response_model=List[MaintenanceReminderResponse])
def get_due_reminders(
    days_ahead: int = Query(7, ge=1, le=365, description="Days ahead to search"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve reminders that are due soon"""
    
    today = date.today()
    future_date = today + timedelta(days=days_ahead)
    
    reminders = db.query(MaintenanceReminder).filter(
        MaintenanceReminder.user_id == current_user.id,
        MaintenanceReminder.is_active == True,
        MaintenanceReminder.due_date.between(today, future_date)
    ).order_by(MaintenanceReminder.due_date).all()
    
    return reminders

# === REPORTS ===

@router.get("/reports/vehicle/{vehicle_id}", response_model=MaintenanceReport)
def get_vehicle_maintenance_report(
    vehicle_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate maintenance report for a vehicle"""
    
    # Verify vehicle
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Get statistics
    records = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.vehicle_id == vehicle_id
    ).all()
    
    total_records = len(records)
    total_cost = sum(record.cost or 0 for record in records)
    
    last_service = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.vehicle_id == vehicle_id
    ).order_by(desc(MaintenanceRecord.service_date)).first()
    
    # Next service
    next_service = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.vehicle_id == vehicle_id,
        MaintenanceRecord.next_service_due >= date.today()
    ).order_by(MaintenanceRecord.next_service_due).first()
    
    # Services by type
    services_by_type = {}
    for record in records:
        if record.service_type in services_by_type:
            services_by_type[record.service_type] += 1
        else:
            services_by_type[record.service_type] = 1
    
    return {
        "vehicle_id": vehicle_id,
        "vehicle_info": {
            "make": vehicle.make,
            "model": vehicle.model,
            "year": vehicle.year,
            "license_plate": vehicle.license_plate,
            "current_mileage": vehicle.current_mileage
        },
        "total_records": total_records,
        "total_cost": total_cost,
        "last_service_date": last_service.service_date if last_service else None,
        "next_service_due": next_service.next_service_due if next_service else None,
        "average_cost_per_service": total_cost / total_records if total_records > 0 else 0,
        "services_by_type": services_by_type
    }
