from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Base schema for Vehicle
class VehicleBase(BaseModel):
    make: str = Field(..., min_length=1, max_length=50, description="Vehicle make")
    model: str = Field(..., min_length=1, max_length=50, description="Vehicle model")
    year: int = Field(..., ge=1900, le=2030, description="Vehicle year")
    license_plate: str = Field(..., min_length=1, max_length=20, description="License plate")
    color: Optional[str] = Field(None, max_length=30, description="Vehicle color")
    current_mileage: Optional[int] = Field(0, ge=0, description="Current mileage")
    fuel_type: Optional[str] = Field(None, max_length=20, description="Fuel type")
    transmission: Optional[str] = Field(None, max_length=20, description="Transmission type")
    engine_size: Optional[str] = Field(None, max_length=10, description="Engine size")
    vin: Optional[str] = Field(None, min_length=17, max_length=17, description="VIN number")
    notes: Optional[str] = Field(None, description="Additional notes")

# Schema to create vehicle
class VehicleCreate(VehicleBase):
    user_id: str = Field(..., description="Owner ID")

# Schema to update vehicle
class VehicleUpdate(BaseModel):
    make: Optional[str] = Field(None, min_length=1, max_length=50)
    model: Optional[str] = Field(None, min_length=1, max_length=50)
    year: Optional[int] = Field(None, ge=1900, le=2030)
    license_plate: Optional[str] = Field(None, min_length=1, max_length=20)
    color: Optional[str] = Field(None, max_length=30)
    current_mileage: Optional[int] = Field(None, ge=0)
    fuel_type: Optional[str] = Field(None, max_length=20)
    transmission: Optional[str] = Field(None, max_length=20)
    engine_size: Optional[str] = Field(None, max_length=10)
    vin: Optional[str] = Field(None, min_length=17, max_length=17)
    image: Optional[str] = Field(None, description="Image URL")
    notes: Optional[str] = Field(None, description="Additional notes")

# Schema for response
class VehicleResponse(VehicleBase):
    id: str
    user_id: str
    image: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schema for response with user information
class VehicleWithOwner(VehicleResponse):
    owner: dict = Field(..., description="Owner information")