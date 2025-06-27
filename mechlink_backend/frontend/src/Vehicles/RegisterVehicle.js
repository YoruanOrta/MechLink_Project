import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/RegisterVehicle.css";

function RegisterVehicle() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const user_id = localStorage.getItem("user_id");

  const [formData, setFormData] = useState({
    make: "",
    model: "",
    year: "",
    license_plate: "",
    color: "",
    current_mileage: "",
    fuel_type: "",
    transmission: "",
    engine_size: "",
    vin: "",
    image: "",
    notes: "",
    user_id: user_id,
  });

  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    try {
      const response = await fetch("http://localhost:8000/api/v1/vehicles/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setMessage("Vehicle registered successfully 🚗");
        navigate("/vehicles");
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
        <input type="number" name="current_mileage" placeholder="Mileage" onChange={handleChange} />
        <input type="text" name="fuel_type" placeholder="Fuel Type" onChange={handleChange} />
        <input type="text" name="transmission" placeholder="Transmission" onChange={handleChange} />
        <input type="text" name="engine_size" placeholder="Engine Size" onChange={handleChange} />
        <input type="text" name="vin" placeholder="VIN (17 characters)" onChange={handleChange} />
        <input type="text" name="image" placeholder="Image URL" onChange={handleChange} />
        <textarea name="notes" placeholder="Additional Notes" onChange={handleChange}></textarea>

        <button type="submit">Register</button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
}

export default RegisterVehicle;