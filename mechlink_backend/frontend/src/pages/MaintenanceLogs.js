import React, { useEffect, useState } from "react";
import "../styles/MaintenanceLogs.css";

function MaintenanceLogs() {
  const [records, setRecords] = useState([]);
  const [error, setError] = useState("");
  const token = localStorage.getItem("token");

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/maintenance/records", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch");
        return res.json();
      })
      .then((data) => setRecords(data))
      .catch(() => setError("Failed to load maintenance records."));
  }, [token]);

  return (
    <div className="maintenance-container">
      <h2>Maintenance Logs</h2>
      {error && <p className="error">{error}</p>}
      {records.length === 0 ? (
        <p>No maintenance records found.</p>
      ) : (
        <ul className="maintenance-list">
          {records.map((record) => (
            <li key={record.id} className="maintenance-card">
              <strong>{record.service_type}</strong> on {record.service_date}
              <br />
              Mileage: {record.mileage_at_service} km
              <br />
              Cost: ${record.cost || "N/A"}
              <br />
              Notes: {record.notes || "None"}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default MaintenanceLogs;
