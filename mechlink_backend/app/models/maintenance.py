from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Numeric, Date, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.config.database import Base

class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=False)
    workshop_name = Column(String(100), nullable=True)  # Workshop name as text
    service_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    cost = Column(Numeric(10, 2), nullable=True)
    mileage_at_service = Column(Integer, nullable=False)
    service_date = Column(Date, nullable=False)
    next_service_due = Column(Date, nullable=True)
    next_mileage_due = Column(Integer, nullable=True)
    receipt_image = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="maintenance_records")
    
    def __repr__(self):
        return f"<MaintenanceRecord(vehicle_id='{self.vehicle_id}', service='{self.service_type}', date='{self.service_date}')>"

class MaintenanceReminder(Base):
    __tablename__ = "maintenance_reminders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    reminder_type = Column(String(20), nullable=False)
    service_type = Column(String(100), nullable=False)
    due_date = Column(Date, nullable=True)
    due_mileage = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    last_notified = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    vehicle = relationship("Vehicle")
    user = relationship("User")
    
    def __repr__(self):
        return f"<MaintenanceReminder(vehicle_id='{self.vehicle_id}', service='{self.service_type}')>"