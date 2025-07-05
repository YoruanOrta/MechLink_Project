import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/RegisterVehicle.css";
import tokenManager from '../utils/tokenManager';

function RegisterVehicle() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  const [formData, setFormData] = useState({
    make: "",
    model: "",
    year: "",
    user_id: localStorage.getItem("user_id"),
    license_plate: "",
    color: "",
    current_mileage: "",
    transmission: "",
    engine_size: "",
    notes: "",
  });

  const [message, setMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setIsSubmitting(true);
  
    try {
      const response = await tokenManager.post("http://localhost:8000/api/v1/vehicles/", formData);
  
      if (response.ok) {
        setMessage("Vehicle registered successfully! 🚗");
        
        // Clear form after successful registration
        setFormData({
          make: "",
          model: "",
          year: "",
          user_id: localStorage.getItem("user_id"),
          license_plate: "",
          color: "",
          current_mileage: "",
          transmission: "",
          engine_size: "",
          notes: "",
        });
        
        // Redirect after a short delay
        setTimeout(() => {
          navigate("/dashboard");
        }, 2000);
      } else {
        const data = await response.json();
        setMessage(data.detail || "Error registering vehicle");
      }
    } catch (err) {
      setMessage("Network error. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="vehicle-form-container">
      <div className="vehicle-form-wrapper">
        <div className="vehicle-brand-section">
          <div className="vehicle-brand-logo">🚗</div>
          <h1 className="vehicle-brand-title">Add Your Vehicle</h1>
          <p className="vehicle-brand-subtitle">
            Register your vehicle to start tracking maintenance, booking appointments, and managing your automotive needs with MechLink.
          </p>
          
          <div className="vehicle-features">
            <div className="vehicle-feature">
              <div className="vehicle-feature-icon">📊</div>
              <div className="vehicle-feature-text">Track maintenance history</div>
            </div>
            <div className="vehicle-feature">
              <div className="vehicle-feature-icon">📅</div>
              <div className="vehicle-feature-text">Schedule service appointments</div>
            </div>
            <div className="vehicle-feature">
              <div className="vehicle-feature-icon">🔔</div>
              <div className="vehicle-feature-text">Get maintenance reminders</div>
            </div>
            <div className="vehicle-feature">
              <div className="vehicle-feature-icon">📱</div>
              <div className="vehicle-feature-text">Access from anywhere</div>
            </div>
          </div>
        </div>

        <div className="vehicle-form-section">
          <button 
            className="vehicle-back-button"
            onClick={() => navigate("/dashboard")}
          >
            ← Back to Dashboard
          </button>

          <div className="vehicle-header">
            <h2>Vehicle Registration</h2>
            <p>Fill in your vehicle details to get started</p>
          </div>

          <form className="vehicle-form" onSubmit={handleSubmit}>
            <div className="vehicle-form-group">
              <input
                type="text"
                name="make"
                placeholder="Make (e.g., Toyota, Honda, Ford)"
                value={formData.make}
                onChange={handleChange}
                required
              />
            </div>

            <div className="vehicle-form-group">
              <input
                type="text"
                name="model"
                placeholder="Model (e.g., Civic, Corolla, F-150)"
                value={formData.model}
                onChange={handleChange}
                required
              />
            </div>

            <div className="vehicle-form-group">
              <input
                type="number"
                name="year"
                placeholder="Year (e.g., 2020)"
                value={formData.year}
                onChange={handleChange}
                min="1900"
                max={new Date().getFullYear() + 1}
                required
              />
            </div>

            <div className="vehicle-form-group">
              <input
                type="text"
                name="license_plate"
                placeholder="License Plate (e.g., ABC-123)"
                value={formData.license_plate}
                onChange={handleChange}
                required
              />
            </div>

            <div className="vehicle-form-group">
              <input
                type="text"
                name="color"
                placeholder="Color (e.g., Red, Blue, Silver)"
                value={formData.color}
                onChange={handleChange}
              />
            </div>

            <div className="vehicle-form-group">
              <input
                type="number"
                name="current_mileage"
                placeholder="Current Mileage (e.g., 50000)"
                value={formData.current_mileage}
                onChange={handleChange}
                min="0"
              />
            </div>

            <div className="vehicle-form-group">
              <input
                type="text"
                name="transmission"
                placeholder="Transmission (e.g., Manual, Automatic)"
                value={formData.transmission}
                onChange={handleChange}
              />
            </div>

            <div className="vehicle-form-group">
              <input
                type="text"
                name="engine_size"
                placeholder="Engine Size (e.g., 2.0L, V6)"
                value={formData.engine_size}
                onChange={handleChange}
              />
            </div>

            <div className="vehicle-form-group full-width">
              <textarea
                name="notes"
                placeholder="Additional Notes (optional - any special details about your vehicle)"
                value={formData.notes}
                onChange={handleChange}
              />
            </div>

            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? '🔄 Registering Vehicle...' : '🚗 Register Vehicle'}
            </button>

            {message && (
              <div className={`message ${message.includes("successfully") ? "success" : "error"}`}>
                {message}
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}

export default RegisterVehicle;