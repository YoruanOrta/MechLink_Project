from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from decimal import Decimal

from app.config.database import get_db
from app.models.workshop import Workshop
from app.models.user import User
from app.services.advanced_search_service import AdvancedSearchService

from app.schemas.workshop_schemas import (
    AdvancedGeographicSearch,
    AdvancedSearchResult,
    ServiceSearchRequest,
    BrandSpecialtySearchRequest,
    OpenNowSearchRequest,
    SearchSuggestionsResponse,
    WorkshopWithAdvancedInfo
)
from app.services.geolocation_service import (
    GeolocationService, 
    add_distance_to_workshops, 
    sort_workshops_by_distance
)
from app.schemas.workshop_schemas import (
    WorkshopWithDistance,
    GeographicSearchResult,
    GeocodeRequest,
    GeocodeResponse,
    NearbyWorkshopsRequest,
    LocationInfo,
    DistanceCalculation
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/geographic", tags=["geographic-search"])

# === SEARCH ENDPOINTS ===

@router.post("/search", response_model=GeographicSearchResult)
def geographic_search(
    latitude: Optional[float] = Query(None, ge=-90, le=90, description="Latitude"),
    longitude: Optional[float] = Query(None, ge=-180, le=180, description="Longitude"),
    address: Optional[str] = Query(None, description="Address to search"),
    city: Optional[str] = Query("Puerto Rico", description="City"),
    radius_km: float = Query(10, ge=1, le=100, description="Radius in km"),
    max_results: int = Query(20, ge=1, le=100, description="Maximum results"),
    services: Optional[str] = Query(None, description="Comma-separated services"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    verified_only: bool = Query(False, description="Only verified"),
    db: Session = Depends(get_db)
):
    """
    Geographic search for workshops
    Can use direct coordinates or address geocoding
    """
    
    geo_service = GeolocationService()
    search_lat = latitude
    search_lon = longitude
    
    # If no coordinates, perform geocoding
    if not search_lat or not search_lon:
        if not address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coordinates (lat, lon) or address are required for search"
            )
        
        coords = geo_service.geocode_address(address, city)
        if not coords:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not find location: {address}, {city}"
            )
        
        search_lat, search_lon = coords
    
    # Validate coordinates
    if not geo_service.is_valid_coordinates(search_lat, search_lon):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coordinates"
        )
    
    # Get bounding box for optimized query
    bbox = geo_service.get_bounding_box(search_lat, search_lon, radius_km)
    
    # Base query
    query = db.query(Workshop).filter(
        and_(
            Workshop.is_active == True,
            Workshop.latitude.between(bbox['min_lat'], bbox['max_lat']),
            Workshop.longitude.between(bbox['min_lon'], bbox['max_lon'])
        )
    )
    
    # Apply additional filters
    if min_rating is not None:
        query = query.filter(Workshop.rating_average >= min_rating)
    
    if verified_only:
        query = query.filter(Workshop.is_verified == True)
    
    # TODO: Implement service filtering when available in DB
    # if services:
    #     service_list = [s.strip() for s in services.split(',')]
    #     query = query.filter(Workshop.services.contains(service_list))
    
    workshops = query.all()
    
    # Convert to dictionaries and calculate distances
    workshops_data = []
    workshops_in_radius = []
    
    for workshop in workshops:
        workshop_dict = {
            "id": workshop.id,
            "name": workshop.name,
            "description": workshop.description,
            "address": workshop.address,
            "city": workshop.city,
            "state": workshop.state,
            "postal_code": workshop.postal_code,
            "phone": workshop.phone,
            "email": workshop.email,
            "website": workshop.website,
            "latitude": float(workshop.latitude) if workshop.latitude else None,
            "longitude": float(workshop.longitude) if workshop.longitude else None,
            "services": workshop.services or [],
            "specialties": workshop.specialties or [],
            "working_hours": workshop.working_hours or {},
            "rating_average": float(workshop.rating_average),
            "total_reviews": workshop.total_reviews,
            "images": workshop.images or [],
            "certifications": workshop.certifications or [],
            "years_in_business": workshop.years_in_business,
            "is_active": workshop.is_active,
            "is_verified": workshop.is_verified,
            "created_at": workshop.created_at
        }
        
        # Calculate distance if the workshop has coordinates
        if workshop.latitude and workshop.longitude:
            distance = geo_service.calculate_distance(
                search_lat, search_lon,
                float(workshop.latitude), float(workshop.longitude)
            )
            
            # Only include if within radius
            if distance <= radius_km:
                travel_time = geo_service.estimate_travel_time(distance)
                workshop_dict['distance_km'] = distance
                workshop_dict['estimated_travel_time_minutes'] = travel_time
                workshops_in_radius.append(workshop_dict)
    
    # Sort by distance
    workshops_in_radius.sort(key=lambda x: x['distance_km'])
    
    # Limit results
    workshops_in_radius = workshops_in_radius[:max_results]
    
    return {
        "workshops": workshops_in_radius,
        "search_center": {"latitude": search_lat, "longitude": search_lon},
        "total_found": len(workshops_in_radius),
        "search_radius_km": radius_km
    }

@router.get("/nearby", response_model=List[WorkshopWithDistance])
def get_nearby_workshops(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10, ge=1, le=100),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get workshops near a specific location"""
    
    geo_service = GeolocationService()
    
    # Validate coordinates
    if not geo_service.is_valid_coordinates(latitude, longitude):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coordinates"
        )
    
    # Bounding box for optimized query
    bbox = geo_service.get_bounding_box(latitude, longitude, radius_km)
    
    # Query with bounding box
    workshops = db.query(Workshop).filter(
        and_(
            Workshop.is_active == True,
            Workshop.latitude.between(bbox['min_lat'], bbox['max_lat']),
            Workshop.longitude.between(bbox['min_lon'], bbox['max_lon']),
            Workshop.latitude.isnot(None),
            Workshop.longitude.isnot(None)
        )
    ).all()
    
    # Convert to dictionaries and filter by exact radius
    workshops_with_distance = []
    
    for workshop in workshops:
        distance = geo_service.calculate_distance(
            latitude, longitude,
            float(workshop.latitude), float(workshop.longitude)
        )
        
        if distance <= radius_km:
            workshop_dict = {
                "id": workshop.id,
                "name": workshop.name,
                "description": workshop.description,
                "address": workshop.address,
                "city": workshop.city,
                "state": workshop.state,
                "postal_code": workshop.postal_code,
                "phone": workshop.phone,
                "email": workshop.email,
                "website": workshop.website,
                "latitude": float(workshop.latitude),
                "longitude": float(workshop.longitude),
                "services": workshop.services or [],
                "specialties": workshop.specialties or [],
                "working_hours": workshop.working_hours or {},
                "rating_average": float(workshop.rating_average),
                "total_reviews": workshop.total_reviews,
                "images": workshop.images or [],
                "certifications": workshop.certifications or [],
                "years_in_business": workshop.years_in_business,
                "is_active": workshop.is_active,
                "is_verified": workshop.is_verified,
                "created_at": workshop.created_at,
                "distance_km": distance,
                "estimated_travel_time_minutes": geo_service.estimate_travel_time(distance)
            }
            workshops_with_distance.append(workshop_dict)
    
    # Sort by distance and limit results
    workshops_with_distance.sort(key=lambda x: x['distance_km'])
    return workshops_with_distance[:limit]

# === GEOCODING ENDPOINTS ===

@router.post("/geocode", response_model=GeocodeResponse)
def geocode_address(request: GeocodeRequest):
    """Convert address to coordinates"""
    
    geo_service = GeolocationService()
    
    try:
        coords = geo_service.geocode_address(request.address, request.city)
        
        if coords:
            lat, lon = coords
            # Also retrieve formatted address
            location_info = geo_service.reverse_geocode(lat, lon)
            
            return {
                "success": True,
                "latitude": lat,
                "longitude": lon,
                "formatted_address": location_info.get('formatted_address') if location_info else None
            }
        else:
            return {
                "success": False,
                "error_message": f"Could not find the location: {request.address}, {request.city}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error_message": f"Error en geocoding: {str(e)}"
        }

@router.get("/reverse-geocode", response_model=dict)
def reverse_geocode(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180)
):
    """Convert coordinates to a readable address"""
    
    geo_service = GeolocationService()
    
    if not geo_service.is_valid_coordinates(latitude, longitude):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coordinates"
        )
    
    location_info = geo_service.reverse_geocode(latitude, longitude)
    
    if not location_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not retrieve location information for these coordinates"
        )
    return location_info

# === DISTANCE CALCULATION ENDPOINTS ===

@router.get("/distance")
def calculate_distance(
    lat1: float = Query(..., ge=-90, le=90, description="Origin latitude"),
    lon1: float = Query(..., ge=-180, le=180, description="Origin longitude"),
    lat2: float = Query(..., ge=-90, le=90, description="Destination latitude"),
    lon2: float = Query(..., ge=-180, le=180, description="Destination longitude")
):
    """Calculate distance between two points"""
    
    geo_service = GeolocationService()
    
    # Validate coordinates
    if not all([
        geo_service.is_valid_coordinates(lat1, lon1),
        geo_service.is_valid_coordinates(lat2, lon2)
    ]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coordinates"
        )
    
    distance = geo_service.calculate_distance(lat1, lon1, lat2, lon2)
    travel_time = geo_service.estimate_travel_time(distance)
    
    return {
        "distance_km": distance,
        "estimated_travel_time_minutes": travel_time,
        "from_coordinates": {"latitude": lat1, "longitude": lon1},
        "to_coordinates": {"latitude": lat2, "longitude": lon2}
    }

# === UTILITY ENDPOINTS ===

@router.get("/cities/puerto-rico")
def get_puerto_rico_cities():
    """Get coordinates of main cities in Puerto Rico"""
    
    geo_service = GeolocationService()
    cities = geo_service.get_puerto_rico_coordinates()
    
    return [
        {
            "name": city,
            "latitude": lat,
            "longitude": lon
        }
        for city, lat, lon in cities
    ]

# === ADVANCED SEARCH ENDPOINTS ===

@router.post("/search-by-services", response_model=List[WorkshopWithAdvancedInfo])
def search_by_services(
    request: ServiceSearchRequest,
    db: Session = Depends(get_db)
):
    """Specific search for required services"""
    
    geo_service = GeolocationService()
    search_service = AdvancedSearchService(db)
    
    # Validate coordinates
    if not geo_service.is_valid_coordinates(request.latitude, request.longitude):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coordinates"
        )
    
    # Bounding box
    bbox = geo_service.get_bounding_box(request.latitude, request.longitude, request.radius_km)
    
    # Retrieve workshops in the area
    workshops = db.query(Workshop).filter(
        and_(
            Workshop.is_active == True,
            Workshop.latitude.between(bbox['min_lat'], bbox['max_lat']),
            Workshop.longitude.between(bbox['min_lon'], bbox['max_lon']),
            Workshop.latitude.isnot(None),
            Workshop.longitude.isnot(None)
        )
    ).all()
    
    # Filter by distance
    workshops_in_radius = []
    for workshop in workshops:
        distance = geo_service.calculate_distance(
            request.latitude, request.longitude,
            float(workshop.latitude), float(workshop.longitude)
        )
        if distance <= request.radius_km:
            workshops_in_radius.append(workshop)
    
    # Filter by services
    service_results = search_service.filter_by_services(
        workshops_in_radius,
        request.services,
        match_all=request.match_all_services
    )
    
    # Create response
    results = []
    for workshop, metadata in service_results:
        distance = geo_service.calculate_distance(
            request.latitude, request.longitude,
            float(workshop.latitude), float(workshop.longitude)
        )
        
        result = {
            "id": workshop.id,
            "name": workshop.name,
            "description": workshop.description,
            "address": workshop.address,
            "city": workshop.city,
            "state": workshop.state,
            "phone": workshop.phone,
            "email": workshop.email,
            "latitude": float(workshop.latitude),
            "longitude": float(workshop.longitude),
            "services": workshop.services or [],
            "specialties": workshop.specialties or [],
            "working_hours": workshop.working_hours or {},
            "rating_average": float(workshop.rating_average),
            "total_reviews": workshop.total_reviews,
            "is_verified": workshop.is_verified,
            "years_in_business": workshop.years_in_business,
            "distance_km": distance,
            "estimated_travel_time_minutes": geo_service.estimate_travel_time(distance),
            "matching_services": metadata["matching_services"],
            "search_score": metadata["total_matches"] * 10,
            "is_active": workshop.is_active,
            "created_at": workshop.created_at,
        }
        results.append(result)
    
    # Sort by relevance (more matches first, then by distance)
    results.sort(key=lambda x: (-x["search_score"], x["distance_km"]))
    
    return results

@router.post("/search-by-brand", response_model=List[WorkshopWithAdvancedInfo])
def search_by_brand_specialty(
    request: BrandSpecialtySearchRequest,
    db: Session = Depends(get_db)
):
    """Search by specific brand specialty"""
    
    geo_service = GeolocationService()
    search_service = AdvancedSearchService(db)
    
    # Validate coordinates
    if not geo_service.is_valid_coordinates(request.latitude, request.longitude):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coordinates"
        )
    
    # Bounding box
    bbox = geo_service.get_bounding_box(request.latitude, request.longitude, request.radius_km)
    
    # Retrieve workshops
    workshops = db.query(Workshop).filter(
        and_(
            Workshop.is_active == True,
            Workshop.latitude.between(bbox['min_lat'], bbox['max_lat']),
            Workshop.longitude.between(bbox['min_lon'], bbox['max_lon']),
            Workshop.latitude.isnot(None),
            Workshop.longitude.isnot(None)
        )
    ).all()
    
    # Filter by distance
    workshops_in_radius = []
    for workshop in workshops:
        distance = geo_service.calculate_distance(
            request.latitude, request.longitude,
            float(workshop.latitude), float(workshop.longitude)
        )
        if distance <= request.radius_km:
            workshops_in_radius.append(workshop)
    
    # Filter by brand specialty
    specialty_results = search_service.filter_by_specialties(
        workshops_in_radius,
        [request.car_brand]
    )
    
    # Create response
    results = []
    for workshop, metadata in specialty_results:
        distance = geo_service.calculate_distance(
            request.latitude, request.longitude,
            float(workshop.latitude), float(workshop.longitude)
        )
        
        result = {
            "id": workshop.id,
            "name": workshop.name,
            "description": workshop.description,
            "address": workshop.address,
            "city": workshop.city,
            "state": workshop.state,
            "postal_code": workshop.postal_code,
            "phone": workshop.phone,
            "email": workshop.email,
            "website": workshop.website,
            "latitude": float(workshop.latitude),
            "longitude": float(workshop.longitude),
            "services": workshop.services or [],
            "specialties": workshop.specialties or [],
            "working_hours": workshop.working_hours or {},
            "rating_average": float(workshop.rating_average),
            "total_reviews": workshop.total_reviews,
            "images": workshop.images or [],
            "certifications": workshop.certifications or [],
            "years_in_business": workshop.years_in_business,
            "is_active": workshop.is_active,
            "is_verified": workshop.is_verified,
            "created_at": workshop.created_at,
            "distance_km": distance,
            "estimated_travel_time_minutes": geo_service.estimate_travel_time(distance),
            "matching_specialties": metadata["matching_specialties"],
            "search_score": metadata["brand_matches"] * 15
        }
        results.append(result)
    
    # Sort by distance
    results.sort(key=lambda x: x["distance_km"])
    
    return results

@router.post("/search-open-now", response_model=List[WorkshopWithAdvancedInfo])
def search_open_now(
    request: OpenNowSearchRequest,
    db: Session = Depends(get_db)
):
    """Search for workshops open now"""
    
    geo_service = GeolocationService()
    search_service = AdvancedSearchService(db)
    
    # Validate coordinates
    if not geo_service.is_valid_coordinates(request.latitude, request.longitude):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coordinates"
        )
    
    # Bounding box
    bbox = geo_service.get_bounding_box(request.latitude, request.longitude, request.radius_km)
    
    # Retrieve workshops
    workshops = db.query(Workshop).filter(
        and_(
            Workshop.is_active == True,
            Workshop.latitude.between(bbox['min_lat'], bbox['max_lat']),
            Workshop.longitude.between(bbox['min_lon'], bbox['max_lon']),
            Workshop.latitude.isnot(None),
            Workshop.longitude.isnot(None)
        )
    ).all()
    
    # Filter by distance and availability
    results = []
    for workshop in workshops:
        distance = geo_service.calculate_distance(
            request.latitude, request.longitude,
            float(workshop.latitude), float(workshop.longitude)
        )
        
        if distance <= request.radius_km:
            # Check availability
            availability = search_service.check_workshop_availability(
                workshop,
                request.current_time,
                request.day_of_week
            )
            
            # Only include if open
            if availability["is_open_now"]:
                result = {
                    "id": workshop.id,
                    "name": workshop.name,
                    "description": workshop.description,
                    "address": workshop.address,
                    "city": workshop.city,
                    "phone": workshop.phone,
                    "latitude": float(workshop.latitude),
                    "longitude": float(workshop.longitude),
                    "services": workshop.services or [],
                    "working_hours": workshop.working_hours or {},
                    "rating_average": float(workshop.rating_average),
                    "total_reviews": workshop.total_reviews,
                    "is_verified": workshop.is_verified,
                    "distance_km": distance,
                    "estimated_travel_time_minutes": geo_service.estimate_travel_time(distance),
                    "availability": availability,
                    "search_score": 50 + (10 if workshop.is_verified else 0),  # Bonus for being open
                    "state": workshop.state,
                    "postal_code": workshop.postal_code,
                    "email": workshop.email,
                    "website": workshop.website,
                    "working_hours": workshop.working_hours or {},
                    "images": workshop.images or [],
                    "certifications": workshop.certifications or [],
                    "is_active": workshop.is_active,
                    "created_at": workshop.created_at,
                }
                results.append(result)
    
    # Sort by distance
    results.sort(key=lambda x: x["distance_km"])
    
    return results

@router.get("/search-suggestions", response_model=SearchSuggestionsResponse)
def get_search_suggestions(db: Session = Depends(get_db)):
    """Get suggestions for searches"""
    
    search_service = AdvancedSearchService(db)
    suggestions = search_service.get_search_suggestions()
    
    return suggestions

@router.get("/filter-options")
def get_filter_options(db: Session = Depends(get_db)):
    """Get available options for filters"""
    
    # Retrieve unique values from the database
    workshops = db.query(Workshop).filter(Workshop.is_active == True).all()
    
    all_services = set()
    all_specialties = set()
    all_cities = set()
    
    for workshop in workshops:
        if workshop.services:
            all_services.update(workshop.services)
        if workshop.specialties:
            all_specialties.update(workshop.specialties)
        if workshop.city:
            all_cities.add(workshop.city)
    
    return {
        "services": sorted(list(all_services)),
        "specialties": sorted(list(all_specialties)),
        "cities": sorted(list(all_cities)),
        "rating_options": [1, 2, 3, 4, 5],
        "radius_options": [5, 10, 15, 20, 25, 30, 50, 100],
        "sort_options": [
            {"value": "distance", "label": "Distance"},
            {"value": "rating", "label": "Rating"},
            {"value": "reviews", "label": "Number of reviews"},
            {"value": "years", "label": "Years in business"},
            {"value": "score", "label": "Relevance"}
        ]
    }
@router.post("/advanced-search", response_model=AdvancedSearchResult)
def advanced_geographic_search(
    search_params: AdvancedGeographicSearch,
    db: Session = Depends(get_db)
):
    """
    Advanced geographic search with multiple intelligent filters
    """
    
    geo_service = GeolocationService()
    search_service = AdvancedSearchService(db)
    
    # Determine search coordinates
    search_lat = search_params.latitude
    search_lon = search_params.longitude
    
    if not search_lat or not search_lon:
        if not search_params.address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coordinates or address are required for the search"
            )
        
        coords = geo_service.geocode_address(search_params.address, search_params.city)
        if not coords:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not find the location: {search_params.address}"
            )
        
        search_lat, search_lon = coords
    
    # Bounding box for optimized query
    bbox = geo_service.get_bounding_box(search_lat, search_lon, search_params.radius_km)
    
    # Base query with basic filters
    query = db.query(Workshop).filter(
        and_(
            Workshop.is_active == True,
            Workshop.latitude.between(bbox['min_lat'], bbox['max_lat']),
            Workshop.longitude.between(bbox['min_lon'], bbox['max_lon']),
            Workshop.latitude.isnot(None),
            Workshop.longitude.isnot(None)
        )
    )
    
    # Apply basic filters
    if search_params.min_rating is not None:
        query = query.filter(Workshop.rating_average >= search_params.min_rating)
    
    if search_params.min_reviews is not None:
        query = query.filter(Workshop.total_reviews >= search_params.min_reviews)
    
    if search_params.verified_only:
        query = query.filter(Workshop.is_verified == True)
    
    if search_params.min_years_in_business is not None:
        query = query.filter(Workshop.years_in_business >= search_params.min_years_in_business)
    
    if search_params.max_years_in_business is not None:
        query = query.filter(Workshop.years_in_business <= search_params.max_years_in_business)
    
    workshops = query.all()
    
    # Filter by exact distance
    workshops_in_radius = []
    for workshop in workshops:
        distance = geo_service.calculate_distance(
            search_lat, search_lon,
            float(workshop.latitude), float(workshop.longitude)
        )
        
        if distance <= search_params.radius_km:
            workshops_in_radius.append((workshop, {"distance_km": distance}))
    
    # Apply advanced filters
    filtered_workshops = workshops_in_radius
    
    # Filter by services
    if search_params.required_services or search_params.preferred_services:
        workshops_only = [w[0] for w in filtered_workshops]
        service_results = search_service.filter_by_services(
            workshops_only,
            search_params.required_services or [],
            search_params.preferred_services,
            match_all=True
        )
        
        # Combine metadata
        service_dict = {w.id: metadata for w, metadata in service_results}
        filtered_workshops = []
        for workshop, dist_meta in workshops_in_radius:
            if workshop.id in service_dict:
                combined_meta = {**dist_meta, **service_dict[workshop.id]}
                filtered_workshops.append((workshop, combined_meta))
    
    # Filter by specialties
    if search_params.car_brands or search_params.specializations:
        workshops_only = [w[0] for w in filtered_workshops]
        specialty_results = search_service.filter_by_specialties(
            workshops_only,
            search_params.car_brands or [],
            search_params.specializations
        )
        
        specialty_dict = {w.id: metadata for w, metadata in specialty_results}
        temp_filtered = []
        for workshop, existing_meta in filtered_workshops:
            if workshop.id in specialty_dict:
                combined_meta = {**existing_meta, **specialty_dict[workshop.id]}
                temp_filtered.append((workshop, combined_meta))
        filtered_workshops = temp_filtered
    
    # Apply schedule filters
    if search_params.open_now or search_params.day_of_week or search_params.time_of_day:
        temp_filtered = []
        for workshop, metadata in filtered_workshops:
            availability = search_service.check_workshop_availability(
                workshop, 
                search_params.time_of_day,
                search_params.day_of_week
            )
            
            # If it requires being open now
            if search_params.open_now and not availability["is_open_now"]:
                continue
            
            metadata["availability"] = availability
            temp_filtered.append((workshop, metadata))
        
        filtered_workshops = temp_filtered
    
    # Calculate scores and create response
    workshops_with_info = []
    search_params_dict = search_params.dict()
    
    for workshop, metadata in filtered_workshops:
        # Calculate travel time
        travel_time = geo_service.estimate_travel_time(metadata["distance_km"])
        
        # Calculate relevance score
        search_score = search_service.calculate_search_score(workshop, metadata, search_params_dict)
        
        workshop_info = {
            "id": workshop.id,
            "name": workshop.name,
            "description": workshop.description,
            "address": workshop.address,
            "city": workshop.city,
            "state": workshop.state,
            "postal_code": workshop.postal_code,
            "phone": workshop.phone,
            "email": workshop.email,
            "website": workshop.website,
            "latitude": float(workshop.latitude),
            "longitude": float(workshop.longitude),
            "services": workshop.services or [],
            "specialties": workshop.specialties or [],
            "working_hours": workshop.working_hours or {},
            "rating_average": float(workshop.rating_average),
            "total_reviews": workshop.total_reviews,
            "images": workshop.images or [],
            "certifications": workshop.certifications or [],
            "years_in_business": workshop.years_in_business,
            "is_active": workshop.is_active,
            "is_verified": workshop.is_verified,
            "created_at": workshop.created_at,
            "distance_km": metadata["distance_km"],
            "estimated_travel_time_minutes": travel_time,
            "matching_services": metadata.get("matching_services", []),
            "matching_specialties": metadata.get("matching_specialties", []),
            "search_score": search_score,
            "availability": metadata.get("availability")
        }
        
        workshops_with_info.append(workshop_info)
    
    # Sort results
    sort_key = search_params.sort_by or "distance"
    reverse_order = search_params.sort_order == "desc"
    
    if sort_key == "distance":
        workshops_with_info.sort(key=lambda x: x["distance_km"], reverse=reverse_order)
    elif sort_key == "rating":
        workshops_with_info.sort(key=lambda x: x["rating_average"], reverse=reverse_order)
    elif sort_key == "reviews":
        workshops_with_info.sort(key=lambda x: x["total_reviews"], reverse=reverse_order)
    elif sort_key == "years":
        workshops_with_info.sort(key=lambda x: x["years_in_business"] or 0, reverse=reverse_order)
    elif sort_key == "score":
        workshops_with_info.sort(key=lambda x: x["search_score"], reverse=True)
    
    # Limit results
    workshops_with_info = workshops_with_info[:search_params.max_results]
    
    return {
        "workshops": workshops_with_info,
        "search_center": {"latitude": search_lat, "longitude": search_lon},
        "total_found": len(workshops_with_info),
        "search_radius_km": search_params.radius_km,
        "filters_applied": {
            "services": search_params.required_services or [],
            "car_brands": search_params.car_brands or [],
            "min_rating": search_params.min_rating,
            "verified_only": search_params.verified_only,
            "open_now": search_params.open_now
        },
        "search_metadata": {
            "sort_by": sort_key,
            "sort_order": search_params.sort_order,
            "total_workshops_in_radius": len(workshops_in_radius)
        }
    }
