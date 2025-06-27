import React, { useEffect, useState } from "react";
import "../styles/ViewVehicles.css";

function ViewVehicles() {
  const [vehicles, setVehicles] = useState([]);
  const [error, setError] = useState("");
  const token = localStorage.getItem("token");

  useEffect(() => {
    const fetchVehicles = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/v1/vehicles/my-vehicles", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (res.ok) {
          const data = await res.json();
          setVehicles(data);
        } else {
          const errData = await res.json();
          setError(errData.detail || "Error loading vehicles.");
        }
      } catch {
        setError("Connection error.");
      }
    };

    fetchVehicles();
  }, [token]);

  return (
    <div className="vehicles-container">
      <h2>My Vehicles</h2>
      {error && <p className="error">{error}</p>}
      {vehicles.length === 0 ? (
        <p>You have no registered vehicles.</p>
      ) : (
        <ul className="vehicle-list">
          {vehicles.map((v) => (
            <li key={v.id} className="vehicle-card">
              <strong>{v.make} {v.model}</strong> ({v.year})<br />
              License Plate: {v.license_plate}<br />
              Color: {v.color || "N/A"}<br />
              Mileage: {v.current_mileage} km
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default ViewVehicles;