from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.config.database import get_db
from app.models.notification import (
    Notification, NotificationTemplate, NotificationPreference,
    NotificationType, NotificationStatus, NotificationChannel
)
from app.models.user import User
from app.schemas.notification_schemas import (
    NotificationCreate, NotificationUpdate, NotificationResponse,
    NotificationTemplateCreate, NotificationTemplateUpdate, NotificationTemplateResponse,
    NotificationPreferenceCreate, NotificationPreferenceUpdate, NotificationPreferenceResponse,
    BulkNotificationCreate, NotificationStats, SendNotificationRequest,
    ReminderScheduleRequest, TestNotificationRequest
)
from app.api.deps import get_current_user
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notificaciones"])

# === USER NOTIFICATION ENDPOINTS ===

@router.get("/", response_model=List[NotificationResponse])
def get_user_notifications(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    type_filter: Optional[str] = Query(None, description="Filter by type"),
    unread_only: bool = Query(False, description="Only unread"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve user notifications"""
    
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    # Apply filters
    if status_filter:
        try:
            status_enum = NotificationStatus(status_filter)
            query = query.filter(Notification.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    if type_filter:
        try:
            type_enum = NotificationType(type_filter)
            query = query.filter(Notification.type == type_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid type: {type_filter}"
            )
    
    if unread_only:
        query = query.filter(Notification.read_at.is_(None))
    
    notifications = query.order_by(
        desc(Notification.created_at)
    ).offset(skip).limit(limit).all()
    
    return notifications

@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve specific notification"""
    
    notification = db.query(Notification).filter(
        and_(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return notification

@router.patch("/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark notification as read"""
    
    notification_service = NotificationService(db)
    success = notification_service.mark_as_read(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification marked as read"}

@router.patch("/mark-all-read")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read"""
    
    unread_notifications = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.read_at.is_(None)
        )
    ).all()
    
    for notification in unread_notifications:
        notification.status = NotificationStatus.READ
        notification.read_at = datetime.now()
    
    db.commit()
    
    return {"message": f"{len(unread_notifications)} notifications marked as read"}

@router.get("/stats/user", response_model=dict)
def get_user_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve user notification statistics"""
    
    notification_service = NotificationService(db)
    stats = notification_service.get_notification_stats(current_user.id)
    
    return stats

# === NOTIFICATION PREFERENCES ===

@router.get("/preferences", response_model=NotificationPreferenceResponse)
def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve user notification preferences"""
    
    notification_service = NotificationService(db)
    preferences = notification_service.get_user_preferences(current_user.id)
    
    return preferences

@router.put("/preferences", response_model=NotificationPreferenceResponse)
def update_notification_preferences(
    preference_data: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user notification preferences"""
    
    notification_service = NotificationService(db)
    preferences = notification_service.get_user_preferences(current_user.id)
    
    # Update fields
    update_data = preference_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preferences, field, value)
    
    db.commit()
    db.refresh(preferences)
    
    return preferences

# === SEND NOTIFICATIONS ===

@router.post("/send", response_model=NotificationResponse)
def send_notification(
    notification_request: SendNotificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send immediate notification"""
    
    notification_service = NotificationService(db)
    
    notification = notification_service.create_notification(
        user_id=notification_request.user_id,
        notification_type=notification_request.type,
        channel=notification_request.channel,
        title=notification_request.title,
        message=notification_request.message,
        data=notification_request.data
    )
    
    return notification

@router.post("/bulk-send")
def send_bulk_notifications(
    bulk_request: BulkNotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send bulk notifications"""
    
    notification_service = NotificationService(db)
    created_notifications = []
    
    for user_id in bulk_request.user_ids:
        try:
            notification = notification_service.create_notification(
                user_id=user_id,
                notification_type=bulk_request.type,
                channel=bulk_request.channel,
                title=bulk_request.title,
                message=bulk_request.message,
                data=bulk_request.data,
                scheduled_for=bulk_request.scheduled_for
            )
            if notification:
                created_notifications.append(notification.id)
        except Exception as e:
            continue
    
    return {
        "message": f"Creadas {len(created_notifications)} notificaciones",
        "notification_ids": created_notifications
    }

@router.post("/test")
def send_test_notification(
    test_request: TestNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send test notification"""
    
    notification_service = NotificationService(db)
    
    title = "Test Notification - MechLink"
    message = f"This is a test notification sent on {datetime.now().strftime('%d/%m/%Y %H:%M')}. If you receive this message, the notification system is working correctly."
    
    # Use the current user's email if no other is provided
    recipient_email = test_request.recipient_email or current_user.email
    
    notification = notification_service.create_notification(
        user_id=current_user.id,
        notification_type=NotificationType.SYSTEM_UPDATE,
        channel=test_request.channel,
        title=title,
        message=message,
        data={"test_type": test_request.test_type}
    )
    
    return {"message": "Test notification sent", "notification_id": notification.id}

# === APPOINTMENT INTEGRATION ===

@router.post("/appointments/{appointment_id}/reminders")
def schedule_appointment_reminders(
    appointment_id: str,
    reminder_request: ReminderScheduleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Schedule reminders for an appointment"""
    
    notification_service = NotificationService(db)
    
    try:
        reminders = notification_service.schedule_appointment_reminders(appointment_id)
        
        return {
            "message": f"Scheduled {len(reminders)} reminders",
            "reminder_ids": [r.id for r in reminders]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/appointments/{appointment_id}/confirmation")
def send_appointment_confirmation(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send appointment confirmation"""
    
    notification_service = NotificationService(db)
    
    try:
        confirmation = notification_service.send_appointment_confirmation(appointment_id)
        
        return {
            "message": "Confirmation sent",
            "notification_id": confirmation.id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/appointments/{appointment_id}/review-request")
def send_review_request(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send review request"""
    
    notification_service = NotificationService(db)
    
    try:
        review_request = notification_service.send_review_request(appointment_id)
        
        return {
            "message": "Review request sent",
            "notification_id": review_request.id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# === MAINTENANCE REMINDERS ===

@router.post("/vehicles/{vehicle_id}/maintenance-reminder")
def send_maintenance_reminder(
    vehicle_id: str,
    reminder_type: str = Query(..., description="Type: 'mileage' or 'time'"),
    current_mileage: Optional[int] = Query(None, description="Current mileage"),
    last_service_date: Optional[str] = Query(None, description="Last service date (YYYY-MM-DD)"),
    service_type: str = Query("General inspection", description="Recommended service type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send maintenance reminder"""
    
    notification_service = NotificationService(db)
    
    details = {
        "service_type": service_type,
        "current_mileage": current_mileage,
        "last_service_date": last_service_date
    }
    
    if reminder_type == "time" and last_service_date:
        try:
            last_date = datetime.strptime(last_service_date, '%Y-%m-%d')
            days_since = (datetime.now() - last_date).days
            details["days_since"] = days_since
        except ValueError:
            pass
    
    try:
        reminder = notification_service.send_maintenance_reminder(
            vehicle_id=vehicle_id,
            reminder_type=reminder_type,
            details=details
        )
        
        return {
            "message": "Maintenance reminder sent",
            "notification_id": reminder.id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# === ADMIN ENDPOINTS ===

@router.get("/admin/stats", response_model=dict)
def get_admin_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve general statistics (admin)"""
    
    notification_service = NotificationService(db)
    stats = notification_service.get_notification_stats()
    
    return stats

@router.post("/admin/process-scheduled")
def process_scheduled_notifications(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process scheduled notifications (admin)"""
    
    notification_service = NotificationService(db)
    
    # Execute in background
    background_tasks.add_task(notification_service.process_scheduled_notifications)
    
    return {"message": "Scheduled notifications processing started"}

@router.post("/admin/retry-failed")
def retry_failed_notifications(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retry failed notifications (admin)"""
    
    notification_service = NotificationService(db)
    
    # Execute in background
    background_tasks.add_task(notification_service.retry_failed_notifications)
    
    return {"message": "Retry of failed notifications started"}

@router.delete("/admin/cleanup")
def cleanup_old_notifications(
    days_old: int = Query(90, ge=1, le=365, description="Days of age"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clean up old notifications (admin)"""
    
    notification_service = NotificationService(db)
    cleaned_count = notification_service.cleanup_old_notifications(days_old)
    
    return {"message": f"Deleted {cleaned_count} old notifications"}

# === TEMPLATE ENDPOINTS ===

@router.get("/templates", response_model=List[NotificationTemplateResponse])
def get_notification_templates(
    skip: int = 0,
    limit: int = 20,
    active_only: bool = Query(True, description="Only active templates"),
    db: Session = Depends(get_db)
):
    """Retrieve notification templates"""
    
    query = db.query(NotificationTemplate)
    
    if active_only:
        query = query.filter(NotificationTemplate.is_active == True)
    
    templates = query.offset(skip).limit(limit).all()
    return templates

@router.post("/templates", response_model=NotificationTemplateResponse)
def create_notification_template(
    template_data: NotificationTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create notification template"""
    template = NotificationTemplate(**template_data.dict())
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return template