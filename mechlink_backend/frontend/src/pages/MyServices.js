// src/pages/MyServices.js

import React, { useEffect, useState } from "react";
import "../styles/MyServices.css";
import { useNavigate } from "react-router-dom";

function MyServices() {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchVehicles = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/v1/vehicles/my-vehicles", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });

        if (!response.ok) throw new Error("Failed to fetch vehicles");

        const data = await response.json();
        setVehicles(data);
      } catch (err) {
        setError("Could not load vehicles. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchVehicles();
  }, []);

  return (
    <div className="my-services-container">
      <h2>🛠️ My Services</h2>

      {loading && <p>Loading...</p>}
      {error && <p className="error-text">{error}</p>}

      {vehicles.length === 0 && !loading ? (
        <div className="no-vehicles">
          <p>No vehicles registered yet.</p>
          <button onClick={() => navigate("/vehicles/register")}>Register Vehicle</button>
        </div>
      ) : (
        <div className="vehicle-list">
          {vehicles.map((vehicle) => (
            <div key={vehicle.id} className="vehicle-card">
              <h3>{vehicle.make} {vehicle.model} ({vehicle.year})</h3>
              <p>📄 Plate: {vehicle.license_plate}</p>
              {/* <p>🔢 VIN: {vehicle.vin}</p> */}
              {/* Optional edit/delete buttons here */}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MyServices;
