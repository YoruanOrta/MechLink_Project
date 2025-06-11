from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from app.models.review import Review, ReviewHelpful
from app.models.user import User
from app.models.workshop import Workshop
from app.models.vehicle import Vehicle
from app.schemas.review_schemas import (
    ReviewCreate, ReviewUpdate, ReviewResponse, ReviewStats,
    WorkshopReviewSummary, ReviewFilters
)

class ReviewService:
    """Review management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_review(self, user_id: str, review_data: ReviewCreate) -> Review:
        """Create new review"""
        
        # Verify that the user has not already reviewed this workshop for the same appointment
        if review_data.appointment_id:
            existing_review = self.db.query(Review).filter(
                and_(
                    Review.user_id == user_id,
                    Review.appointment_id == review_data.appointment_id
                )
            ).first()
            
            if existing_review:
                raise ValueError("You have already reviewed this service")
        
        # Verify that the workshop exists
        workshop = self.db.query(Workshop).filter(
            Workshop.id == review_data.workshop_id
        ).first()
        
        if not workshop:
            raise ValueError("Workshop not found")
        
        # Crear la reseña
        review = Review(
            user_id=user_id,
            workshop_id=review_data.workshop_id,
            appointment_id=review_data.appointment_id,
            vehicle_id=review_data.vehicle_id,
            rating=review_data.rating,
            title=review_data.title,
            comment=review_data.comment,
            service_type=review_data.service_type,
            quality_rating=review_data.quality_rating,
            price_rating=review_data.price_rating,
            time_rating=review_data.time_rating,
            service_rating=review_data.service_rating,
            would_recommend=review_data.would_recommend,
            service_date=review_data.service_date,
            is_verified=self._is_verified_review(user_id, review_data.appointment_id)
        )
        
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        
        return review
    
    def get_review(self, review_id: str, include_private: bool = False) -> Optional[Review]:
        """Get review by ID"""
        
        query = self.db.query(Review).filter(Review.id == review_id)
        
        if not include_private:
            query = query.filter(Review.is_public == True)
        
        return query.first()
    
    def get_reviews_by_workshop(
        self,
        workshop_id: str,
        filters: Optional[ReviewFilters] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Review], int]:
        """Get reviews of a workshop with filters"""
        
        query = self.db.query(Review).filter(
            and_(
                Review.workshop_id == workshop_id,
                Review.is_public == True
            )
        )
        
        if filters:
            query = self._apply_filters(query, filters)
        
        total = query.count()
        
        reviews = query.order_by(desc(Review.created_at)).offset(skip).limit(limit).all()
        
        return reviews, total
    
    def get_reviews_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Review], int]:
        """Get reviews from a user"""
        
        query = self.db.query(Review).filter(Review.user_id == user_id)
        total = query.count()
        
        reviews = query.order_by(desc(Review.created_at)).offset(skip).limit(limit).all()
        
        return reviews, total
    
    def update_review(
        self,
        review_id: str,
        user_id: str,
        update_data: ReviewUpdate
    ) -> Optional[Review]:
        """Update review (author only)"""
        
        review = self.db.query(Review).filter(
            and_(
                Review.id == review_id,
                Review.user_id == user_id
            )
        ).first()
        
        if not review:
            return None
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(review, field, value)
        
        review.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(review)
        
        return review
    
    def delete_review(self, review_id: str, user_id: str) -> bool:
        """Delete review (author only)"""
        
        review = self.db.query(Review).filter(
            and_(
                Review.id == review_id,
                Review.user_id == user_id
            )
        ).first()
        
        if not review:
            return False
        
        self.db.delete(review)
        self.db.commit()
        
        return True
    
    def add_workshop_response(
        self,
        review_id: str,
        workshop_id: str,
        response: str
    ) -> Optional[Review]:
        """Add workshop response"""
        
        review = self.db.query(Review).filter(
            and_(
                Review.id == review_id,
                Review.workshop_id == workshop_id
            )
        ).first()
        
        if not review:
            return None
        
        review.workshop_response = response
        review.workshop_response_date = datetime.now()
        
        self.db.commit()
        self.db.refresh(review)
        
        return review
    
    def vote_helpful(self, review_id: str, user_id: str, is_helpful: bool) -> bool:
        """Vote if a review is helpful"""
        
        # Verify that the review exists
        review = self.db.query(Review).filter(Review.id == review_id).first()
        if not review:
            return False
        
        # Check if you have already voted
        existing_vote = self.db.query(ReviewHelpful).filter(
            and_(
                ReviewHelpful.review_id == review_id,
                ReviewHelpful.user_id == user_id
            )
        ).first()
        
        if existing_vote:
            # Update existing vote
            old_helpful = existing_vote.is_helpful
            existing_vote.is_helpful = is_helpful
            
            # Update counter in review
            if old_helpful and not is_helpful:
                review.helpful_votes = max(0, review.helpful_votes - 1)
            elif not old_helpful and is_helpful:
                review.helpful_votes += 1
        else:
            # Create new vote
            vote = ReviewHelpful(
                review_id=review_id,
                user_id=user_id,
                is_helpful=is_helpful
            )
            self.db.add(vote)
            
            # Update counter
            if is_helpful:
                review.helpful_votes += 1
        
        self.db.commit()
        return True
    
    def get_workshop_stats(self, workshop_id: str) -> ReviewStats:
        """Get review statistics for a workshop"""
        
        reviews = self.db.query(Review).filter(
            and_(
                Review.workshop_id == workshop_id,
                Review.is_public == True
            )
        ).all()
        
        if not reviews:
            return ReviewStats(
                total_reviews=0,
                average_rating=0.0,
                rating_distribution={str(i): 0 for i in range(1, 6)},
                recommendation_percentage=0.0,
                service_breakdown={}
            )
        
        # Calculate statistics
        total_reviews = len(reviews)
        ratings = [r.rating for r in reviews]
        average_rating = sum(ratings) / len(ratings)
        
        # Star distribution
        rating_distribution = {}
        for i in range(1, 6):
            count = len([r for r in reviews if r.rating == i])
            rating_distribution[str(i)] = count
        
        # Averages by aspect
        quality_ratings = [r.quality_rating for r in reviews if r.quality_rating]
        price_ratings = [r.price_rating for r in reviews if r.price_rating]
        time_ratings = [r.time_rating for r in reviews if r.time_rating]
        service_ratings = [r.service_rating for r in reviews if r.service_rating]
        
        avg_quality = sum(quality_ratings) / len(quality_ratings) if quality_ratings else None
        avg_price = sum(price_ratings) / len(price_ratings) if price_ratings else None
        avg_time = sum(time_ratings) / len(time_ratings) if time_ratings else None
        avg_service = sum(service_ratings) / len(service_ratings) if service_ratings else None
        
        # Recommendation percentage
        recommendations = [r for r in reviews if r.would_recommend]
        recommendation_percentage = (len(recommendations) / total_reviews) * 100
        
        # Distribution by type of service
        service_breakdown = {}
        for review in reviews:
            if review.service_type:
                service_breakdown[review.service_type] = service_breakdown.get(review.service_type, 0) + 1
        
        # Verified reviews
        verified_count = len([r for r in reviews if r.is_verified])
        
        return ReviewStats(
            total_reviews=total_reviews,
            average_rating=round(average_rating, 2),
            rating_distribution=rating_distribution,
            avg_quality=round(avg_quality, 2) if avg_quality else None,
            avg_price=round(avg_price, 2) if avg_price else None,
            avg_time=round(avg_time, 2) if avg_time else None,
            avg_service=round(avg_service, 2) if avg_service else None,
            total_verified=verified_count,
            recommendation_percentage=round(recommendation_percentage, 1),
            service_breakdown=service_breakdown
        )
    
    def get_workshop_summary(self, workshop_id: str) -> Optional[WorkshopReviewSummary]:
        """Get a full summary of workshop reviews"""
        
        workshop = self.db.query(Workshop).filter(Workshop.id == workshop_id).first()
        if not workshop:
            return None
        
        stats = self.get_workshop_stats(workshop_id)
        
        # Get recent reviews
        recent_reviews, _ = self.get_reviews_by_workshop(
            workshop_id=workshop_id,
            skip=0,
            limit=5
        )
        
        # Convert to response format
        recent_review_responses = []
        for review in recent_reviews:
            review_response = self._review_to_response(review)
            recent_review_responses.append(review_response)
        
        return WorkshopReviewSummary(
            workshop_id=workshop_id,
            workshop_name=workshop.name,
            stats=stats,
            recent_reviews=recent_review_responses
        )
    
    def search_reviews(
        self,
        query: str,
        filters: Optional[ReviewFilters] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Review], int]:
        """Search reviews by text"""
        
        db_query = self.db.query(Review).filter(
            and_(
                Review.is_public == True,
                or_(
                    Review.title.ilike(f"%{query}%"),
                    Review.comment.ilike(f"%{query}%"),
                    Review.service_type.ilike(f"%{query}%")
                )
            )
        )
        
        if filters:
            db_query = self._apply_filters(db_query, filters)
        
        total = db_query.count()
        reviews = db_query.order_by(desc(Review.created_at)).offset(skip).limit(limit).all()
        
        return reviews, total
    
    def _apply_filters(self, query, filters: ReviewFilters):
        """Apply filters to a review query"""
        
        if filters.rating:
            query = query.filter(Review.rating == filters.rating)
        
        if filters.min_rating:
            query = query.filter(Review.rating >= filters.min_rating)
        
        if filters.service_type:
            query = query.filter(Review.service_type == filters.service_type)
        
        if filters.verified_only:
            query = query.filter(Review.is_verified == True)
        
        if filters.with_comment:
            query = query.filter(Review.comment.isnot(None))
        
        if filters.start_date:
            query = query.filter(Review.created_at >= filters.start_date)
        
        if filters.end_date:
            query = query.filter(Review.created_at <= filters.end_date)
        
        return query
    
    def _is_verified_review(self, user_id: str, appointment_id: Optional[str]) -> bool:
        """Check if a review should be marked as verified"""
        # A review is considered verified if it's associated with a real appointment
        if appointment_id:
            # Here we would check that the appointment exists and belongs to the user
            # For now, return True if appointment_id is provided
            return True
        return False
    
    def _review_to_response(self, review: Review) -> ReviewResponse:
        """Convert Review model to ReviewResponse"""
        
        # Obtain user information (without sensitive data)
        user = self.db.query(User).filter(User.id == review.user_id).first()
        user_name = f"{user.first_name} {user.last_name[0]}." if user else "User"
        
        # Get vehicle information
        vehicle_info = None
        if review.vehicle_id:
            vehicle = self.db.query(Vehicle).filter(Vehicle.id == review.vehicle_id).first()
            if vehicle:
                vehicle_info = f"{vehicle.make} {vehicle.model} {vehicle.year}"
        
        return ReviewResponse(
            id=review.id,
            user_id=review.user_id,
            workshop_id=review.workshop_id,
            appointment_id=review.appointment_id,
            vehicle_id=review.vehicle_id,
            rating=review.rating,
            title=review.title,
            comment=review.comment,
            service_type=review.service_type,
            quality_rating=review.quality_rating,
            price_rating=review.price_rating,
            time_rating=review.time_rating,
            service_rating=review.service_rating,
            would_recommend=review.would_recommend,
            service_date=review.service_date,
            user_name=user_name,
            vehicle_info=vehicle_info,
            is_verified=review.is_verified,
            is_moderated=review.is_moderated,
            is_public=review.is_public,
            workshop_response=review.workshop_response,
            workshop_response_date=review.workshop_response_date,
            helpful_votes=review.helpful_votes,
            created_at=review.created_at,
            updated_at=review.updated_at
        )