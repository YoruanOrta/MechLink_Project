import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/RegisterVehicle.css";
import tokenManager from '../utils/tokenManager';


function RegisterVehicle() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const user_id = "ede51667-a6a0-48ac-be6d-869b1fbc9513";

  const [formData, setFormData] = useState({
    make: "",
    model: "",
    year: "",
    user_id: localStorage.getItem("user_id"),
    license_plate: "",
    color: "",
    mileage: "",
    transmission: "",
    engine_size: "",
    notes: "",
  });

  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
  
    try {
      // ✅ USAR tokenManager en lugar de fetch
      const response = await tokenManager.post("http://localhost:8000/api/v1/vehicles/", formData);
  
      if (response.ok) {
        setMessage("Vehicle registered successfully 🚗");
        navigate("/dashboard");
      } else {
        const data = await response.json();
        setMessage(data.detail || "Error registering vehicle");
      }
    } catch (err) {
      setMessage("Network error.");
    }
  };

  return (
    <div className="vehicle-form-container">
      <h2>Register Vehicle</h2>
      <form className="vehicle-form" onSubmit={handleSubmit}>
        <input type="text" name="make" placeholder="Make*" required onChange={handleChange} />
        <input type="text" name="model" placeholder="Model*" required onChange={handleChange} />
        <input type="number" name="year" placeholder="Year*" required onChange={handleChange} />
        <input type="text" name="license_plate" placeholder="License Plate*" required onChange={handleChange} />
        <input type="text" name="color" placeholder="Color" onChange={handleChange} />
        <input type="number" name="mileage" placeholder="Mileage" onChange={handleChange} />
        <input type="text" name="transmission" placeholder="Transmission" onChange={handleChange} />
        <input type="text" name="engine_size" placeholder="Engine Size" onChange={handleChange} />
        <textarea name="notes" placeholder="Additional Notes" onChange={handleChange}></textarea>

        <button type="submit">Register</button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
}

export default RegisterVehicle;