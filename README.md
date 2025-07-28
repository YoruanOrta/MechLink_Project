# 🚗 MechLink - Automotive Platform

<div align="center">
    <img src="./mechlink_backend/frontend/public/images/logo_de_mi_app.jpg" alt="MechLink Logo" width="300"/>
</div>

> **The right workshop, right nearby. Never miss a service.**

MechLink is a comprehensive web application designed to connect vehicle owners with trusted automotive workshops in Puerto Rico. Our platform simplifies the process of finding reliable mechanics, booking appointments, and managing vehicle maintenance.

---

## 🌟 Features

- **🔍 Workshop Discovery**: Search and filter workshops by location and service type.
- **📅 Appointment Management**: Book, view, and manage appointments with smart notifications.
- **🚗 Vehicle Management**: Register vehicles and track maintenance history.
- **🔔 Smart Notifications**: Automatic reminders and email confirmations.
- **⭐ Review System**: Rate workshops and read authentic customer reviews.
- **📊 Analytics & Reports**: Track spending and maintenance schedules.

---

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework.
- **SQLAlchemy**: Python SQL toolkit and ORM.
- **SQLite**: Database for development.
- **APScheduler**: Notification scheduling system.

### Frontend
- **React.js**: User interface library.
- **HTML5/CSS3**: Modern web standards.
- **JavaScript ES6+**: Modern JavaScript features.

---

## 🚀 Quick Start

### Prerequisites
- **Python**: Version 3.13+
- **Node.js**: Version 18+

### Backend Setup
```bash
# Clone the repository
git clone https://github.com/YoruanOrta/mechlink.git
cd mechlink

# Create virtual environment
python -m venv mechlink_env
source mechlink_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Access the Application
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🏗️ Project Structure

```plaintext
mechlink/
├── app/                    # Backend application
│   ├── api/v1/             # API endpoints
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   └── config/             # Configuration
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   └── styles/         # CSS styles
│   └── public/
└── requirements.txt
```

---

## 👥 Team

- **Yoruan Orta Bonilla**: Backend Developer.
- **Emanuel Mendoza**: Frontend Developer.

---

## 🐛 Known Issues

- Favorites system uses `localStorage` (backend persistence in development).
- Geographic search backend is ready, frontend UI is pending.
- Mobile optimization improvements are ongoing.

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 🙏 Acknowledgments

- **Holberton School**: For providing the educational foundation.
- **Puerto Rico automotive community**: For inspiration and feedback.

---

<div align="center">
    Made with ❤️ for the Puerto Rican automotive community  
</div>