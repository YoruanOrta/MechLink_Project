from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.api.v1 import notifications
from app.config.database import Base, engine, get_db
from app.config.settings import settings
from app.api.v1 import users, vehicles, auth, maintenance, workshops, appointments, geographic

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="API para gestión de mantenimiento vehicular",
    version=settings.VERSION,
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:49998", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:49998",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Authorization", 
        "Content-Type", 
        "Accept",
        "Origin",
        "X-Requested-With"
    ],
    expose_headers=["*"]
)

# Incluir routers
app.include_router(users.router, prefix="/api/v1")
app.include_router(vehicles.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(maintenance.router, prefix="/api/v1")
app.include_router(workshops.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")
app.include_router(geographic.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "message": "¡MechLink API funcionando! 🚗⚙️",
        "version": settings.VERSION,
        "docs": "/docs",
        "database": "Connected",
        "endpoints": {
            "users": "/api/v1/users",
            "vehicles": "/api/v1/vehicles",
            "workshops": "/api/v1/workshops",
            "appointments": "/api/v1/appointments",
            "geographic": "/api/v1/geographic",
            "maintenance": "/api/v1/maintenance",
            "notifications": "/api/v1/notifications",
            "auth": "/api/v1/auth",
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {
            "status": "healthy", 
            "api": "MechLink",
            "database": "Connected ✅",
            "version": settings.VERSION
        }
    except Exception as e:
        return {
            "status": "error",
            "api": "MechLink", 
            "database": f"Error: {str(e)}",
            "version": settings.VERSION
        }

@app.get("/api/database/info")
def database_info(db: Session = Depends(get_db)):
    try:
        result = db.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in result.fetchall()]
        
        user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0] if 'users' in tables else 0
        vehicle_count = db.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0] if 'vehicles' in tables else 0
        workshop_count = db.execute("SELECT COUNT(*) FROM workshops").fetchone()[0] if 'workshops' in tables else 0
        appointment_count = db.execute("SELECT COUNT(*) FROM appointments").fetchone()[0] if 'appointments' in tables else 0
        notification_count = db.execute("SELECT COUNT(*) FROM notifications").fetchone()[0] if 'notifications' in tables else 0  # ✅ AGREGAR
        
        return {
            "database_type": "SQLite",
            "database_file": "mechlink.db",
            "tables": tables,
            "counts": {
                "users": user_count,
                "vehicles": vehicle_count,
                "workshops": workshop_count,
                "appointments": appointment_count,
                "notifications": notification_count
            },
            "status": "Connected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)