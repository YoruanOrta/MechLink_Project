from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

# === ENUMS ===

class RatingEnum(int, Enum):
    ONE_STAR = 1
    TWO_STARS = 2
    THREE_STARS = 3
    FOUR_STARS = 4
    FIVE_STARS = 5

class ServiceTypeEnum(str, Enum):
    OIL_CHANGE = "Oil change"
    BRAKE_SERVICE = "Brakes"
    TIRE_SERVICE = "Tires"
    ENGINE_REPAIR = "Engine repair"
    TRANSMISSION = "Transmission"
    ELECTRICAL = "Electrical system"
    AIR_CONDITIONING = "Air conditioning"
    GENERAL_MAINTENANCE = "General maintenance"
    INSPECTION = "Inspection"
    OTHER = "Other"

# === REVIEW SCHEMAS ===

class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    title: Optional[str] = Field(None, max_length=200, description="Review title")
    comment: Optional[str] = Field(None, max_length=2000, description="Detailed comment")
    service_type: Optional[str] = Field(None, description="Type of service reviewed")

    # Specific ratings (optional)
    quality_rating: Optional[int] = Field(None, ge=1, le=5, description="Quality of work")
    price_rating: Optional[int] = Field(None, ge=1, le=5, description="Value for money")
    time_rating: Optional[int] = Field(None, ge=1, le=5, description="Punctuality")
    service_rating: Optional[int] = Field(None, ge=1, le=5, description="Customer service")

    would_recommend: bool = Field(True, description="Would you recommend this shop?")
    service_date: Optional[datetime] = Field(None, description="Date of service")

class ReviewCreate(ReviewBase):
    workshop_id: str = Field(..., description="Workshop ID")
    appointment_id: Optional[str] = Field(None, description="Related appointment ID")
    vehicle_id: Optional[str] = Field(None, description="Vehicle ID")
    
    @validator('rating', 'quality_rating', 'price_rating', 'time_rating', 'service_rating')
    def validate_ratings(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Ratings must be between 1 and 5')
        return v

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    comment: Optional[str] = Field(None, max_length=2000)
    service_type: Optional[str] = None
    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    price_rating: Optional[int] = Field(None, ge=1, le=5)
    time_rating: Optional[int] = Field(None, ge=1, le=5)
    service_rating: Optional[int] = Field(None, ge=1, le=5)
    would_recommend: Optional[bool] = None

class ReviewResponse(ReviewBase):
    id: str
    user_id: str
    workshop_id: str
    appointment_id: Optional[str] = None
    vehicle_id: Optional[str] = None
    
    # User information (no sensitive data)
    user_name: Optional[str] = None  # It will be filled in at the endpoint
    
    # Vehicle information
    vehicle_info: Optional[str] = None  # "Toyota Camry 2020"
    
    # State and moderation
    is_verified: bool = False
    is_moderated: bool = False
    is_public: bool = True
    
    # Workshop Response
    workshop_response: Optional[str] = None
    workshop_response_date: Optional[datetime] = None
    
    # Stats
    helpful_votes: int = 0
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# === WORKSHOP RESPONSE SCHEMAS ===

class WorkshopResponseCreate(BaseModel):
    response: str = Field(..., min_length=10, max_length=1000, description="Workshop response")

class WorkshopResponseUpdate(BaseModel):
    response: str = Field(..., min_length=10, max_length=1000)

# === HELPFUL VOTE SCHEMAS ===

class ReviewHelpfulCreate(BaseModel):
    is_helpful: bool = Field(..., description="True if useful, False if noto")

class ReviewHelpfulResponse(BaseModel):
    id: str
    review_id: str
    user_id: str
    is_helpful: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# === FILTER AND SEARCH SCHEMAS ===

class ReviewFilters(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5, description="Filter by specific rating")
    min_rating: Optional[int] = Field(None, ge=1, le=5, description="Minimum rating")
    service_type: Optional[str] = Field(None, description="Filter by service type")
    verified_only: bool = Field(False, description="Only verified reviews")
    with_comment: bool = Field(False, description="Only reviews with comments")
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")

# === STATISTICS SCHEMAS ===

class ReviewStats(BaseModel):
    total_reviews: int
    average_rating: float = Field(..., description="Average rating")
    rating_distribution: dict = Field(..., description="Star rating distribution")
    
    # Averages by aspect
    avg_quality: Optional[float] = None
    avg_price: Optional[float] = None
    avg_time: Optional[float] = None
    avg_service: Optional[float] = None
    
    # Additional statistics
    total_verified: int = 0
    recommendation_percentage: float = 0.0  # % who would recommend
    
    # Breakdown by service
    service_breakdown: dict = Field(default_factory=dict)

class WorkshopReviewSummary(BaseModel):
    workshop_id: str
    workshop_name: str
    stats: ReviewStats
    recent_reviews: List[ReviewResponse] = Field(default_factory=list)

# === BULK OPERATIONS ===

class BulkReviewRequest(BaseModel):
    workshop_ids: List[str] = Field(..., min_items=1, description="IDs of workshops")
    filters: Optional[ReviewFilters] = None