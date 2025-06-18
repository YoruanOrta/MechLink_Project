import React, { useState, useEffect } from "react";
import "./BookAppointment.css";

function BookAppointment() {
  const token = localStorage.getItem("token");
  const userId = localStorage.getItem("user_id");

  const [workshops, setWorkshops] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [formData, setFormData] = useState({
    workshop_id: "",
    vehicle_id: "",
    appointment_date: "",
    appointment_time: "",
    notes: "",
  });
  const [message, setMessage] = useState("");

  // Fetch user's vehicles
  useEffect(() => {
    fetch("http://localhost:8000/api/v1/vehicles/my-vehicles", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => setVehicles(data))
      .catch(() => setMessage("Failed to load vehicles."));
  }, [token]);

  // Fetch available workshops
  useEffect(() => {
    fetch("http://localhost:8000/api/v1/workshops", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => setWorkshops(data))
      .catch(() => setMessage("Failed to load workshops."));
  }, [token]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    try {
      const response = await fetch("http://localhost:8000/api/v1/appointments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setMessage("Appointment booked successfully 📅");
      } else {
        const errorData = await response.json();
        setMessage(errorData.detail || "Error booking appointment.");
      }
    } catch {
      setMessage("Network error.");
    }
  };

  return (
    <div className="appointment-form-container">
      <h2>Book Appointment</h2>
      <form className="appointment-form" onSubmit={handleSubmit}>
        <label>
          Select Workshop:
          <select name="workshop_id" required onChange={handleChange}>
            <option value="">-- Choose a workshop --</option>
            {workshops.map((w) => (
              <option key={w.id} value={w.id}>
                {w.name} - {w.city}
              </option>
            ))}
          </select>
        </label>

        <label>
          Select Vehicle:
          <select name="vehicle_id" required onChange={handleChange}>
            <option value="">-- Choose a vehicle --</option>
            {vehicles.map((v) => (
              <option key={v.id} value={v.id}>
                {v.make} {v.model} ({v.year})
              </option>
            ))}
          </select>
        </label>

        <input type="date" name="appointment_date" required onChange={handleChange} />
        <input type="time" name="appointment_time" required onChange={handleChange} />
        <textarea name="notes" placeholder="Additional notes" onChange={handleChange}></textarea>

        <button type="submit">Book Appointment</button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
}

export default BookAppointment;