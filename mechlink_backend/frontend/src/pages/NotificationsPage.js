import React, { useEffect, useState } from "react";

function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [error, setError] = useState("");

  const token = localStorage.getItem("token");

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/notifications", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setNotifications(data);
        } else {
          setError("Unexpected response format.");
        }
      })
      .catch(() => setError("Failed to fetch notifications."));
  }, [token]);

  return (
    <div style={{ padding: "2rem" }}>
      <h2>My Notifications</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {notifications.length === 0 && !error ? (
        <p>No notifications found.</p>
      ) : (
        <ul>
          {notifications.map((n) => (
            <li key={n.id}>
              <strong>{n.title}</strong> — {n.message}
              <br />
              <small>Status: {n.status}</small>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default NotificationsPage;
