import React, { useEffect, useState } from "react";
import "../styles/Dashboard.css";
import { useNavigate } from "react-router-dom";
import NotificationWidget from "../components/NotificationWidget";
import tokenManager from '../utils/tokenManager';
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
  const [activeSection, setActiveSection] = useState('search');
  const [appointments, setAppointments] = useState([]);
  const [appointmentsLoading, setAppointmentsLoading] = useState(true);
  const [favorites, setFavorites] = useState([]);
  const [favoritesLoading, setFavoritesLoading] = useState(false);

  const fetchWorkshops = async () => {
    setLoading(true);
    setError("");
  
    try {
      const response = await tokenManager.get("http://localhost:8000/api/v1/workshops/");
  
      if (!response.ok) {
        throw new Error("Failed to fetch mechanics.");
      }
  
      const data = await response.json();
      setAllWorkshops(data || []);
      setSearchResults(data || []);
    } catch (err) {
      setError("Failed to fetch workshops.");
    } finally {
      setLoading(false);
    }
  };

  const fetchVehicles = async () => {
    setVehiclesLoading(true);
    try {
      // ✅ USAR tokenManager en lugar de fetch
      const response = await tokenManager.get("http://localhost:8000/api/v1/vehicles/");
  
      if (!response.ok) throw new Error("Failed to fetch vehicles");
      const data = await response.json();
      setVehicles(data || []);
    } catch (err) {
      console.error("Error fetching vehicles:", err);
    } finally {
      setVehiclesLoading(false);
    }
  };
  const fetchAppointments = async () => {
    setAppointmentsLoading(true);
    try {
      const response = await tokenManager.get("http://localhost:8000/api/v1/appointments/");
      if (response.ok) {
        const data = await response.json();
        
        const activeAppointments = data?.filter(apt => apt.status !== "cancelled") || [];
        
        setAppointments(activeAppointments);
      }
    } catch (err) {
      console.error("Error fetching appointments:", err);
    } finally {
      setAppointmentsLoading(false);
    }
  };

  const fetchFavorites = async () => {
    try {
      const favoritesString = localStorage.getItem('favorites');
      console.log("🔍 localStorage raw:", favoritesString);
      
      const favorites = JSON.parse(favoritesString || '[]');
      console.log("🔍 Parsed favorites:", favorites);
      console.log("🔍 Favorites count:", favorites.length);
      
      setFavorites(favorites);
    } catch (error) {
      console.error('Error loading favorites:', error);
      setFavorites([]);
    }
  };
  
  const toggleFavorite = async (workshop) => {
    try {
      console.log("🔍 toggleFavorite llamado con:", workshop);
      setFavoritesLoading(true);
      
      const currentFavorites = JSON.parse(localStorage.getItem('favorites') || '[]');
      console.log("🔍 currentFavorites:", currentFavorites);
      
      const isAlreadyFavorite = currentFavorites.some(fav => fav.id === workshop.id);
      console.log("🔍 isAlreadyFavorite:", isAlreadyFavorite);
      
      let updatedFavorites;
      if (isAlreadyFavorite) {
        updatedFavorites = currentFavorites.filter(fav => fav.id !== workshop.id);
        console.log("🔍 Removiendo favorito, nuevo array:", updatedFavorites);
      } else {
        const favoriteWorkshop = {
          ...workshop,
          addedToFavorites: new Date().toISOString()
        };
        updatedFavorites = [...currentFavorites, favoriteWorkshop];
        console.log("🔍 Agregando favorito, nuevo array:", updatedFavorites);
      }
      
      console.log("🔍 Guardando en localStorage:", JSON.stringify(updatedFavorites));
      localStorage.setItem('favorites', JSON.stringify(updatedFavorites));
      
      // Verificar que se guardó
      const verified = localStorage.getItem('favorites');
      console.log("🔍 Verificación - guardado:", verified);
      
      setFavorites(updatedFavorites);
      
      if (isAlreadyFavorite) {
        alert(`❌ ${workshop.name} removed from favorites`);
      } else {
        alert(`⭐ ${workshop.name} added to favorites!`);
      }
      
    } catch (error) {
      console.error('🔍 Error en toggleFavorite:', error);
      alert('❌ Error updating favorites');
    } finally {
      setFavoritesLoading(false);
    }
  };
  
  const isFavorite = (workshopId) => {
    return favorites.some(fav => fav.id === workshopId);
  };
  

  const handleSearch = () => {
    console.log("🔍 DEBUG - Service Type selected:", serviceType);
    console.log("📍 DEBUG - Location:", location);
    
  const filtered = allWorkshops.filter((workshop) => {
    console.log("🏪 Workshop:", workshop.name);
    console.log("📋 Services:", workshop.services);
    console.log("🌍 City:", workshop.city);
    
  const matchesCity =
    location.trim() === "" ||
    workshop.city.toLowerCase().includes(location.trim().toLowerCase());
  
    let matchesService = false;
    if (serviceType === "all") {
      matchesService = true;
    } else if (workshop.services) {
      matchesService = workshop.services.some((service) => {
  const result = service.toLowerCase().includes(serviceType.toLowerCase());
    console.log(`🔎 "${service}" includes "${serviceType}"? ${result}`);
        return result;
      });
    }
  
      console.log("✅ Matches city:", matchesCity);
      console.log("✅ Matches service:", matchesService);
      console.log("📊 Final result:", matchesCity && matchesService);
      console.log("---");
  
      return matchesCity && matchesService;
    });
  
    console.log("🎯 Filtered results:", filtered);
    setSearchResults(filtered);
  };

  useEffect(() => {
    fetchWorkshops();
    fetchVehicles();
    fetchAppointments();
    fetchFavorites();

    const checkForUpdates = () => {
      if (localStorage.getItem('appointmentsUpdated') === 'true') {
        fetchAppointments();
        localStorage.removeItem('appointmentsUpdated');
      }
    };
    
    window.addEventListener('focus', checkForUpdates);
    return () => window.removeEventListener('focus', checkForUpdates);
  }, []);
  useEffect(() => {
    if (activeSection === 'services') {
      
      if (localStorage.getItem('appointmentsUpdated') === 'true') {
        fetchAppointments();
        localStorage.removeItem('appointmentsUpdated');
      }
    }
  }, [activeSection]);

  return (
    <div className="dashboard-container">
    <button 
      onClick={() => navigate("/")} 
      className="back-to-landing-button"
      title="Back to Landing Page"
    >
      ←
    </button>
      <aside className="sidebar">
        <h2 className="sidebar-logo">
          <img src="/images/gear.svg" alt="MechLink Logo" style={{width: '90px', height: '90px'}} />
        </h2>
        <ul>
          <li 
            className="sidebar-button btn-blue pulse"
            onClick={() => setActiveSection('search')}
          >
              🔍 Search Mechanics
          </li>
          <li 
              className="sidebar-button btn-green"
              onClick={() => setActiveSection('services')}
          >
            🛠️ My Services
          </li>
          <li onClick={() => navigate("/appointments/book")} className="sidebar-button btn-red">⚡ Easy Appointments</li>
          <li onClick={() => navigate("/maintenance/logs")} className="sidebar-button btn-blue">📘 Maintenance Logs</li>
          <li 
            className="sidebar-button btn-yellow"
            onClick={() => navigate("/favorites")}
          >
          ⭐ Favorites
        </li>
        </ul>
      </aside>

      <main className="main-content">
        <div className="dashboard-header">
          <NotificationWidget />
        </div>

        {activeSection === 'search' ? (
          <>
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
                    <option value="Oil Change">Oil Change</option>
                    <option value="Brake Service">Brake Service</option>
                    <option value="AC Repair">AC Repair</option>
                    <option value="Tire Service">Tire Service</option>
                    <option value="Engine Repair">Engine Repair</option>
                    <option value="Transmission">Transmission</option>
                    <option value="General Maintenance">General Maintenance</option>
                    <option value="Inspection">Inspection</option>
                    <option value="Wheel Alignment">Wheel Alignment</option>
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
                ) : searchResults.length === 0 ? (
                  <div style={{
                    textAlign: 'center',
                    padding: '40px',
                    backgroundColor: '#1e293b',
                    borderRadius: '12px',
                    color: '#94a3b8'
                  }}>
                    <p>No workshops found matching your criteria.</p>
                    <p>Try adjusting your search filters.</p>
                  </div>
                ) : (
                  searchResults.map((workshop) => (
                    <div key={workshop.id} style={{
                      backgroundColor: '#1e293b',
                      padding: '20px',
                      borderRadius: '12px',
                      border: '2px solid #10b981',
                      marginBottom: '15px',
                      position: 'relative'
                    }}>
                      {/* Header with name and favorite button */}
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                        marginBottom: '15px'
                      }}>
                        <h3 style={{
                          color: '#10b981',
                          marginBottom: '0',
                          flex: 1
                        }}>
                          {workshop.name}
                        </h3>
                        
                        {/* Favorite Button */}
                        <button
                          onClick={() => toggleFavorite(workshop)}
                          disabled={favoritesLoading}
                          style={{
                            background: isFavorite(workshop.id) 
                              ? 'linear-gradient(45deg, #f59e0b, #f97316)' 
                              : 'linear-gradient(45deg, #6b7280, #9ca3af)',
                            color: 'white',
                            border: 'none',
                            padding: '8px 16px',
                            borderRadius: '8px',
                            fontSize: '14px',
                            fontWeight: 'bold',
                            cursor: favoritesLoading ? 'not-allowed' : 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            transition: 'all 0.3s ease',
                            opacity: favoritesLoading ? 0.7 : 1,
                            transform: 'scale(0.95)',
                            marginLeft: '15px'
                          }}
                          onMouseEnter={(e) => {
                            if (!favoritesLoading) {
                              e.target.style.transform = 'scale(1)';
                              e.target.style.boxShadow = '0 4px 15px rgba(245, 158, 11, 0.4)';
                            }
                          }}
                          onMouseLeave={(e) => {
                            if (!favoritesLoading) {
                              e.target.style.transform = 'scale(0.95)';
                              e.target.style.boxShadow = 'none';
                            }
                          }}
                        >
                          {isFavorite(workshop.id) ? '⭐' : '☆'}
                          {isFavorite(workshop.id) ? 'Favorited' : 'Add to Favorites'}
                        </button>
                      </div>

                      {/* Workshop info */}
                      <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                        gap: '15px',
                        marginBottom: '15px'
                      }}>
                        <div>
                          <p style={{color: '#e5e7eb', margin: '5px 0'}}>
                            📍 {workshop.address || workshop.city}
                          </p>
                          <p style={{color: '#e5e7eb', margin: '5px 0'}}>
                            📞 {workshop.phone}
                          </p>
                          <p style={{color: '#e5e7eb', margin: '5px 0'}}>
                            ⏰ {workshop.business_hours || 'Mon-Fri 8:00 AM - 6:00 PM'}
                          </p>
                        </div>
                        
                        <div>
                          <p style={{color: '#e5e7eb', margin: '5px 0'}}>
                            🔧 {workshop.services?.join(', ') || 'General Repair'}
                          </p>
                          <p style={{color: '#e5e7eb', margin: '5px 0'}}>
                            ⭐ {workshop.rating_average || '4.5'}/5 ({workshop.total_reviews || '12'} reviews)
                          </p>
                          {workshop.description && (
                            <p style={{color: '#94a3b8', margin: '5px 0', fontSize: '14px'}}>
                              📝 {workshop.description}
                            </p>
                          )}
                        </div>
                      </div>
                      {/* Action buttons */}
                      <div style={{
                        display: 'flex',
                        gap: '10px',
                        flexWrap: 'wrap'
                      }}>
                        <button 
                          style={{
                            backgroundColor: '#3b82f6',
                            color: 'white',
                            padding: '10px 20px',
                            border: 'none',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            fontWeight: 'bold',
                            flex: '1',
                            minWidth: '140px'
                          }}
                          onClick={() => navigate("/appointments/book")}
                        >
                          📅 Book Appointment
                        </button>
                        
                        <button 
                          style={{
                            backgroundColor: '#10b981',
                            color: 'white',
                            padding: '10px 20px',
                            border: 'none',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            fontWeight: 'bold',
                            flex: '1',
                            minWidth: '100px'
                          }}
                          onClick={() => window.open(`tel:${workshop.phone}`, '_self')}
                        >
                          📞 Call
                        </button>
                        
                        <button 
                          style={{
                            backgroundColor: '#6366f1',
                            color: 'white',
                            padding: '10px 20px',
                            border: 'none',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            fontWeight: 'bold',
                            flex: '1',
                            minWidth: '120px'
                          }}
                          onClick={() => window.open(`https://maps.google.com/?q=${encodeURIComponent((workshop.address || '') + ', ' + workshop.city)}`, '_blank')}
                        >
                          🗺️ Directions
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </section>
            </div>
          </>
        ) : (
          <>
          {/* My Services Section */}
          <div className="my-services-section">
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
              <h2>🛠️ My Services</h2>
              <button 
                style={{
                  backgroundColor: '#10b981',
                  color: 'white',
                  padding: '10px 20px',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
                onClick={() => navigate("/vehicles/register")}
              >
                ➕ Add Vehicle
              </button>
            </div>
            
            {vehiclesLoading ? (
              <p>Loading vehicles...</p>
            ) : vehicles.length === 0 ? (
              <div className="no-vehicles-container" style={{
                border: '2px dashed #10b981',
                borderRadius: '12px',
                padding: '40px',
                textAlign: 'center',
                backgroundColor: '#1e293b'
              }}>
                <p style={{fontSize: '18px', marginBottom: '20px'}}>No vehicles registered yet.</p>
                <button 
                  style={{
                    backgroundColor: '#10b981',
                    color: 'white',
                    padding: '12px 24px',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    cursor: 'pointer'
                  }}
                  onClick={() => navigate("/vehicles/register")}
                >
                  Register Vehicle
                </button>
              </div>
            ) : (
              <div>
                {vehicles.map((vehicle) => (
                  <div key={vehicle.id} style={{
                    backgroundColor: '#1e293b',
                    padding: '20px',
                    borderRadius: '12px',
                    marginBottom: '15px',
                    border: '2px solid #10b981'
                  }}>
                    <h3 style={{color: '#10b981', marginBottom: '10px'}}>
                      {vehicle.make} {vehicle.model} ({vehicle.year})
                    </h3>
                    <p style={{color: '#e5e7eb'}}>🚗 Plate: {vehicle.license_plate}</p>
                    <p style={{color: '#e5e7eb'}}>🎨 Color: {vehicle.color}</p>
                    <p style={{color: '#e5e7eb'}}>🏃 Mileage: {vehicle.current_mileage || vehicle.mileage || 0} km</p>
                    {vehicle.notes && <p style={{color: '#94a3b8'}}>📝 {vehicle.notes}</p>}
                  </div>
                ))}
                
                <div style={{
                  textAlign: 'center',
                  marginTop: '20px',
                  padding: '20px',
                  border: '2px dashed #10b981',
                  borderRadius: '12px',
                  backgroundColor: '#1e293b'
                }}>
                  <p style={{color: '#94a3b8', marginBottom: '15px'}}>
                    Want to add another vehicle?
                  </p>
                  <button 
                    style={{
                      backgroundColor: '#10b981',
                      color: 'white',
                      padding: '12px 24px',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '16px',
                      fontWeight: 'bold',
                      cursor: 'pointer'
                    }}
                    onClick={() => navigate("/vehicles/register")}
                  >
                    ➕ Add Another Vehicle
                  </button>
                </div>
              </div>
            )}
          </div>
        {/* Active Services */}
        {vehicles.length > 0 && (
          <section className="active-services">
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
              <h2>🚗 Active Services</h2>
              <button 
                style={{
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  padding: '10px 20px',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
                onClick={() => navigate("/appointments/book")}
              >
                📅 Book New Appointment
              </button>
            </div>

            {appointmentsLoading ? (
              <p style={{color: '#94a3b8'}}>Loading appointments...</p>
            ) : appointments.length === 0 ? (
              <div style={{
                textAlign: 'center',
                padding: '40px',
                backgroundColor: '#1e293b',
                borderRadius: '12px',
                border: '2px dashed #64748b'
              }}>
                <p style={{color: '#94a3b8', fontSize: '16px', marginBottom: '10px'}}>
                  📅 No active appointments
                </p>
                <p style={{color: '#64748b', fontSize: '14px'}}>
                  Book an appointment with a mechanic to see your active services here.
                </p>
                <button 
                  style={{
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    padding: '10px 20px',
                    border: 'none',
                    borderRadius: '8px',
                    marginTop: '15px',
                    cursor: 'pointer'
                  }}
                  onClick={() => navigate("/appointments/book")}
                >
                  📅 Book Appointment
                </button>
              </div>
            ) : (
              <div>
                {appointments.map((appointment) => {
                  const workshop = allWorkshops.find(w => w.id === appointment.workshop_id);
                  const vehicle = vehicles.find(v => v.id === appointment.vehicle_id);
                  
                  const appointmentDate = new Date(appointment.appointment_datetime);
                  const isUpcoming = appointmentDate > new Date();
                  const dateStr = appointmentDate.toLocaleDateString('en-US', {
                    weekday: 'short',
                    year: 'numeric', 
                    month: 'short', 
                    day: 'numeric'
                  });
                  const timeStr = appointmentDate.toLocaleTimeString('en-US', {
                    hour: '2-digit',
                    minute: '2-digit'
                  });

                  return (
                    <div 
                      key={appointment.id} 
                      style={{
                        backgroundColor: '#1e293b',
                        padding: '20px',
                        borderRadius: '12px',
                        marginBottom: '15px',
                        border: `2px solid ${isUpcoming ? '#3b82f6' : '#10b981'}`,
                        position: 'relative'
                      }}
                    >
                      {/* Status badge */}
                      <span 
                        style={{
                          position: 'absolute',
                          top: '15px',
                          right: '15px',
                          backgroundColor: isUpcoming ? '#3b82f6' : '#10b981',
                          color: 'white',
                          padding: '4px 12px',
                          borderRadius: '20px',
                          fontSize: '12px',
                          fontWeight: 'bold'
                        }}
                      >
                        {isUpcoming ? 'UPCOMING' : 'COMPLETED'}
                      </span>

                      {/* Service title */}
                      <h3 style={{color: '#3b82f6', marginBottom: '15px', marginRight: '100px'}}>
                        {appointment.service_type || 'General Service'}
                      </h3>

                      {/* Details grid */}
                      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '10px'}}>
                        <div>
                          <p style={{color: '#e5e7eb', margin: '5px 0'}}>
                            🏪 <strong>Workshop:</strong> {workshop ? workshop.name : 'Loading...'}
                          </p>
                          <p style={{color: '#e5e7eb', margin: '5px 0'}}>
                            📍 <strong>Location:</strong> {workshop ? workshop.city : 'Loading...'}
                          </p>
                        </div>
                        <div>
                          <p style={{color: '#e5e7eb', margin: '5px 0'}}>
                            🚗 <strong>Vehicle:</strong> {vehicle ? `${vehicle.make} ${vehicle.model}` : 'Loading...'}
                          </p>
                          <p style={{color: '#e5e7eb', margin: '5px 0'}}>
                            🏃 <strong>Plate:</strong> {vehicle ? vehicle.license_plate : 'Loading...'}
                          </p>
                        </div>
                      </div>

                      {/* Date and time */}
                      <div style={{
                        backgroundColor: '#374151',
                        padding: '10px',
                        borderRadius: '8px',
                        marginTop: '10px'
                      }}>
                        <p style={{color: '#10b981', margin: '0', fontWeight: 'bold'}}>
                          📅 {dateStr} at {timeStr}
                        </p>
                        {appointment.notes && (
                          <p style={{color: '#94a3b8', margin: '5px 0 0 0', fontSize: '14px'}}>
                            📝 {appointment.notes}
                          </p>
                        )}
                      </div>

                      {/* Action buttons */}
                      <div style={{display: 'flex', gap: '10px', marginTop: '15px'}}>
                        {isUpcoming && (
                          <>
                            <button style={{
                              backgroundColor: '#ef4444',
                              color: 'white',
                              padding: '6px 12px',
                              border: 'none',
                              borderRadius: '6px',
                              fontSize: '12px',
                              cursor: 'pointer'
                            }}>
                              Cancel
                            </button>
                            <button style={{
                              backgroundColor: '#f59e0b',
                              color: 'white',
                              padding: '6px 12px',
                              border: 'none',
                              borderRadius: '6px',
                              fontSize: '12px',
                              cursor: 'pointer'
                            }}>
                              Reschedule
                            </button>
                          </>
                        )}
                        {workshop && (
                          <button style={{
                            backgroundColor: '#10b981',
                            color: 'white',
                            padding: '6px 12px',
                            border: 'none',
                            borderRadius: '6px',
                            fontSize: '12px',
                            cursor: 'pointer'
                          }}>
                            📞 Call {workshop.phone}
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
            {/* Dashboard actions */}
            <div className="dashboard-actions" style={{marginTop: '20px'}}>
              <button className="emergency-button">🚨 EMERGENCY</button>
              <button 
                className="schedule-button"
                onClick={() => navigate("/appointments/book")}
              >
                📅 SCHEDULE
              </button>
              <button 
                className="history-button"
                onClick={() => navigate("/maintenance/logs")}
              >
                📊 HISTORY
              </button>
            </div>
          </section>
          )}
        </>
        )}
      </main>
    </div>
  );
}

export default Dashboard;