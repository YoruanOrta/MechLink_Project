from sqlalchemy import Column, String, Integer, DateTime, Text, Numeric, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.config.database import Base

class Workshop(Base):
    __tablename__ = "workshops"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String(200), nullable=False)
    city = Column(String(50), nullable=False)
    state = Column(String(50), nullable=True)
    postal_code = Column(String(10), nullable=True)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    
    # Geographic location
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    
    # Business information
    services = Column(JSON, nullable=True)
    specialties = Column(JSON, nullable=True)
    working_hours = Column(JSON, nullable=True)
    
    # Ratings
    rating_average = Column(Numeric(3, 2), default=0.0)
    total_reviews = Column(Integer, default=0)
    
    # Additional information
    images = Column(JSON, nullable=True)
    certifications = Column(JSON, nullable=True)
    years_in_business = Column(Integer, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Workshop(name='{self.name}', city='{self.city}')>"

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=False)
    workshop_id = Column(String, ForeignKey("workshops.id"), nullable=False)
    
    # Appointment Information
    service_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    appointment_datetime = Column(DateTime, nullable=False)
    estimated_duration = Column(Integer, nullable=True)
    
    # Costs
    estimated_cost = Column(Numeric(10, 2), nullable=True)
    actual_cost = Column(Numeric(10, 2), nullable=True)
    
    # Status
    status = Column(String(20), default="pending")
    
    # Notes
    customer_notes = Column(Text, nullable=True)
    workshop_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workshop = relationship("Workshop")
    user = relationship("User")
    vehicle = relationship("Vehicle")
    
    def __repr__(self):
        return f"<Appointment(workshop='{self.workshop_id}', service='{self.service_type}', status='{self.status}')>"

class WorkshopReview(Base):
    __tablename__ = "workshop_reviews"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    workshop_id = Column(String, ForeignKey("workshops.id"), nullable=False)
    appointment_id = Column(String, ForeignKey("appointments.id"), nullable=True)
    
    # Rating
    rating = Column(Integer, nullable=False)
    title = Column(String(100), nullable=True)
    comment = Column(Text, nullable=True)
    
    # Specific ratings
    service_quality = Column(Integer, nullable=True)
    price_fairness = Column(Integer, nullable=True)
    timeliness = Column(Integer, nullable=True)
    communication = Column(Integer, nullable=True)
    
    # Additional information
    would_recommend = Column(Boolean, nullable=True)
    images = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workshop = relationship("Workshop")
    user = relationship("User")
    appointment = relationship("Appointment")
    
    def __repr__(self):
        return f"<WorkshopReview(workshop='{self.workshop_id}', rating={self.rating})>"