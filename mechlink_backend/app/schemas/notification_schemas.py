from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

# === ENUMS ===

class NotificationTypeEnum(str, Enum):
    APPOINTMENT_REMINDER = "appointment_reminder"
    MAINTENANCE_REMINDER = "maintenance_reminder"
    APPOINTMENT_CONFIRMATION = "appointment_confirmation"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    APPOINTMENT_COMPLETED = "appointment_completed"
    REVIEW_REQUEST = "review_request"
    SYSTEM_UPDATE = "SYSTEM_UPDATE"
    PROMOTIONAL = "promotional"
    WORKSHOP_UPDATE = "workshop_update"

class NotificationStatusEnum(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"

class NotificationChannelEnum(str, Enum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"

class PriorityEnum(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

# === NOTIFICATION SCHEMAS ===

class NotificationBase(BaseModel):
    type: NotificationTypeEnum
    channel: NotificationChannelEnum
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    data: Optional[Dict[str, Any]] = None
    priority: PriorityEnum = PriorityEnum.NORMAL
    scheduled_for: Optional[datetime] = None

class NotificationCreate(NotificationBase):
    user_id: str
    recipient_email: Optional[EmailStr] = None
    recipient_phone: Optional[str] = None
    appointment_id: Optional[str] = None
    workshop_id: Optional[str] = None
    vehicle_id: Optional[str] = None
    expires_at: Optional[datetime] = None

class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatusEnum] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    last_error: Optional[str] = None

class NotificationResponse(NotificationBase):
    id: str
    user_id: str
    status: NotificationStatusEnum
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    appointment_id: Optional[str] = None
    workshop_id: Optional[str] = None
    vehicle_id: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    attempts: int
    max_attempts: int
    last_error: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# === TEMPLATE SCHEMAS ===

class NotificationTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: NotificationTypeEnum
    channel: NotificationChannelEnum
    subject_template: str = Field(..., min_length=1, max_length=200)
    message_template: str = Field(..., min_length=1)
    html_template: Optional[str] = None
    available_variables: Optional[List[str]] = []
    default_priority: PriorityEnum = PriorityEnum.NORMAL

class NotificationTemplateCreate(NotificationTemplateBase):
    pass

class NotificationTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    subject_template: Optional[str] = Field(None, min_length=1, max_length=200)
    message_template: Optional[str] = Field(None, min_length=1)
    html_template: Optional[str] = None
    available_variables: Optional[List[str]] = None
    is_active: Optional[bool] = None
    default_priority: Optional[PriorityEnum] = None

class NotificationTemplateResponse(NotificationTemplateBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# === PREFERENCE SCHEMAS ===

class NotificationPreferenceBase(BaseModel):
    appointment_reminders: bool = True
    maintenance_reminders: bool = True
    appointment_confirmations: bool = True
    review_requests: bool = True
    system_updates: bool = True
    promotional: bool = False
    email_enabled: bool = True
    push_enabled: bool = True
    sms_enabled: bool = False
    quiet_hours_start: str = Field("22:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    quiet_hours_end: str = Field("08:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    timezone: str = "America/Puerto_Rico"
    reminder_hours_before: int = Field(24, ge=1, le=168)  # 1 hour to 1 hour
    maintenance_reminder_days: int = Field(30, ge=1, le=365)  # 1 day to 1 yer

class NotificationPreferenceCreate(NotificationPreferenceBase):
    pass

class NotificationPreferenceUpdate(BaseModel):
    appointment_reminders: Optional[bool] = None
    maintenance_reminders: Optional[bool] = None
    appointment_confirmations: Optional[bool] = None
    review_requests: Optional[bool] = None
    system_updates: Optional[bool] = None
    promotional: Optional[bool] = None
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    quiet_hours_end: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    timezone: Optional[str] = None
    reminder_hours_before: Optional[int] = Field(None, ge=1, le=168)
    maintenance_reminder_days: Optional[int] = Field(None, ge=1, le=365)

class NotificationPreferenceResponse(NotificationPreferenceBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# === BULK AND UTILITY SCHEMAS ===

class BulkNotificationCreate(BaseModel):
    user_ids: List[str] = Field(..., min_items=1)
    type: NotificationTypeEnum
    channel: NotificationChannelEnum
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    data: Optional[Dict[str, Any]] = None
    priority: PriorityEnum = PriorityEnum.NORMAL
    scheduled_for: Optional[datetime] = None

class NotificationStats(BaseModel):
    total_notifications: int
    sent_today: int
    pending: int
    failed: int
    delivered_rate: float
    notifications_by_type: Dict[str, int]
    notifications_by_channel: Dict[str, int]

class SendNotificationRequest(BaseModel):
    """Request to send immediate notification"""
    user_id: str
    type: NotificationTypeEnum
    title: str
    message: str
    channel: NotificationChannelEnum = NotificationChannelEnum.EMAIL
    data: Optional[Dict[str, Any]] = None
    priority: PriorityEnum = PriorityEnum.NORMAL

class ReminderScheduleRequest(BaseModel):
    """Request to schedule reminders"""
    appointment_id: str
    reminder_hours: List[int] = [24, 1]  # 24 hours and 1 hour before
    
class TestNotificationRequest(BaseModel):
    """Request to send test notification"""
    channel: NotificationChannelEnum
    recipient_email: Optional[EmailStr] = None
    recipient_phone: Optional[str] = None
    test_type: str = "system_test"