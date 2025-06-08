#!/usr/bin/env python3
"""
Script to update coordinates for existing workshops and insert sample workshops
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.config.database import get_db, SessionLocal
from app.models.workshop import Workshop
from app.services.geolocation_service import GeolocationService

def update_workshop_coordinates():
    """
    Update coordinates for workshops that don't yet have them.

    This function queries the database for workshops with missing latitude or longitude.
    It attempts to fetch coordinates using the GeolocationService. If no result is found
    using the full address, it tries to get coordinates for the city instead.
    """
    db = SessionLocal()
    geo_service = GeolocationService()

    try:
        # Retrieve workshops missing coordinates
        workshops = db.query(Workshop).filter(
            Workshop.latitude.is_(None) | Workshop.longitude.is_(None)
        ).all()

        print(f"Found {len(workshops)} workshops without coordinates")

        for workshop in workshops:
            print(f"\nProcessing: {workshop.name} - {workshop.address}, {workshop.city}")

            # Try geocoding using full address
            address = f"{workshop.address}, {workshop.city}, Puerto Rico"
            coords = geo_service.geocode_address(address)

            if coords:
                lat, lon = coords
                workshop.latitude = lat
                workshop.longitude = lon
                print(f"  ✅ Coordinates found: {lat}, {lon}")
            else:
                print(f"  ❌ Failed to get coordinates")

                # Fallback to using city name only
                city_coords = geo_service.geocode_address(workshop.city, "Puerto Rico")
                if city_coords:
                    lat, lon = city_coords
                    workshop.latitude = lat
                    workshop.longitude = lon
                    print(f"  ⚠️  Using city-level coordinates: {lat}, {lon}")

        # Save all changes to the database
        db.commit()
        print(f"\n✅ Coordinate update completed for {len(workshops)} workshops")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

def add_sample_workshops_with_coordinates():
    """
    Insert predefined sample workshops with coordinates.

    These sample entries represent real-world-like workshops in Puerto Rico.
    Coordinates, services, and other fields are hardcoded for demonstration.
    """
    db = SessionLocal()

    sample_workshops = [
        {
            "name": "Taller AutoExpress Ponce",
            "description": "Quick maintenance specialists offering quality services",
            "address": "Calle Salud #45",
            "city": "Ponce",
            "state": "Puerto Rico",
            "phone": "787-555-0789",
            "email": "info@autoexpressponce.com",
            "latitude": 18.0113,
            "longitude": -66.6140,
            "services": ["Cambio de aceite", "Frenos", "A/C", "Inspección"],
            "specialties": ["Servicio rápido", "Honda", "Toyota"],
            "working_hours": {
                "monday": "7:30-17:30",
                "tuesday": "7:30-17:30", 
                "wednesday": "7:30-17:30",
                "thursday": "7:30-17:30",
                "friday": "7:30-17:30",
                "saturday": "8:00-14:00"
            },
            "years_in_business": 12,
            "is_verified": True
        },
        {
            "name": "Mecánica Caguas Premium",
            "description": "Full-service workshop with advanced technology",
            "address": "Avenida Luis Muñoz Marín #234",
            "city": "Caguas", 
            "state": "Puerto Rico",
            "phone": "787-555-0321",
            "email": "contacto@caguaspremium.com",
            "latitude": 18.2342,
            "longitude": -66.0359,
            "services": ["Motor", "Transmisión", "Suspensión", "Electricidad"],
            "specialties": ["Diagnóstico computarizado", "BMW", "Mercedes"],
            "working_hours": {
                "monday": "8:00-17:00",
                "tuesday": "8:00-17:00",
                "wednesday": "8:00-17:00", 
                "thursday": "8:00-17:00",
                "friday": "8:00-17:00",
                "saturday": "8:00-12:00"
            },
            "years_in_business": 8,
            "is_verified": True
        },
        {
            "name": "Taller Mayagüez Motors",
            "description": "Professional service in Puerto Rico's west region",
            "address": "Carretera 2 KM 159.8",
            "city": "Mayagüez",
            "state": "Puerto Rico", 
            "phone": "787-555-0654",
            "email": "info@mayagueznotors.com",
            "latitude": 18.2013,
            "longitude": -67.1397,
            "services": ["Cambio aceite", "Frenos", "Alineación", "Gomas"],
            "specialties": ["Nissan", "Hyundai", "Kia"],
            "working_hours": {
                "monday": "7:00-16:00",
                "tuesday": "7:00-16:00",
                "wednesday": "7:00-16:00",
                "thursday": "7:00-16:00", 
                "friday": "7:00-16:00",
                "saturday": "7:00-13:00"
            },
            "years_in_business": 20,
            "is_verified": False
        }
    ]

    try:
        for workshop_data in sample_workshops:
            # Check if the workshop already exists
            existing = db.query(Workshop).filter(
                Workshop.name == workshop_data["name"]
            ).first()

            if not existing:
                workshop = Workshop(**workshop_data)
                db.add(workshop)
                print(f"✅ Added: {workshop_data['name']} in {workshop_data['city']}")

        db.commit()
        print(f"\n✅ Sample workshops added successfully")

    except Exception as e:
        print(f"❌ Error adding workshops: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🌍 Updating workshop coordinates...")
    print("=" * 50)

    # First update missing coordinates for existing workshops
    update_workshop_coordinates()

    print("\n" + "=" * 50)
    print("🏪 Adding sample workshops...")

    # Then insert sample workshops
    add_sample_workshops_with_coordinates()

    print("\n🎉 Process completed!")