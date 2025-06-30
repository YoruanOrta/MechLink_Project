import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import tokenManager from '../utils/tokenManager';
import "./BookAppointment.css";

function BookAppointment() {
  const navigate = useNavigate();
  const [workshops, setWorkshops] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [formData, setFormData] = useState({
    workshop_id: "",
    vehicle_id: "",
    service_type: "",
    appointment_date: "",
    appointment_time: "",
    notes: "",
  });
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  // ✅ Fetch user's vehicles using tokenManager
  useEffect(() => {
    const fetchVehicles = async () => {
      try {
        const response = await tokenManager.get("http://localhost:8000/api/v1/vehicles/");
        
        if (response.ok) {
          const data = await response.json();
          if (Array.isArray(data)) {
            setVehicles(data);
          } else {
            console.error("Unexpected vehicles data:", data);
            setVehicles([]);
            setMessage("Failed to load vehicles (invalid response).");
          }
        } else {
          setMessage("Failed to load vehicles.");
        }
      } catch (error) {
        console.error("Error fetching vehicles:", error);
        setMessage("Failed to load vehicles.");
      }
    };

    fetchVehicles();
  }, []);

  // ✅ Fetch workshops using tokenManager
  useEffect(() => {
    const fetchWorkshops = async () => {
      try {
        const response = await tokenManager.get("http://localhost:8000/api/v1/workshops/");
        
        if (response.ok) {
          const data = await response.json();
          if (Array.isArray(data)) {
            setWorkshops(data);
          } else {
            console.error("Unexpected workshops data:", data);
            setWorkshops([]);
            setMessage("Failed to load workshops (invalid response).");
          }
        } else {
          setMessage("Failed to load workshops.");
        }
      } catch (error) {
        console.error("Error fetching workshops:", error);
        setMessage("Failed to load workshops.");
      }
    };

    fetchWorkshops();
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setLoading(true);

    const { appointment_date, appointment_time, ...rest } = formData;
    const appointment_datetime = `${appointment_date}T${appointment_time}`;

    try {
      const response = await tokenManager.post("http://localhost:8000/api/v1/appointments/", {
        ...rest, 
        appointment_datetime
      });

      if (response.ok) {
        const responseData = await response.json();
        setMessage("Appointment booked successfully 📅");
        
        setTimeout(() => {
          navigate("/dashboard");
        }, 2000);
      } else {
        const errorData = await response.json();
        console.error("Error response:", errorData);
        
        if (typeof errorData.detail === 'string') {
          setMessage(errorData.detail);
        } else if (Array.isArray(errorData.detail)) {
          setMessage(errorData.detail.map(err => err.msg).join(', '));
        } else {
          setMessage("Error booking appointment.");
        }
      }
    } catch (error) {
      console.error("Network error:", error);
      setMessage("Network error.");
      } finally {
        setLoading(false);
    }
  };

  return (
    <div className="appointment-form-container">
      <div className="appointment-form-wrapper">
        <button onClick={() => navigate("/dashboard")} className="back-button">
          ← Back to Dashboard
        </button>
        
        <h2>📅 Book Appointment</h2>
        
        <form className="appointment-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="workshop">Select Workshop:</label>
            <select 
              id="workshop"
              name="workshop_id" 
              required 
              onChange={handleChange}
              value={formData.workshop_id}
            >
              <option value="">-- Choose a workshop --</option>
              {Array.isArray(workshops) &&
                workshops.map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.name} - {w.city}
                  </option>
                ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="vehicle">Select Vehicle:</label>
            <select 
              id="vehicle"
              name="vehicle_id" 
              required 
              onChange={handleChange}
              value={formData.vehicle_id}
            >
              <option value="">-- Choose a vehicle --</option>
              {Array.isArray(vehicles) &&
                vehicles.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.make} {v.model} ({v.year})
                  </option>
                ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="service">Select Service:</label>
            <select 
              id="service"
              name="service_type" 
              required 
              onChange={handleChange}
              value={formData.service_type}
            >
              <option value="">-- Choose a service --</option>
              <option value="Oil Change">Oil Change</option>
              <option value="Brake Service">Brake Service</option>
              <option value="AC Repair">AC Repair</option>
              <option value="Tire Service">Tire Service</option>
              <option value="Engine Repair">Engine Repair</option>
              <option value="Transmission">Transmission</option>
              <option value="General Maintenance">General Maintenance</option>
              <option value="Inspection">Inspection</option>
              <option value="Wheel Alignment">Wheel Alignment</option>
            </select>
          </div>

          <div className="datetime-grid">
            <div className="form-group">
              <label htmlFor="date">Appointment Date:</label>
              <input 
                type="date" 
                id="date"
                name="appointment_date" 
                required 
                onChange={handleChange}
                value={formData.appointment_date}
                min={new Date().toISOString().split('T')[0]}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="time">Appointment Time:</label>
              <input 
                type="time" 
                id="time"
                name="appointment_time" 
                required 
                onChange={handleChange}
                value={formData.appointment_time}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="notes">Additional Notes (Optional):</label>
            <textarea 
              id="notes"
              name="notes" 
              placeholder="Any specific requirements or additional information..."
              onChange={handleChange}
              value={formData.notes}
              rows="4"
            ></textarea>
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Booking...' : '📅 Book Appointment'}
          </button>
        </form>
        
        {message && (
          <div className={`message ${message.includes('successfully') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}
      </div>
    </div>
  );
}
export default BookAppointment;