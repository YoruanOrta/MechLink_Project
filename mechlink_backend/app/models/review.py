from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.config.database import Base

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Main relationships
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    workshop_id = Column(String, ForeignKey("workshops.id"), nullable=False)
    appointment_id = Column(String, ForeignKey("appointments.id"), nullable=True)  # If related to an appointment
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=True)  # Vehicle of the service
    
    # Review content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(200), nullable=True)  # Optional title
    comment = Column(Text, nullable=True)  # Detailed comment
    service_type = Column(String(100), nullable=True)  # Type of service reviewed
    
    # Specific aspects (optional - detailed ratings)
    quality_rating = Column(Integer, nullable=True)  # Work quality (1-5)
    price_rating = Column(Integer, nullable=True)    # Value for money (1-5)
    time_rating = Column(Integer, nullable=True)     # Punctuality (1-5)
    service_rating = Column(Integer, nullable=True)  # Customer service (1-5)
    
    # Additional information
    service_date = Column(DateTime, nullable=True)  # Date of the reviewed service
    would_recommend = Column(Boolean, default=True)  # Would recommend the workshop?
    
    # Moderation and status
    is_verified = Column(Boolean, default=False)  # Verified as a real customer
    is_moderated = Column(Boolean, default=False)  # Reviewed by moderation
    is_public = Column(Boolean, default=True)  # Publicly visible
    
    # Workshop response
    workshop_response = Column(Text, nullable=True)  # Workshop's response
    workshop_response_date = Column(DateTime, nullable=True)
    
    # Metadata
    helpful_votes = Column(Integer, default=0)  # "Helpful" votes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    workshop = relationship("Workshop")
    vehicle = relationship("Vehicle")
    
    def __repr__(self):
        return f"<Review(workshop='{self.workshop_id}', rating='{self.rating}', user='{self.user_id}')>"

class ReviewHelpful(Base):
    """Table for 'helpful' votes on reviews"""
    __tablename__ = "review_helpful"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = Column(String, ForeignKey("reviews.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    is_helpful = Column(Boolean, nullable=False)  # True = helpful, False = not helpful
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    review = relationship("Review")
    user = relationship("User")
    
    def __repr__(self):
        return f"<ReviewHelpful(review='{self.review_id}', user='{self.user_id}', helpful='{self.is_helpful}')>"