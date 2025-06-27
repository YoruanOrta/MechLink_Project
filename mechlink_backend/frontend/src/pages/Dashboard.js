import React, { useEffect, useState } from "react";
import "../styles/Dashboard.css";
import { useNavigate } from "react-router-dom";
import NotificationWidget from "../components/NotificationWidget";
import { Link } from "react-router-dom";

function Dashboard() {
  const navigate = useNavigate();
  const [allWorkshops, setAllWorkshops] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [location, setLocation] = useState("");
  const [serviceType, setServiceType] = useState("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [vehicles, setVehicles] = useState([]);
  const [vehiclesLoading, setVehiclesLoading] = useState(true);

  const fetchWorkshops = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/v1/workshops/for-map", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch mechanics.");
      }

      const data = await response.json();
      setAllWorkshops(data.workshops || []);
      setSearchResults(data.workshops || []);
    } catch (err) {
      setError("Failed to fetch workshops.");
    } finally {
      setLoading(false);
    }
  };

  const fetchVehicles = async () => {
    setVehiclesLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/vehicles/my-vehicles", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (!response.ok) throw new Error("Failed to fetch vehicles");
      const data = await response.json();
      setVehicles(data || []);
    } catch (err) {
      console.error("Error fetching vehicles:", err);
    } finally {
      setVehiclesLoading(false);
    }
  };

  const handleSearch = () => {
    const filtered = allWorkshops.filter((workshop) => {
      const matchesCity =
        location.trim() === "" ||
        workshop.city.toLowerCase().includes(location.trim().toLowerCase());

      const matchesService =
        serviceType === "all" ||
        (workshop.services &&
          workshop.services.some((service) =>
            service.toLowerCase().includes(serviceType.toLowerCase())
          ));

      return matchesCity && matchesService;
    });

    setSearchResults(filtered);
  };

  useEffect(() => {
    fetchWorkshops();
    fetchVehicles();
  }, []);

  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <h2 className="sidebar-logo">🔧 MechLink</h2>
        <ul>
          <li className="sidebar-button btn-blue">
            <Link to="/search" className="sidebar-link">
              🔍 Search Mechanics
            </Link>
          </li>
          <li className="sidebar-button btn-yellow"><Link to="/my-services" className="sidebar-link">
      🛠️ My Services
    </Link></li>
          <li onClick={() => navigate("/appointments/book")} className="sidebar-button btn-red">⚡ Easy Appointments</li>
          <li onClick={() => navigate("/maintenance/logs")} className="sidebar-button btn-blue">📘 Maintenance Logs</li>
          <li className="sidebar-button btn-yellow">⭐ Favorites</li>
        </ul>
      </aside>

      <main className="main-content">
        <div className="dashboard-header">
          <NotificationWidget />
        </div>

        <div className="search-bar-box">
          <h2 className="search-bar-title">Find & Connect with Mechanics</h2>
          <div className="search-bar-ui">
            <div className="input-group">
              <label>Location</label>
              <input
                type="text"
                placeholder="Enter location"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
            </div>
            <div className="input-group">
              <label>Service Type</label>
              <select
                value={serviceType}
                onChange={(e) => setServiceType(e.target.value)}
              >
                <option value="all">All Services</option>
                <option value="oil change">Oil Change</option>
                <option value="brake inspection">Brake Inspection</option>
              </select>
            </div>
            <button className="search-button" onClick={handleSearch}>
              SEARCH
            </button>
          </div>
        </div>

        <div className="dashboard-body">
          <section className="available-mechanics">
            <h2>🔧 Available Mechanics</h2>
            {loading ? (
              <p>Loading...</p>
            ) : error ? (
              <p className="error-text">{error}</p>
            ) : searchResults.length > 0 ? (
              searchResults.map((workshop) => (
                <div className="mechanic-card" key={workshop.id}>
                  <h3>{workshop.name}</h3>
                  <p>
                    ⭐ {workshop.rating} ({workshop.total_reviews} reviews)
                  </p>
                  <p>📍 {workshop.city}</p>
                  <p>📞 {workshop.phone}</p>
                  <button className="connect-button">Connect Now</button>
                </div>
              ))
            ) : (
              <p>No results found</p>
            )}
          </section>

          {/* <section className="my-services">
            <h2>🛠️ My Services</h2>
            {vehiclesLoading ? (
              <p>Loading vehicles...</p>
            ) : vehicles.length === 0 ? (
              <div className="no-vehicles-box">
                <p>You have no registered vehicles.</p>
                <button
                  className="register-vehicle-button"
                  onClick={() => navigate("/vehicles/register")}
                >
                  Register a Vehicle
                </button>
              </div>
            ) : (
              vehicles.map((vehicle) => (
                <div className="vehicle-card" key={vehicle.id}>
                  <h3>
                    {vehicle.make} {vehicle.model} ({vehicle.year})
                  </h3>
                  <p>🚗 Plate: {vehicle.license_plate}</p>
                  <p>🔑 VIN: {vehicle.vin}</p>
                </div>
              ))
            )}
          </section> */}

          <section className="active-services">
            <h2>🚗 Active Services</h2>
            <div className="service-card in-progress">
              <h3>
                Oil Change & Filter{" "}
                <span className="status-label in-progress">In Progress</span>
              </h3>
              <p>AutoPro Services</p>
              <p>ETA: 15 minutes remaining</p>
            </div>

            <div className="service-card scheduled">
              <h3>
                Brake Inspection{" "}
                <span className="status-label scheduled">Scheduled</span>
              </h3>
              <p>SpeedyFix Garage</p>
              <p>Scheduled for tomorrow 2:00 PM</p>
            </div>

            <div className="dashboard-actions">
              <button className="emergency-button">🚨 EMERGENCY</button>
              <button className="schedule-button">📅 SCHEDULE</button>
              <button className="history-button">📊 HISTORY</button>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

export default Dashboard;