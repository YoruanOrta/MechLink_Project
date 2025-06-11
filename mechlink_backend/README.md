# MechLink Backend 🚗⚙️

A vehicle management platform API for Puerto Rico. Connect with workshops, schedule appointments, and get maintenance reminders.

### What it does
- User registration and login
- Vehicle management 
- Workshop directory
- Appointment booking
- Email notifications
- Puerto Rico map integration

### Tech Stack
- FastAPI + Python 3.13
- SQLAlchemy + SQLite
- JWT Authentication
- SMTP Email System

### Quick Start

Install and run:
```bash
pip install -r requirements.txt
uvicorn app.main:main --reload --port 8000
```

Check it works:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Main Endpoints

```
POST /api/v1/auth/register     # Sign up
POST /api/v1/auth/login-json   # Login
GET  /api/v1/vehicles/         # Your vehicles
GET  /api/v1/workshops/        # Find workshops
POST /api/v1/appointments/     # Book appointment
GET  /api/v1/notifications/    # Your messages
```

### Email Setup

Get Gmail app password and update `notification_service.py`:
```python
smtp_user = "your-email@gmail.com"
smtp_password = "your-app-password"
```

Test it:
```bash
curl -X POST "http://localhost:8000/api/v1/notifications/test" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"channel":"email","test_type":"system_test"}'
```

### Features Working
- ✅ User auth with JWT
- ✅ Vehicle CRUD
- ✅ Workshop search
- ✅ Appointment system
- ✅ Real email notifications
- ✅ Puerto Rico maps
- ✅ Maintenance tracking

### Database
Uses SQLite by default. Easy to switch to PostgreSQL for production.

### Status
Ready to use! 🚀 All major features implemented and tested.