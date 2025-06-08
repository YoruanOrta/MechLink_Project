from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

# Base schema for MaintenanceRecord
class MaintenanceRecordBase(BaseModel):
    service_type: str = Field(..., min_length=1, max_length=100, description="Type of service")
    description: Optional[str] = Field(None, description="Detailed description")
    cost: Optional[Decimal] = Field(None, ge=0, description="Service cost")
    mileage_at_service: int = Field(..., ge=0, description="Mileage at the time of service")
    service_date: date = Field(..., description="Date of service")
    next_service_due: Optional[date] = Field(None, description="Next recommended service")
    next_mileage_due: Optional[int] = Field(None, ge=0, description="Next mileage for service")
    notes: Optional[str] = Field(None, description="Additional notes")

# Schema to create maintenance record
class MaintenanceRecordCreate(MaintenanceRecordBase):
    vehicle_id: str = Field(..., description="ID of the vehicle")
    workshop_name: Optional[str] = Field(None, max_length=100, description="Workshop name (optional)")

# Schema to update record
class MaintenanceRecordUpdate(BaseModel):
    service_type: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    cost: Optional[Decimal] = Field(None, ge=0)
    mileage_at_service: Optional[int] = Field(None, ge=0)
    service_date: Optional[date] = None
    next_service_due: Optional[date] = None
    next_mileage_due: Optional[int] = Field(None, ge=0)
    workshop_name: Optional[str] = Field(None, max_length=100)
    receipt_image: Optional[str] = None
    notes: Optional[str] = None

# Schema for response
class MaintenanceRecordResponse(MaintenanceRecordBase):
    id: str
    vehicle_id: str
    workshop_name: Optional[str] = None
    receipt_image: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schema with vehicle information
class MaintenanceRecordWithVehicle(MaintenanceRecordResponse):
    vehicle: dict = Field(..., description="Vehicle information")

# Schema for reminders
class MaintenanceReminderBase(BaseModel):
    reminder_type: str = Field(..., description="Tipo: 'time_based', 'mileage_based', 'both'")
    service_type: str = Field(..., min_length=1, max_length=100, description="Type of service")
    due_date: Optional[date] = Field(None, description="Deadline")
    due_mileage: Optional[int] = Field(None, ge=0, description="Mileage limit")

class MaintenanceReminderCreate(MaintenanceReminderBase):
    vehicle_id: str = Field(..., description="ID of the vehicle")

class MaintenanceReminderResponse(MaintenanceReminderBase):
    id: str
    vehicle_id: str
    user_id: str
    is_active: bool
    last_notified: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schema for reports
class MaintenanceReport(BaseModel):
    vehicle_id: str
    vehicle_info: dict
    total_records: int
    total_cost: Decimal
    last_service_date: Optional[date]
    next_service_due: Optional[date]
    average_cost_per_service: Decimal
    services_by_type: dict
    
class MaintenanceStats(BaseModel):
    total_vehicles: int
    total_maintenance_records: int
    total_spent: Decimal
    most_common_service: str
    average_mileage_between_services: int