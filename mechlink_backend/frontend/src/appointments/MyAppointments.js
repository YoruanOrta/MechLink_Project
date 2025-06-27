import React, { useEffect, useState } from "react";
import "./MyAppointments.css";

function MyAppointments() {
  const token = localStorage.getItem("token");
  const [appointments, setAppointments] = useState([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [filter, setFilter] = useState("all");

  const fetchAppointments = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/appointments", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setAppointments(data);
      } else {
        const err = await response.json();
        setError(err.detail || "Error loading appointments.");
      }
    } catch {
      setError("Network error.");
    }
  };

  useEffect(() => {
    fetchAppointments();
  }, []);

  const handleCancel = async (id) => {
    const confirmCancel = window.confirm("Are you sure you want to cancel this appointment?");
    if (!confirmCancel) return;

    try {
      const res = await fetch(`http://localhost:8000/api/v1/appointments/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (res.ok) {
        setMessage("Appointment cancelled successfully.");
        fetchAppointments();
      } else {
        const err = await res.json();
        setError(err.detail || "Could not cancel appointment.");
      }
    } catch {
      setError("Network error while cancelling.");
    }
  };

  // Apply filter
  const filteredAppointments = appointments.filter((a) => {
    if (filter === "active") return a.status !== "cancelled";
    if (filter === "cancelled") return a.status === "cancelled";
    return true; // all
  });

  return (
    <div className="appointments-container">
      <h2>My Appointments</h2>

      <div className="filter-section">
        <label>Filter:</label>
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="all">All</option>
          <option value="active">Active</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      {error && <p className="error">{error}</p>}
      {message && <p className="success">{message}</p>}

      {filteredAppointments.length === 0 ? (
        <p>No appointments found for selected filter.</p>
      ) : (
        <ul className="appointment-list">
          {filteredAppointments.map((a) => (
            <li key={a.id} className="appointment-card">
              <strong>Date:</strong>{" "}
              {new Date(a.appointment_datetime).toLocaleDateString()}<br />
              <strong>Time:</strong>{" "}
              {new Date(a.appointment_datetime).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}<br />
              <strong>Service:</strong> {a.service_type}<br />
              <strong>Status:</strong> {a.status}
              {a.notes && <><br /><em>Note: {a.notes}</em></>}
              {a.status !== "cancelled" && (
                <button onClick={() => handleCancel(a.id)} className="cancel-btn">
                  Cancel Appointment
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default MyAppointments;