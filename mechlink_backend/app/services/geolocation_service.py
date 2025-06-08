import math
import requests
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class GeolocationService:
    """Service for managing geolocation and geographic searches"""
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the distance between two points using the Haversine 
        formula returns distance in kilometers
        """
        if not all([lat1, lon1, lat2, lon2]):
            return float('inf')
        
        # Radius of the Earth in kilometers
        R = 6371.0
        
        # Convert degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = (math.sin(dlat / 2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return round(distance, 2)
    
    @staticmethod
    def estimate_travel_time(distance_km: float, avg_speed_kmh: float = 40) -> int:
        """
        Estimate travel time in minutes
        avg_speed_kmh: average city speed (default 40 km/h)
        """
        if distance_km <= 0:
            return 0
        
        travel_time_hours = distance_km / avg_speed_kmh
        travel_time_minutes = int(travel_time_hours * 60)
        
        return max(travel_time_minutes, 1)  # Minimum 1 minute
    
    @staticmethod
    def geocode_address(address: str, city: str = "Puerto Rico") -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates using Nominatim (OpenStreetMap)
        Returns (latitude, longitude) or None if not found
        """
        try:
            # Use Nominatim from OpenStreetMap (free)
            base_url = "https://nominatim.openstreetmap.org/search"
            
            # Build query
            query = f"{address}, {city}"
            
            params = {
                'q': query,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'MechLink/1.0 (contact@mechlink.com)'
            }
            
            response = requests.get(base_url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if data:
                location = data[0]
                lat = float(location['lat'])
                lon = float(location['lon'])
                return (lat, lon)
            
            return None
            
        except Exception as e:
            logger.error(f"Error in geocoding: {str(e)}")
            return None
    
    @staticmethod
    def reverse_geocode(lat: float, lon: float) -> Optional[Dict]:
        """
        Convert coordinates to readable address
        """
        try:
            base_url = "https://nominatim.openstreetmap.org/reverse"
            
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'MechLink/1.0 (contact@mechlink.com)'
            }
            
            response = requests.get(base_url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if 'address' in data:
                address = data['address']
                return {
                    'formatted_address': data.get('display_name', ''),
                    'city': address.get('city') or address.get('town') or address.get('municipality', ''),
                    'state': address.get('state', ''),
                    'country': address.get('country', ''),
                    'postal_code': address.get('postcode', '')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in reverse geocoding: {str(e)}")
            return None
    
    @staticmethod
    def get_puerto_rico_coordinates() -> List[Tuple[str, float, float]]:
        """
        Get coordinates of major cities in Puerto Rico
        For testing and reference data
        """
        return [
            ("San Juan", 18.4655, -66.1057),
            ("Bayamón", 18.3964, -66.1577),
            ("Carolina", 18.3809, -65.9571),
            ("Ponce", 18.0113, -66.6140),
            ("Caguas", 18.2342, -66.0359),
            ("Guaynabo", 18.4178, -66.1103),
            ("Arecibo", 18.4509, -66.7151),
            ("Toa Baja", 18.4448, -66.2540),
            ("Mayagüez", 18.2013, -67.1397),
            ("Trujillo Alto", 18.3629, -66.0115)
        ]
    
    @staticmethod
    def is_valid_coordinates(lat: float, lon: float) -> bool:
        """
        Validate that the coordinates are valid
        """
        return (-90 <= lat <= 90) and (-180 <= lon <= 180)
    
    @staticmethod
    def get_bounding_box(lat: float, lon: float, radius_km: float) -> Dict[str, float]:
        """
        Calculate bounding boxes to optimize database queries
        """
        # Approximation: 1 degree of latitude ≈ 111 km
        # 1 degree of longitude ≈ 111 km * cos(latitude)
        
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * math.cos(math.radians(lat)))
        
        return {
            'min_lat': lat - lat_delta,
            'max_lat': lat + lat_delta,
            'min_lon': lon - lon_delta,
            'max_lon': lon + lon_delta
        }

# Utility functions for use on endpoints
def add_distance_to_workshops(workshops: List[Dict], user_lat: float, user_lon: float) -> List[Dict]:
    """
    Add distance information to a workshop list
    """
    geo_service = GeolocationService()
    
    for workshop in workshops:
        if workshop.get('latitude') and workshop.get('longitude'):
            workshop_lat = float(workshop['latitude'])
            workshop_lon = float(workshop['longitude'])
            
            distance = geo_service.calculate_distance(
                user_lat, user_lon, workshop_lat, workshop_lon
            )
            travel_time = geo_service.estimate_travel_time(distance)
            
            workshop['distance_km'] = distance
            workshop['estimated_travel_time_minutes'] = travel_time
        else:
            workshop['distance_km'] = None
            workshop['estimated_travel_time_minutes'] = None
    
    return workshops

def sort_workshops_by_distance(workshops: List[Dict]) -> List[Dict]:
    """
    Sort workshops by distance (closest first)
    """
    return sorted(workshops, key=lambda x: x.get('distance_km', float('inf')))