from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.config.database import get_db
from app.models.vehicle import Vehicle
from app.models.user import User
from app.schemas.vehicle_schemas import VehicleCreate, VehicleResponse, VehicleUpdate, VehicleWithOwner
from app.api.deps import get_current_user

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle_data: VehicleCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new vehicle (requires authentication)"""
    
    # The user can only create vehicles for themselves
    if vehicle_data.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create vehicles for yourself"
        )
    
    # Verify that the license plate does not already exist
    existing_vehicle = db.query(Vehicle).filter(Vehicle.license_plate == vehicle_data.license_plate).first()
    if existing_vehicle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="License plate already registered"
        )
    
    # Create vehicle
    db_vehicle = Vehicle(**vehicle_data.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    
    return db_vehicle

@router.get("/", response_model=List[VehicleResponse])
def get_vehicles(
    skip: int = 0, 
    limit: int = 10,
    make: Optional[str] = Query(None, description="Filter by make"),
    model: Optional[str] = Query(None, description="Filter by model"),
    year: Optional[int] = Query(None, description="Filter by year"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve vehicles of the authenticated user"""
    
    query = db.query(Vehicle).filter(
        Vehicle.is_active == True,
        Vehicle.user_id == current_user.id  # Only vehicles of the current user
    )
    
    # Apply filters
    if make:
        query = query.filter(Vehicle.make.ilike(f"%{make}%"))
    if model:
        query = query.filter(Vehicle.model.ilike(f"%{model}%"))
    if year:
        query = query.filter(Vehicle.year == year)
    
    vehicles = query.offset(skip).limit(limit).all()
    return vehicles

@router.get("/my-vehicles", response_model=List[VehicleResponse])
def get_my_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all vehicles of the authenticated user"""
    
    vehicles = db.query(Vehicle).filter(
        Vehicle.user_id == current_user.id,
        Vehicle.is_active == True
    ).all()
    
    return vehicles

@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve a specific vehicle of the authenticated user"""
    
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.user_id == current_user.id  # Only vehicles of the current user
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    return vehicle

@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: str, 
    vehicle_update: VehicleUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update vehicle of the authenticated user"""
    
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Update fields
    for field, value in vehicle_update.dict(exclude_unset=True).items():
        setattr(vehicle, field, value)
    
    db.commit()
    db.refresh(vehicle)
    return vehicle

@router.delete("/{vehicle_id}")
def delete_vehicle(
    vehicle_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete vehicle of the authenticated user"""
    
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    vehicle.is_active = False
    db.commit()
    
    return {"message": "Vehicle deleted successfully"}