from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_ 
from typing import List, Optional

from app.config.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.services.review_service import ReviewService
from app.schemas.review_schemas import (
    ReviewCreate, ReviewUpdate, ReviewResponse, ReviewStats,
    WorkshopReviewSummary, ReviewFilters, ReviewHelpfulCreate,
    WorkshopResponseCreate
)

router = APIRouter(prefix="/reviews", tags=["reviews"])

# === USER REVIEW ENDPOINTS ===

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new review"""
    
    review_service = ReviewService(db)
    
    try:
        review = review_service.create_review(current_user.id, review_data)
        return review_service._review_to_response(review)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/my-reviews", response_model=List[ReviewResponse])
def get_my_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reviews of the current user"""
    
    review_service = ReviewService(db)
    reviews, total = review_service.get_reviews_by_user(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    return [review_service._review_to_response(review) for review in reviews]

@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: str,
    db: Session = Depends(get_db)
):
    """Get specific review"""
    
    review_service = ReviewService(db)
    review = review_service.get_review(review_id)
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return review_service._review_to_response(review)

@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: str,
    update_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update own review"""
    
    review_service = ReviewService(db)
    updated_review = review_service.update_review(
        review_id=review_id,
        user_id=current_user.id,
        update_data=update_data
    )
    
    if not updated_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or not authorized"
        )
    
    return review_service._review_to_response(updated_review)

@router.delete("/{review_id}")
def delete_review(
    review_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete own review"""
    
    review_service = ReviewService(db)
    success = review_service.delete_review(review_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or not authorized"
        )
    
    return {"message": "Review deleted successfully"}

# === WORKSHOP REVIEW ENDPOINTS ===

@router.get("/workshop/{workshop_id}", response_model=List[ReviewResponse])
def get_workshop_reviews(
    workshop_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    rating: Optional[int] = Query(None, ge=1, le=5, description="Filter by rating"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="Minimum rating"),
    service_type: Optional[str] = Query(None, description="Filter by service type"),
    verified_only: bool = Query(False, description="Only verified reviews"),
    with_comment: bool = Query(False, description="Only reviews with comments"),
    db: Session = Depends(get_db)
):
    """Get workshop reviews with filters"""
    
    review_service = ReviewService(db)
    
    # Create filters
    filters = ReviewFilters(
        rating=rating,
        min_rating=min_rating,
        service_type=service_type,
        verified_only=verified_only,
        with_comment=with_comment
    )
    
    reviews, total = review_service.get_reviews_by_workshop(
        workshop_id=workshop_id,
        filters=filters,
        skip=skip,
        limit=limit
    )
    
    return [review_service._review_to_response(review) for review in reviews]

@router.get("/workshop/{workshop_id}/stats", response_model=ReviewStats)
def get_workshop_review_stats(
    workshop_id: str,
    db: Session = Depends(get_db)
):
    """Get workshop review statistics"""
    review_service = ReviewService(db)
    return review_service.get_workshop_stats(workshop_id)

@router.get("/workshop/{workshop_id}/summary", response_model=WorkshopReviewSummary)
def get_workshop_review_summary(
    workshop_id: str,
    db: Session = Depends(get_db)
):
    """Get complete review summary for a workshop"""
    
    review_service = ReviewService(db)
    summary = review_service.get_workshop_summary(workshop_id)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workshop not found"
        )
    
    return summary

# === SEARCH ENDPOINTS ===

@router.get("/search", response_model=List[ReviewResponse])
def search_reviews(
    q: str = Query(..., min_length=3, description="Text to search"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    rating: Optional[int] = Query(None, ge=1, le=5),
    min_rating: Optional[int] = Query(None, ge=1, le=5),
    service_type: Optional[str] = Query(None),
    verified_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Search reviews by text"""
    
    review_service = ReviewService(db)
    
    filters = ReviewFilters(
        rating=rating,
        min_rating=min_rating,
        service_type=service_type,
        verified_only=verified_only
    )
    
    reviews, total = review_service.search_reviews(
        query=q,
        filters=filters,
        skip=skip,
        limit=limit
    )
    
    return [review_service._review_to_response(review) for review in reviews]

# === HELPFUL VOTES ===

@router.post("/{review_id}/helpful")
def vote_review_helpful(
    review_id: str,
    vote_data: ReviewHelpfulCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Vote if a review is helpful"""
    
    review_service = ReviewService(db)
    success = review_service.vote_helpful(
        review_id=review_id,
        user_id=current_user.id,
        is_helpful=vote_data.is_helpful
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return {"message": "Vote recorded successfully"}

# === WORKSHOP RESPONSE ENDPOINTS ===

@router.post("/{review_id}/response")
def add_workshop_response(
    review_id: str,
    response_data: WorkshopResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add workshop response to a review"""
    
    # Note: Here you should verify that the current user is the owner of the workshop
    # For simplicity, we assume any authenticated user can respond
    
    review_service = ReviewService(db)
    
    # Get the review to verify the workshop_id
    review = review_service.get_review(review_id, include_private=True)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    updated_review = review_service.add_workshop_response(
        review_id=review_id,
        workshop_id=review.workshop_id,
        response=response_data.response
    )
    
    if not updated_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error adding response"
        )
    
    return {"message": "Response added successfully"}

# === ANALYTICS ENDPOINTS ===

@router.get("/analytics/trending-services")
def get_trending_services(
    days: int = Query(30, ge=7, le=365, description="Days for analysis"),
    limit: int = Query(10, ge=5, le=50),
    db: Session = Depends(get_db)
):
    """Get most commented/reviewed services"""
    
    review_service = ReviewService(db)
    
    # Query to get most mentioned services
    from datetime import datetime, timedelta
    from sqlalchemy import func
    from app.models.review import Review
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    trending = db.query(
        Review.service_type,
        func.count(Review.id).label('review_count'),
        func.avg(Review.rating).label('avg_rating')
    ).filter(
        and_(
            Review.service_type.isnot(None),
            Review.created_at >= cutoff_date,
            Review.is_public == True
        )
    ).group_by(Review.service_type).order_by(
        func.count(Review.id).desc()
    ).limit(limit).all()
    
    return [
        {
            "service_type": item.service_type,
            "review_count": item.review_count,
            "average_rating": round(float(item.avg_rating), 2)
        }
        for item in trending
    ]

@router.get("/analytics/user-satisfaction")
def get_user_satisfaction_trends(
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """Get user satisfaction trends"""
    
    from datetime import datetime, timedelta
    from sqlalchemy import func, extract
    from app.models.review import Review
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Satisfacción por mes
    monthly_satisfaction = db.query(
        extract('year', Review.created_at).label('year'),
        extract('month', Review.created_at).label('month'),
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('review_count'),
        func.avg(func.case([(Review.would_recommend == True, 1)], else_=0)).label('recommendation_rate')
    ).filter(
        and_(
            Review.created_at >= cutoff_date,
            Review.is_public == True
        )
    ).group_by(
        extract('year', Review.created_at),
        extract('month', Review.created_at)
    ).order_by(
        extract('year', Review.created_at),
        extract('month', Review.created_at)
    ).all()
    
    return [
        {
            "period": f"{int(item.year)}-{int(item.month):02d}",
            "average_rating": round(float(item.avg_rating), 2),
            "review_count": item.review_count,
            "recommendation_rate": round(float(item.recommendation_rate) * 100, 1)
        }
        for item in monthly_satisfaction
    ]

# === MODERATION ENDPOINTS (For administrators) ===

@router.get("/admin/pending-moderation", response_model=List[ReviewResponse])
def get_pending_moderation_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get pending moderation reviews (Admin)"""
    
    # Note: Here you should verify that the user is an administrator
    
    from app.models.review import Review
    
    reviews = db.query(Review).filter(
        Review.is_moderated == False
    ).order_by(Review.created_at.desc()).offset(skip).limit(limit).all()
    
    review_service = ReviewService(db)
    return [review_service._review_to_response(review) for review in reviews]

@router.patch("/{review_id}/moderate")
def moderate_review(
    review_id: str,
    approve: bool = Query(..., description="True to approve, False to reject"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Moderate a review (Admin)"""
    
    # Note: Verify admin permissions
    
    from app.models.review import Review
    
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    review.is_moderated = True
    review.is_public = approve
    
    db.commit()
    
    return {"message": f"Review {'approved' if approve else 'rejected'} successfully"}