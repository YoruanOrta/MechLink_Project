from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.config.database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    make = Column(String(50), nullable=False)  # brand (Toyota, Honda, etc.)
    model = Column(String(50), nullable=False)  # Model (Corolla, Civic, etc.)
    year = Column(Integer, nullable=False)
    license_plate = Column(String(20), nullable=False, unique=True)
    color = Column(String(30), nullable=True)
    current_mileage = Column(Integer, default=0)
    fuel_type = Column(String(20), nullable=True)  # Gasoline, Diesel, Hybrid, Electric
    transmission = Column(String(20), nullable=True)  # Manual, Automatic
    engine_size = Column(String(10), nullable=True)  # 1.6L, 2.0L, etc.
    vin = Column(String(17), nullable=True, unique=True)  # Vehicle Identification Number
    image = Column(String, nullable=True)  # Image URL
    notes = Column(Text, nullable=True)  # Additional notes
    is_active = Column(String, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="vehicles")
    maintenance_records = relationship("MaintenanceRecord", back_populates="vehicle")
    
    def __repr__(self):
        return f"<Vehicle(make='{self.make}', model='{self.model}', year={self.year}, plate='{self.license_plate}')>"