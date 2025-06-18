import React, { useEffect, useState } from "react";
import "./Dashboard.css";

function Dashboard() {
  const token = localStorage.getItem("token");
  const [vehicles, setVehicles] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchVehicles = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/v1/vehicles", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setVehicles(data);
        }
      } catch {
        setError("Failed to load vehicles");
      }
    };

    const fetchAppointments = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/v1/appointments", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setAppointments(data);
        }
      } catch {
        setError("Failed to load appointments");
      }
    };

    fetchVehicles();
    fetchAppointments();
  }, [token]);

  const totalAppointments = appointments.length;
  const cancelled = appointments.filter((a) => a.status === "cancelled").length;
  const active = totalAppointments - cancelled;

  const nextAppointment = appointments
    .filter((a) => a.status !== "cancelled")
    .sort((a, b) => new Date(a.appointment_datetime) - new Date(b.appointment_datetime))[0];

  return (
    <div className="dashboard-container">
      <h2>Welcome to your Dashboard</h2>
      {error && <p className="error">{error}</p>}

      <div className="cards">
        <div className="card">
          <h3>{vehicles.length}</h3>
          <p>Registered Vehicles</p>
        </div>
        <div className="card">
          <h3>{totalAppointments}</h3>
          <p>Total Appointments</p>
        </div>
        <div className="card">
          <h3>{active}</h3>
          <p>Active Appointments</p>
        </div>
        <div className="card">
          <h3>{cancelled}</h3>
          <p>Cancelled Appointments</p>
        </div>
        {nextAppointment && (
          <div className="card highlight">
            <h3>Next Appointment</h3>
            <p>
              {new Date(nextAppointment.appointment_datetime).toLocaleDateString()}{" "}
              at {new Date(nextAppointment.appointment_datetime).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              <br />
              <strong>{nextAppointment.service_type}</strong>
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;