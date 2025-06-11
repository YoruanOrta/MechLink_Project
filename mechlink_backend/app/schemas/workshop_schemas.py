from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum

# === WORKSHOP SCHEMAS ===

class WorkshopBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    address: str = Field(..., min_length=5, max_length=200)
    city: str = Field(..., min_length=1, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=10)
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    website: Optional[str] = None

class WorkshopCreate(WorkshopBase):
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    services: Optional[List[str]] = []
    specialties: Optional[List[str]] = []
    working_hours: Optional[Dict] = {}
    years_in_business: Optional[int] = Field(None, ge=0, le=100)

class WorkshopUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    address: Optional[str] = Field(None, min_length=5, max_length=200)
    city: Optional[str] = Field(None, min_length=1, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=10)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    services: Optional[List[str]] = None
    specialties: Optional[List[str]] = None
    working_hours: Optional[Dict] = None
    images: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    years_in_business: Optional[int] = Field(None, ge=0, le=100)

class WorkshopResponse(WorkshopBase):
    id: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    services: Optional[List[str]] = []
    specialties: Optional[List[str]] = []
    working_hours: Optional[Dict] = {}
    rating_average: Decimal
    total_reviews: int
    images: Optional[List[str]] = []
    certifications: Optional[List[str]] = []
    years_in_business: Optional[int] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class WorkshopSearch(BaseModel):
    city: Optional[str] = None
    services: Optional[List[str]] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = Field(None, ge=0, le=100)

# === APPOINTMENT SCHEMAS ===

class AppointmentBase(BaseModel):
    service_type: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    appointment_datetime: datetime
    estimated_duration: Optional[int] = Field(None, ge=15, le=480)
    customer_notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    vehicle_id: str
    workshop_id: str

class AppointmentUpdate(BaseModel):
    service_type: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    appointment_datetime: Optional[datetime] = None
    estimated_duration: Optional[int] = Field(None, ge=15, le=480)
    status: Optional[str] = Field(None, pattern="^(pending|confirmed|in_progress|completed|cancelled)$")
    estimated_cost: Optional[Decimal] = Field(None, ge=0)
    actual_cost: Optional[Decimal] = Field(None, ge=0)
    customer_notes: Optional[str] = None
    workshop_notes: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: str
    user_id: str
    vehicle_id: str
    workshop_id: str
    estimated_cost: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    status: str
    workshop_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AppointmentWithDetails(AppointmentResponse):
    workshop: Dict
    vehicle: Dict

# === REVIEW SCHEMAS ===

class WorkshopReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=100)
    comment: Optional[str] = None
    service_quality: Optional[int] = Field(None, ge=1, le=5)
    price_fairness: Optional[int] = Field(None, ge=1, le=5)
    timeliness: Optional[int] = Field(None, ge=1, le=5)
    communication: Optional[int] = Field(None, ge=1, le=5)
    would_recommend: Optional[bool] = None

class WorkshopReviewCreate(WorkshopReviewBase):
    workshop_id: str
    appointment_id: Optional[str] = None

class WorkshopReviewResponse(WorkshopReviewBase):
    id: str
    user_id: str
    workshop_id: str
    appointment_id: Optional[str] = None
    images: Optional[List[str]] = []
    created_at: datetime
    
    class Config:
        from_attributes = True

class WorkshopReviewWithUser(WorkshopReviewResponse):
    user: Dict

# === AVAILABILITY SCHEMAS ===

class WorkshopAvailabilityCreate(BaseModel):
    date: date
    start_time: datetime
    end_time: datetime
    max_appointments: int = Field(1, ge=1, le=10)
    service_types: Optional[List[str]] = []
    notes: Optional[str] = None

class WorkshopAvailabilityResponse(BaseModel):
    id: str
    workshop_id: str
    date: date
    start_time: datetime
    end_time: datetime
    is_available: bool
    max_appointments: int
    service_types: Optional[List[str]] = []
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# === SUMMARY SCHEMAS ===

class WorkshopStats(BaseModel):
    total_workshops: int
    average_rating: Decimal
    total_appointments: int
    popular_services: List[Dict]
    top_rated_workshops: List[Dict]

# === GEOGRAPHIC SEARCH SCHEMAS ===


class GeographicSearch(BaseModel):
    """Geographic search for workshops"""
    
    # User coordinates
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="User latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="User longitude")
    
    # Or address for geocoding
    address: Optional[str] = Field(None, min_length=5, max_length=200, description="Address to search by")
    city: Optional[str] = Field(None, min_length=2, max_length=50, description="City")
    
    # Search filters
    radius_km: Optional[float] = Field(10, ge=1, le=100, description="Search radius in kilometers")
    max_results: Optional[int] = Field(20, ge=1, le=100, description="Maximum number of results")
    
    # Additional filters
    services: Optional[List[str]] = Field(None, description="Required services")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Minimum rating")
    verified_only: Optional[bool] = Field(False, description="Only verified workshops")
    open_now: Optional[bool] = Field(False, description="Only workshops currently open")

class WorkshopWithDistance(WorkshopResponse):
    """Workshop with distance information"""
    distance_km: Optional[float] = Field(None, description="Distance in kilometers")
    estimated_travel_time_minutes: Optional[int] = Field(None, description="Estimated travel time in minutes")

class GeographicSearchResult(BaseModel):
    """Geographic search result"""
    workshops: List[WorkshopWithDistance]
    search_center: Dict[str, float] = Field(description="Search center (lat, lon)")
    total_found: int = Field(description="Total workshops found")
    search_radius_km: float = Field(description="Search radius used")
    
class LocationInfo(BaseModel):
    """Location information"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    
class DistanceCalculation(BaseModel):
    """Calculating the distance between two points"""
    from_location: LocationInfo
    to_location: LocationInfo
    distance_km: float
    estimated_travel_time_minutes: int

class NearbyWorkshopsRequest(BaseModel):
    """Request for nearby workshops"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(10, ge=1, le=100)
    limit: int = Field(20, ge=1, le=100)
    
class GeocodeRequest(BaseModel):
    """Request for geocoding"""
    address: str = Field(..., min_length=5, max_length=200)
    city: Optional[str] = Field("Puerto Rico", max_length=50)
    
class GeocodeResponse(BaseModel):
    """Request for geocoding"""
    success: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    formatted_address: Optional[str] = None
    error_message: Optional[str] = None

# === ADVANCED SEARCH SCHEMAS ===

class WeekDay(str, Enum):
    """Daays of the week"""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

class ServiceType(str, Enum):
    """Types of services offered by workshops"""
    OIL_CHANGE = "Oil Change"
    BRAKES = "Brakes"
    SUSPENSION = "Suspension"
    TRANSMISSION = "Transmission"
    AC = "A/C"
    ALIGNMENT = "Alignment"
    BALANCING = "Balancing"
    INSPECTION = "Inspection"
    ENGINE = "Engine"
    ELECTRICAL = "Electrical"
    TIRES = "Tires"

class CarBrand(str, Enum):
    """Brands of cars that workshops may specialize in"""
    TOYOTA = "Toyota"
    HONDA = "Honda"
    NISSAN = "Nissan"
    BMW = "BMW"
    MERCEDES = "Mercedes"
    HYUNDAI = "Hyundai"
    KIA = "Kia"
    FORD = "Ford"
    CHEVROLET = "Chevrolet"
    VOLKSWAGEN = "Volkswagen"

class AdvancedGeographicSearch(BaseModel):
    """Advanced geographic search with multiple filters"""
    
    # Base location
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="User latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="User longitude")
    address: Optional[str] = Field(None, min_length=5, max_length=200, description="Geocoded address")
    city: Optional[str] = Field("Puerto Rico", max_length=50, description="City")
    
    # Search parameters
    radius_km: float = Field(25, ge=1, le=200, description="Search radius in km")
    max_results: int = Field(20, ge=1, le=100, description="Maximum results")
    
    # Service filters
    required_services: Optional[List[str]] = Field(None, description="Services that the workshop MUST have")
    preferred_services: Optional[List[str]] = Field(None, description="Preferred services (ranking bonus)")
    
    # Specialty filters
    car_brands: Optional[List[str]] = Field(None, description="Car brand specialties")
    specializations: Optional[List[str]] = Field(None, description="Specific specializations")
    
    # Quality filters
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Minimum rating")
    min_reviews: Optional[int] = Field(None, ge=0, description="Minimum number of reviews")
    verified_only: bool = Field(False, description="Only verified workshops")
    
    # Time/schedule filters
    open_now: bool = Field(False, description="Only workshops currently open")
    day_of_week: Optional['WeekDay'] = Field(None, description="Filter by specific day")
    time_of_day: Optional[str] = Field(None, description="Time in HH:MM format")
    
    # Experience filters
    min_years_in_business: Optional[int] = Field(None, ge=0, description="Minimum years in business")
    max_years_in_business: Optional[int] = Field(None, ge=0, description="Maximum years in business")
    
    # Sorting
    sort_by: Optional[str] = Field("distance", description="Sort by: distance, rating, reviews, years")
    sort_order: Optional[str] = Field("asc", description="Order: asc, desc")

class WorkshopAvailability(BaseModel):
    """Availability of a workshop"""
    is_open_now: bool
    opens_at: Optional[str] = None
    closes_at: Optional[str] = None
    is_open_today: bool
    today_hours: Optional[str] = None
    next_open_time: Optional[str] = None

class WorkshopWithAdvancedInfo(WorkshopWithDistance):
    """Workshop with advanced search information"""
    availability: Optional[WorkshopAvailability] = None
    matching_services: List[str] = Field(default_factory=list, description="Services that match the search")
    matching_specialties: List[str] = Field(default_factory=list, description="Specialties that match the search")
    search_score: Optional[float] = Field(None, description="Relevance score from 0 to 100")
    
class AdvancedSearchResult(BaseModel):
    """Advanced search result"""
    workshops: List[WorkshopWithAdvancedInfo]
    search_center: Dict[str, float]
    total_found: int
    search_radius_km: float
    filters_applied: Dict[str, Any]
    search_metadata: Dict[str, Any]

class ServiceSearchRequest(BaseModel):
    """Specific request for service-based search"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    services: List[str] = Field(..., min_items=1, description="List of required services")
    radius_km: float = Field(20, ge=1, le=100)
    match_all_services: bool = Field(True, description="Must include ALL services or just some")

class BrandSpecialtySearchRequest(BaseModel):
    """Request for search by brand specialties"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    car_brand: str = Field(..., description="Brand of car")
    radius_km: float = Field(30, ge=1, le=100)
    
class OpenNowSearchRequest(BaseModel):
    """Request for workshops currently open"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(25, ge=1, le=100)
    current_time: Optional[str] = Field(None, description="Current time in HH:MM format")
    day_of_week: Optional[WeekDay] = Field(None, description="Day of the week")

class SearchSuggestion(BaseModel):
    """Search suggestion"""
    type: str = Field(description="Type: service, brand, location")
    value: str = Field(description="Suggestion value")
    display_text: str = Field(description="Text to display")
    count: int = Field(description="Number of workshops offering this")

class SearchSuggestionsResponse(BaseModel):
    """Answer with search suggestions"""
    services: List[SearchSuggestion]
    brands: List[SearchSuggestion]
    cities: List[SearchSuggestion]
    popular_searches: List[str]