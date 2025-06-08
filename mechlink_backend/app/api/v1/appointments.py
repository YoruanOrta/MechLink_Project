from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from datetime import datetime

from app.models.notification import NotificationType, NotificationChannel
from app.services.notification_service import NotificationService
from app.config.database import get_db
from app.models.workshop import Workshop, Appointment
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.workshop_schemas import (
    AppointmentCreate, AppointmentResponse, AppointmentUpdate, AppointmentWithDetails
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/appointments", tags=["appointments"])

# === APPOINTMENT ENDPOINTS ===

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_data: AppointmentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new appointment at a workshop"""
    
    # Verify that the workshop exists
    workshop = db.query(Workshop).filter(Workshop.id == appointment_data.workshop_id).first()
    if not workshop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workshop not found"
        )
    
    # Verify that the vehicle belongs to the user
    vehicle = db.query(Vehicle).filter(
        and_(
            Vehicle.id == appointment_data.vehicle_id,
            Vehicle.user_id == current_user.id
        )
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found or doesn't belong to user"
        )
    
    # Create appointment
    db_appointment = Appointment(
        **appointment_data.dict(),
        user_id=current_user.id
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)

    notification_service = NotificationService(db)
    try:
        background_tasks.add_task(
            notification_service.send_appointment_confirmation,
            db_appointment.id
        )
    except Exception as e:
        # Log error but do not fail appointment creation
        print(f"Error sending confirmation: {e}")
    
    # 2. Schedule reminders
    try:
        background_tasks.add_task(
            notification_service.schedule_appointment_reminders,
            db_appointment.id
        )
    except Exception as e:
        # Log error but do not fail appointment creation
        print(f"Error scheduling reminders: {e}")
    
    return db_appointment

@router.get("/{appointment_id}", response_model=AppointmentWithDetails)
def get_appointment(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific appointment with details - SPECIFIC ROUTE FIRST"""
    
    appointment = db.query(Appointment).filter(
        and_(
            Appointment.id == appointment_id,
            Appointment.user_id == current_user.id
        )
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Retrieve workshop and vehicle information
    workshop = db.query(Workshop).filter(Workshop.id == appointment.workshop_id).first()
    vehicle = db.query(Vehicle).filter(Vehicle.id == appointment.vehicle_id).first()
    
    appointment_dict = {
        **appointment.__dict__,
        "workshop": {
            "id": workshop.id,
            "name": workshop.name,
            "address": workshop.address,
            "city": workshop.city,
            "phone": workshop.phone
        },
        "vehicle": {
            "id": vehicle.id,
            "make": vehicle.make,
            "model": vehicle.model,
            "year": vehicle.year,
            "license_plate": vehicle.license_plate
        }
    }
    
    return appointment_dict

@router.get("/", response_model=List[AppointmentResponse])
def get_user_appointments(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get appointments for the authenticated user - GENERAL ROUTE AFTER"""
    
    query = db.query(Appointment).filter(Appointment.user_id == current_user.id)
    
    # Apply status filter if provided
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    
    appointments = query.order_by(
        desc(Appointment.appointment_datetime)
    ).offset(skip).limit(limit).all()
    
    return appointments

@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: str,
    appointment_data: AppointmentUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update existing appointment"""
    
    # Verify that the appointment exists and belongs to the user
    appointment = db.query(Appointment).filter(
        and_(
            Appointment.id == appointment_id,
            Appointment.user_id == current_user.id
        )
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    update_data = appointment_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(appointment, field, value)
    
    db.commit()
    db.refresh(appointment)
    
    # ✅ ADD: Notify if the status changed to "completed"
    if update_data.get('status') == 'completed':
        notification_service = NotificationService(db)
        try:
            # Send review request after 1 hour
            background_tasks.add_task(
                notification_service.send_review_request,
                appointment.id
            )
        except Exception as e:
            print(f"Error sending review request: {e}")
    
    return appointment

@router.delete("/{appointment_id}")
def cancel_appointment(
    appointment_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel/delete appointment"""
    
    # Verify that the appointment exists and belongs to the user
    appointment = db.query(Appointment).filter(
        and_(
            Appointment.id == appointment_id,
            Appointment.user_id == current_user.id
        )
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Change status to cancelled instead of deleting
    appointment.status = "cancelled"
    db.commit()
    # ✅ ADD: Notify cancellation
    notification_service = NotificationService(db)
    try:
        workshop = db.query(Workshop).filter(Workshop.id == appointment.workshop_id).first()
        
        background_tasks.add_task(
            notification_service.create_notification,
            appointment.user_id,
            NotificationType.APPOINTMENT_CANCELLED,
            NotificationChannel.EMAIL,
            "Appointment Cancelled - MechLink",
            f"Your appointment for {appointment.service_type} at {workshop.name} scheduled for {appointment.appointment_datetime.strftime('%d/%m/%Y %H:%M')} has been cancelled.",
            {
                "appointment_id": appointment.id,
                "workshop_name": workshop.name,
                "service_type": appointment.service_type,
                "appointment_datetime": appointment.appointment_datetime.isoformat()
            }
        )
    except Exception as e:
        print(f"Error sending cancellation notification: {e}")
    
    return {"message": "Appointment cancelled successfully"}

# === ENDPOINT TEMPORAL DE DEBUG ===
@router.get("/debug/info")
def debug_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint temporal para debug"""
    try:
        # Verify user
        user_info = {
            "user_id": current_user.id,
            "email": current_user.email
        }
        
        # Search for appointments
        appointments = db.query(Appointment).filter(Appointment.user_id == current_user.id).all()
        
        return {
            "debug": "success",
            "user": user_info,
            "appointments_found": len(appointments),
            "appointments": [
                {
                    "id": apt.id,
                    "workshop_id": apt.workshop_id,
                    "service_type": apt.service_type,
                    "status": apt.status
                } for apt in appointments
            ]
        }
    except Exception as e:
        return {
            "debug": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }