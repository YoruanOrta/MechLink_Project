from datetime import datetime, time
from typing import List, Dict, Optional, Tuple
import re
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.workshop import Workshop
from app.services.geolocation_service import GeolocationService

class AdvancedSearchService:
    """Service for advanced workshop searches"""
    
    def __init__(self, db: Session):
        self.db = db
        self.geo_service = GeolocationService()
    
    def check_workshop_availability(self, workshop: Workshop, 
                                  current_time: Optional[str] = None,
                                  day_of_week: Optional[str] = None) -> Dict:
        """
        Check availability of a workshop
        """
        if not workshop.working_hours:
            return {
                "is_open_now": False,
                "is_open_today": False,
                "today_hours": None,
                "opens_at": None,
                "closes_at": None,
                "next_open_time": None
            }
        
        # Get current day if not provided
        if not day_of_week:
            day_of_week = datetime.now().strftime('%A').lower()
        
        # Get current time if not provided
        if not current_time:
            current_time = datetime.now().strftime('%H:%M')
        
        # Get schedules of the day
        today_schedule = workshop.working_hours.get(day_of_week)
        
        if not today_schedule:
            return {
                "is_open_now": False,
                "is_open_today": False,
                "today_hours": None,
                "opens_at": None,
                "closes_at": None,
                "next_open_time": self._get_next_open_time(workshop.working_hours, day_of_week)
            }
        
        # Parse schedules (format: "8:00-17:00")
        try:
            open_time, close_time = today_schedule.split('-')
            open_hour = datetime.strptime(open_time.strip(), '%H:%M').time()
            close_hour = datetime.strptime(close_time.strip(), '%H:%M').time()
            current_hour = datetime.strptime(current_time, '%H:%M').time()
            
            is_open_now = open_hour <= current_hour <= close_hour
            
            return {
                "is_open_now": is_open_now,
                "is_open_today": True,
                "today_hours": today_schedule,
                "opens_at": open_time.strip(),
                "closes_at": close_time.strip(),
                "next_open_time": None if is_open_now else open_time.strip()
            }
            
        except (ValueError, AttributeError):
            return {
                "is_open_now": False,
                "is_open_today": False,
                "today_hours": today_schedule,
                "opens_at": None,
                "closes_at": None,
                "next_open_time": None
            }
    
    def _get_next_open_time(self, working_hours: Dict, current_day: str) -> Optional[str]:
        """Get the next opening time"""
        days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        current_index = days_order.index(current_day) if current_day in days_order else 0
        
        # Search in the next 7 days
        for i in range(7):
            day_index = (current_index + i) % 7
            day = days_order[day_index]
            schedule = working_hours.get(day)
            
            if schedule and '-' in schedule:
                open_time = schedule.split('-')[0].strip()
                day_name = day.capitalize()
                return f"{day_name} {open_time}"
        
        return None
    
    def filter_by_services(self, workshops: List[Workshop], 
                          required_services: List[str],
                          preferred_services: Optional[List[str]] = None,
                          match_all: bool = True) -> List[Tuple[Workshop, Dict]]:
        """
        Filter workshops by services
        Returns a list of (workshop, metadata) where metadata includes matching information
        """
        results = []
        
        for workshop in workshops:
            workshop_services = workshop.services or []
            
            workshop_services_lower = [s.lower() for s in workshop_services]
            required_lower = [s.lower() for s in required_services]
            
            if match_all:
                matching_required = [req for req in required_lower 
                                   if any(req in ws for ws in workshop_services_lower)]
                has_all_required = len(matching_required) == len(required_services)
            else:
                matching_required = [req for req in required_lower 
                                   if any(req in ws for ws in workshop_services_lower)]
                has_all_required = len(matching_required) > 0
            
            if not has_all_required:
                continue
            
            preferred_matches = []
            if preferred_services:
                preferred_lower = [s.lower() for s in preferred_services]
                preferred_matches = [pref for pref in preferred_lower 
                                   if any(pref in ws for ws in workshop_services_lower)]
            
            exact_matches = []
            for service in workshop_services:
                for req in required_services + (preferred_services or []):
                    if req.lower() in service.lower():
                        exact_matches.append(service)
            
            metadata = {
                "matching_services": list(set(exact_matches)),
                "required_matches": len(matching_required),
                "preferred_matches": len(preferred_matches),
                "total_matches": len(matching_required) + len(preferred_matches)
            }
            
            results.append((workshop, metadata))
        
        return results
    
    def filter_by_specialties(self, workshops: List[Workshop], 
                            car_brands: List[str],
                            specializations: Optional[List[str]] = None) -> List[Tuple[Workshop, Dict]]:
        """Filter workshops by specialties"""
        results = []
        
        for workshop in workshops:
            workshop_specialties = workshop.specialties or []
            workshop_specialties_lower = [s.lower() for s in workshop_specialties]
            
            # Check car brands
            brand_matches = []
            for brand in car_brands:
                for specialty in workshop_specialties_lower:
                    if brand.lower() in specialty:
                        brand_matches.append(brand)
            
            # Check additional specializations
            specialization_matches = []
            if specializations:
                for spec in specializations:
                    for specialty in workshop_specialties_lower:
                        if spec.lower() in specialty:
                            specialization_matches.append(spec)
            
            # Only include if you have at least one match
            if brand_matches or specialization_matches:
                metadata = {
                    "matching_specialties": list(set(brand_matches + specialization_matches)),
                    "brand_matches": len(set(brand_matches)),
                    "specialization_matches": len(set(specialization_matches))
                }
                results.append((workshop, metadata))
        
        return results
    
    def calculate_search_score(self, workshop: Workshop, metadata: Dict, 
                             search_params: Dict) -> float:
        """
        Calculate relevance score for a workshop (0-100)
        """
        score = 0.0
        
        # Base score by distance (40 points maximum)
        distance = metadata.get('distance_km', float('inf'))
        if distance < float('inf'):
            max_distance = search_params.get('radius_km', 50)
            distance_score = max(0, (1 - distance / max_distance) * 40)
            score += distance_score
        
        # Score per rating (25 points maximum)
        rating = float(workshop.rating_average or 0)
        rating_score = (rating / 5.0) * 25
        score += rating_score
        
        # Score by number of reviews (10 points maximum)
        reviews = workshop.total_reviews or 0
        review_score = min(reviews / 50.0, 1.0) * 10
        score += review_score
        
        # Score for service matches (15 points maximum)
        service_matches = metadata.get('total_matches', 0)
        service_score = min(service_matches / 3.0, 1.0) * 15
        score += service_score
        
        # Score per verification (5 points)
        if workshop.is_verified:
            score += 5
        
        # Score by years in business (5 points maximum)
        years = workshop.years_in_business or 0
        years_score = min(years / 20.0, 1.0) * 5
        score += years_score
        
        return round(score, 2)
    
    def get_search_suggestions(self) -> Dict:
        """Get search suggestions based on available data"""
        
        service_counts = {}
        specialty_counts = {}
        city_counts = {}
        
        workshops = self.db.query(Workshop).filter(Workshop.is_active == True).all()
        
        for workshop in workshops:
            if workshop.services:
                for service in workshop.services:
                    service_counts[service] = service_counts.get(service, 0) + 1
            
            if workshop.specialties:
                for specialty in workshop.specialties:
                    specialty_counts[specialty] = specialty_counts.get(specialty, 0) + 1
            
            if workshop.city:
                city_counts[workshop.city] = city_counts.get(workshop.city, 0) + 1
        
        # Create ordered suggestions
        services = [{"type": "service", "value": k, "display_text": k, "count": v} 
                   for k, v in sorted(service_counts.items(), key=lambda x: x[1], reverse=True)]
        
        brands = [{"type": "brand", "value": k, "display_text": k, "count": v}
                 for k, v in sorted(specialty_counts.items(), key=lambda x: x[1], reverse=True)]
        
        cities = [{"type": "city", "value": k, "display_text": k, "count": v}
                 for k, v in sorted(city_counts.items(), key=lambda x: x[1], reverse=True)]
        
        popular_searches = [
            "Oil change nearby",
            "Workshop Toyota",
            "Mechanic open now",
            "Urgent brakes",
            "Verified workshop"
        ]
        
        return {
            "services": services[:10],
            "brands": brands[:10],
            "cities": cities[:10],
            "popular_searches": popular_searches
        }