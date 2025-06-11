from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from pydantic import BaseModel

from app.config.database import get_db
from app.models.workshop import Workshop, WorkshopReview
from app.models.user import User
from app.schemas.workshop_schemas import (
    WorkshopCreate, WorkshopResponse, WorkshopUpdate,
    WorkshopReviewCreate, WorkshopReviewResponse, WorkshopReviewWithUser,
    WorkshopStats
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/workshops", tags=["workshops"])

# === OPTIMIZED SCHEMAS FOR MAPS ===

class WorkshopMapMarker(BaseModel):
    """Minimal data for map markers"""
    id: str
    name: str
    latitude: float
    longitude: float
    rating: float = 0.0
    total_reviews: int = 0
    services_count: int = 0
    is_open: Optional[bool] = None
    city: str
    phone: Optional[str] = None
    # Marker color based on rating
    marker_color: str = "blue"  # blue, green, yellow, red
    
class MapBounds(BaseModel):
    """Bounds of the visible map area"""

    north: float  # 18.5
    south: float  # 18.1  
    east: float   # -65.6
    west: float   # -67.2

class WorkshopMapResponse(BaseModel):
    """Optimized response for maps"""
    workshops: List[WorkshopMapMarker]
    total_in_area: int
    bounds_used: Optional[MapBounds] = None
    filters_applied: dict = {}

# === SPECIFIC ENDPOINTS (SHOULD COME FIRST) ===

@router.get("/map-config")
def get_map_configuration():
    """Configuration and useful data for Puerto Rico maps"""
    
    return {
        "puerto_rico_bounds": {
            "north": 18.5208,
            "south": 17.8813,
            "east": -65.2210,
            "west": -67.9566
        },
        "default_center": {
            "latitude": 18.2208,  # Approximate center of PR
            "longitude": -66.5901
        },
        "recommended_zoom": {
            "island_view": 9,      # View the entire island
            "city_view": 12,       # View a city
            "street_view": 15      # View streets
        },
        "major_cities": [
            {"name": "San Juan", "lat": 18.4655, "lng": -66.1057},
            {"name": "Bayamón", "lat": 18.3833, "lng": -66.1500},
            {"name": "Carolina", "lat": 18.3833, "lng": -65.9500},
            {"name": "Ponce", "lat": 18.0175, "lng": -66.6140},
            {"name": "Caguas", "lat": 18.2342, "lng": -66.0356},
            {"name": "Arecibo", "lat": 18.4739, "lng": -66.7206}
        ],
        "marker_colors": {
            "green": "Excellent (4.5+ stars)",
            "blue": "Very good (4.0+ stars)", 
            "yellow": "Good (3.0+ stars)",
            "red": "Fair (less than 3.0)",
            "gray": "No reviews"
        }
        }

@router.get("/for-map", response_model=WorkshopMapResponse)
def get_workshops_for_map(
    # Geographic filters
    bounds: Optional[str] = Query(None, description="Map bounds: 'north,south,east,west'"),
    center_lat: Optional[float] = Query(None, description="Center latitude"),
    center_lng: Optional[float] = Query(None, description="Center longitude"),
    radius_km: Optional[float] = Query(20.0, ge=1, le=100, description="Radius in kilometers"),
    
    # Service filters
    service: Optional[str] = Query(None, description="Specific service type"),
    services: Optional[str] = Query(None, description="Comma-separated services"),
    specialty: Optional[str] = Query(None, description="Workshop specialty"),
    
    # Quality filters
    min_rating: Optional[float] = Query(None, ge=1, le=5, description="Minimum rating"),
    min_reviews: Optional[int] = Query(None, ge=0, description="Minimum number of reviews"),
    verified_only: bool = Query(False, description="Only verified workshops"),
    
    # Operational filters
    city: Optional[str] = Query(None, description="Specific city"),
    open_now: Optional[bool] = Query(None, description="Only workshops open now"),
    
    # Pagination and limits
    limit: int = Query(100, ge=1, le=200, description="Maximum number of markers"),
    
    db: Session = Depends(get_db)
):
    """
    Optimized endpoint to display workshops on maps.
    Returns only essential information for markers.
    """
    
    import json
    
    # Base query
    query = db.query(Workshop).filter(Workshop.is_active == True)
    
    # === GEOGRAPHIC FILTERS ===
    
    # Option 1: Use bounds (rectangular area of the visible map)
    if bounds:
        try:
            coords = bounds.split(',')
            if len(coords) == 4:
                north, south, east, west = map(float, coords)
                query = query.filter(
                    and_(
                        Workshop.latitude >= south,
                        Workshop.latitude <= north,
                        Workshop.longitude >= west,
                        Workshop.longitude <= east
                    )
                )
                bounds_used = MapBounds(north=north, south=south, east=east, west=west)
            else:
                bounds_used = None
        except:
            bounds_used = None
    
    # Option 2: Use center + radius (circular search)
    elif center_lat and center_lng and radius_km:
        # Approximate calculation of degrees per km in Puerto Rico
        lat_km = 1/111.0  # 1 degree ≈ 111 km
        lng_km = 1/(111.0 * 0.87)  # Adjustment for PR's latitude
        
        lat_delta = radius_km * lat_km
        lng_delta = radius_km * lng_km
        
        query = query.filter(
            and_(
                Workshop.latitude >= center_lat - lat_delta,
                Workshop.latitude <= center_lat + lat_delta,
                Workshop.longitude >= center_lng - lng_delta,
                Workshop.longitude <= center_lng + lng_delta
            )
        )
        bounds_used = None
    else:
        bounds_used = None
    
    # === SERVICE FILTERS ===
    
    if service:
        # Search in specialties (as a string or list)
        query = query.filter(
            or_(
                Workshop.specialties.like(f'%"{service}"%'),
                Workshop.specialties.like(f'%{service}%')
            )
        )
    
    if services:
        # Multiple services separated by commas
        service_list = [s.strip() for s in services.split(',')]
        service_conditions = []
        for srv in service_list:
            service_conditions.extend([
                Workshop.specialties.like(f'%"{srv}"%'),
                Workshop.specialties.like(f'%{srv}%')
            ])
        if service_conditions:
            query = query.filter(or_(*service_conditions))
    
    if specialty:
        query = query.filter(
            or_(
                Workshop.specialties.like(f'%"{specialty}"%'),
                Workshop.specialties.like(f'%{specialty}%')
            )
        )
    
    # === QUALITY FILTERS ===
    
    if min_rating:
        query = query.filter(Workshop.rating_average >= min_rating)
    
    if min_reviews:
        query = query.filter(Workshop.total_reviews >= min_reviews)
    
    if verified_only:
        query = query.filter(Workshop.is_verified == True)
    
    # === LOCATION FILTERS ===
    
    if city:
        query = query.filter(Workshop.city.ilike(f"%{city}%"))
    
    # === EXECUTE QUERY ===
    
    workshops = query.limit(limit).all()
    
    # === CONVERT TO MAP FORMAT ===
    
    def get_marker_color(rating: float, reviews: int) -> str:
        """Determine marker color based on quality"""
        if reviews == 0:
            return "gray"
        elif rating >= 4.5:
            return "green"
        elif rating >= 4.0:
            return "blue"
        elif rating >= 3.0:
            return "yellow"
        else:
            return "red"
    
    map_markers = []
    for workshop in workshops:
        # Count services
        services_count = 0
        if workshop.specialties:
            try:
                if isinstance(workshop.specialties, str):
                    specialties = json.loads(workshop.specialties)
                else:
                    specialties = workshop.specialties
                services_count += len(specialties) if specialties else 0
            except:
                # If not valid JSON, count as 1 service
                services_count = 1
        
        # Determine if open (simplified logic)
        is_open = None
        if open_now is not None:
            # Basic business hours: 8 AM - 6 PM
            current_hour = datetime.now().hour
            is_open = 8 <= current_hour <= 18
        
        marker = WorkshopMapMarker(
            id=workshop.id,
            name=workshop.name,
            latitude=float(workshop.latitude),
            longitude=float(workshop.longitude),
            rating=float(workshop.rating_average or 0),
            total_reviews=workshop.total_reviews or 0,
            services_count=services_count,
            is_open=is_open,
            city=workshop.city,
            phone=workshop.phone,
            marker_color=get_marker_color(
                float(workshop.rating_average or 0), 
                workshop.total_reviews or 0
            )
        )
        map_markers.append(marker)
    
    # === PREPARE RESPONSE ===
    
    filters_applied = {}
    if service: filters_applied["service"] = service
    if services: filters_applied["services"] = services.split(',')
    if city: filters_applied["city"] = city
    if min_rating: filters_applied["min_rating"] = min_rating
    if verified_only: filters_applied["verified_only"] = True
    
    return WorkshopMapResponse(
        workshops=map_markers,
        total_in_area=len(map_markers),
        bounds_used=bounds_used,
        filters_applied=filters_applied
    )

# === GENERAL WORKSHOP ENDPOINTS ===

@router.post("/", response_model=WorkshopResponse, status_code=status.HTTP_201_CREATED)
def create_workshop(
    workshop_data: WorkshopCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new workshop"""
    
    # Check if a workshop with the same name and city already exists
    existing_workshop = db.query(Workshop).filter(
        and_(
            Workshop.name == workshop_data.name,
            Workshop.city == workshop_data.city
        )
    ).first()
    
    if existing_workshop:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workshop with this name already exists in this city"
        )
    
    # Create workshop
    db_workshop = Workshop(**workshop_data.dict())
    db.add(db_workshop)
    db.commit()
    db.refresh(db_workshop)
    
    return db_workshop

@router.get("/", response_model=List[WorkshopResponse])
def get_workshops(
    skip: int = 0,
    limit: int = 20,
    city: Optional[str] = Query(None, description="Filter by city"),
    service: Optional[str] = Query(None, description="Filter by service"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    verified_only: bool = Query(False, description="Only verified workshops"),
    db: Session = Depends(get_db)
):
    """Get a list of workshops with filters"""
    
    query = db.query(Workshop).filter(Workshop.is_active == True)
    
    # Apply filters
    if city:
        query = query.filter(Workshop.city.ilike(f"%{city}%"))
    
    if min_rating is not None:
        query = query.filter(Workshop.rating_average >= min_rating)
    
    if verified_only:
        query = query.filter(Workshop.is_verified == True)
    
    # Order by rating
    workshops = query.order_by(
        desc(Workshop.rating_average),
        desc(Workshop.total_reviews)
    ).offset(skip).limit(limit).all()
    
    return workshops

# === ENDPOINTS WITH PARAMETERS (SHOULD GO LAST) ===

@router.get("/{workshop_id}", response_model=WorkshopResponse)
def get_workshop(workshop_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a workshop"""
    
    workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
    if not workshop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workshop not found"
        )
    
    return workshop

@router.put("/{workshop_id}", response_model=WorkshopResponse)
def update_workshop(
    workshop_id: str,
    workshop_data: WorkshopUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update workshop information"""
    
    workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
    if not workshop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workshop not found"
        )
    
    # Update fields
    update_data = workshop_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workshop, field, value)
    
    db.commit()
    db.refresh(workshop)
    
    return workshop

@router.get("/{workshop_id}/reviews", response_model=List[WorkshopReviewWithUser])
def get_workshop_reviews(
    workshop_id: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get reviews for a workshop"""
    
    workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
    if not workshop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workshop not found"
        )
    
    reviews = db.query(WorkshopReview).filter(
        WorkshopReview.workshop_id == workshop_id
    ).order_by(desc(WorkshopReview.created_at)).offset(skip).limit(limit).all()
    
    # Add user information to each review
    reviews_with_user = []
    for review in reviews:
        user = db.query(User).filter(User.id == review.user_id).first()
        review_dict = {
            **review.__dict__,
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }
        reviews_with_user.append(review_dict)
    
    return reviews_with_user

@router.get("/{workshop_id}/stats", response_model=WorkshopStats)
def get_workshop_stats(
    workshop_id: str,
    db: Session = Depends(get_db)
):
    """Get workshop statistics"""
    
    workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
    if not workshop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workshop not found"
        )
    
    # Here you can add logic to calculate statistics
    # For now, we return basic data
    return {
        "total_workshops": 1,
        "average_rating": workshop.rating_average,
        "total_appointments": 0,
        "popular_services": [],
        "top_rated_workshops": []
    }

# === REVIEW ENDPOINTS ===

@router.post("/reviews", response_model=WorkshopReviewResponse, status_code=status.HTTP_201_CREATED)
def create_workshop_review(
    review_data: WorkshopReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a workshop review"""
    
    # Verify that the workshop exists
    workshop = db.query(Workshop).filter(Workshop.id == review_data.workshop_id).first()
    if not workshop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workshop not found"
        )
    
    # Create review
    db_review = WorkshopReview(
        **review_data.dict(),
        user_id=current_user.id
    )
    
    db.add(db_review)
    
    # Update workshop's average rating
    reviews = db.query(WorkshopReview).filter(WorkshopReview.workshop_id == review_data.workshop_id).all()
    total_reviews = len(reviews) + 1
    total_rating = sum(review.rating for review in reviews) + review_data.rating
    new_average = total_rating / total_reviews
    
    workshop.rating_average = round(new_average, 2)
    workshop.total_reviews = total_reviews
    
    db.commit()
    db.refresh(db_review)
    
    return db_review