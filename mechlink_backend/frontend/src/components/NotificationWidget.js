import React, { useEffect, useState } from "react";
import { Bell } from "lucide-react";
import "./NotificationWidget.css";

function NotificationWidget() {
  const [notifications, setNotifications] = useState([]);
  const [open, setOpen] = useState(false);
  const token = localStorage.getItem("access_token");

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/notifications?unread_only=true", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) setNotifications(data);
      })
      .catch((err) => console.error(err));
  }, [token]);

  return (
    <div className="notification-widget">
      <button className="bell-btn" onClick={() => setOpen(!open)}>
        <Bell className="bell-icon" />
        {notifications.length > 0 && (
          <span className="badge">{notifications.length}</span>
        )}
      </button>

      {open && (
        <div className="dropdown">
          <h4>Smart Notifications</h4>
          {notifications.length === 0 ? (
            <p className="no-notifications">You're all caught up!</p>
          ) : (
            <ul>
              {notifications.slice(0, 5).map((n) => (
                <li key={n.id}>
                  <strong>{n.title}</strong>
                  <p>{n.message}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

export default NotificationWidget;
