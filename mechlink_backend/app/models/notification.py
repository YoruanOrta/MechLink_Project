from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.config.database import Base

class NotificationType(enum.Enum):
    """Notification types"""
    APPOINTMENT_REMINDER = "appointment_reminder"
    MAINTENANCE_REMINDER = "maintenance_reminder"
    APPOINTMENT_CONFIRMATION = "appointment_confirmation"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    APPOINTMENT_COMPLETED = "appointment_completed"
    REVIEW_REQUEST = "review_request"
    SYSTEM_UPDATE = "SYSTEM_UPDATE"
    PROMOTIONAL = "promotional"
    WORKSHOP_UPDATE = "workshop_update"

class NotificationStatus(enum.Enum):
    """Notification statuses"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"

class NotificationChannel(enum.Enum):
    """Notification channels"""
    email = "email"
    push = "push"
    sms = "sms"
    in_app = "in_app"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Type and channel
    type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    
    # Content
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)  # Additional data specific to the type
    
    # Recipient information
    recipient_email = Column(String(100), nullable=True)
    recipient_phone = Column(String(20), nullable=True)
    recipient_device_token = Column(String(500), nullable=True)
    
    # Relationships (optional - for tracking)
    appointment_id = Column(String, ForeignKey("appointments.id"), nullable=True)
    workshop_id = Column(String, ForeignKey("workshops.id"), nullable=True)
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=True)
    
    # Scheduling
    scheduled_for = Column(DateTime, nullable=True)  # When to send
    sent_at = Column(DateTime, nullable=True)  # When it was sent
    delivered_at = Column(DateTime, nullable=True)  # When it was delivered
    read_at = Column(DateTime, nullable=True)  # When it was read
    
    # Attempts and errors
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    last_error = Column(Text, nullable=True)
    
    # Metadata
    priority = Column(String(10), default="normal")  # low, normal, high, urgent
    expires_at = Column(DateTime, nullable=True)  # When the notification expires
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    appointment = relationship("Appointment")
    workshop = relationship("Workshop")
    vehicle = relationship("Vehicle")
    
    def __repr__(self):
        return f"<Notification(type='{self.type}', user='{self.user_id}', status='{self.status}')>"

class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identification
    name = Column(String(100), nullable=False, unique=True)
    type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    
    # Template content
    subject_template = Column(String(200), nullable=False)  # For email
    message_template = Column(Text, nullable=False)
    html_template = Column(Text, nullable=True)  # For HTML emails
    
    # Available variables
    available_variables = Column(JSON, nullable=True)  # List of accepted variables
    
    # Configuration
    is_active = Column(Boolean, default=True)
    default_priority = Column(String(10), default="normal")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<NotificationTemplate(name='{self.name}', type='{self.type}')>"

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Preferences by type
    appointment_reminders = Column(Boolean, default=True)
    maintenance_reminders = Column(Boolean, default=True)
    appointment_confirmations = Column(Boolean, default=True)
    review_requests = Column(Boolean, default=True)
    system_updates = Column(Boolean, default=True)
    promotional = Column(Boolean, default=False)
    
    # Preferences by channel
    email_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    
    # Preferred hours
    quiet_hours_start = Column(String(5), default="22:00")  # HH:MM
    quiet_hours_end = Column(String(5), default="08:00")   # HH:MM
    timezone = Column(String(50), default="America/Puerto_Rico")
    
    # Frequency
    reminder_hours_before = Column(Integer, default=24)  # Hours before appointment
    maintenance_reminder_days = Column(Integer, default=30)  # Days before maintenance
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<NotificationPreference(user='{self.user_id}')>"