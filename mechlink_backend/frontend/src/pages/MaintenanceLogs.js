import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import tokenManager from "../utils/tokenManager";
import "../styles/MaintenanceLogs.css";

function MaintenanceLogs() {
  const navigate = useNavigate();
  const [appointments, setAppointments] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [workshops, setWorkshops] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedVehicle, setSelectedVehicle] = useState("all");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [selectedAppointmentForReview, setSelectedAppointmentForReview] = useState(null);
  const [reviewData, setReviewData] = useState({
    rating: 0,
    comment: '',
    recommend: true
  });
  const [submitingReview, setSubmitingReview] = useState(false);
  
  // Modal states
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState(""); // "cancel", "reschedule"
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [rescheduleData, setRescheduleData] = useState({
    date: "",
    time: ""
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [appointmentsRes, vehiclesRes, workshopsRes] = await Promise.all([
        tokenManager.get("http://localhost:8000/api/v1/appointments/"),
        tokenManager.get("http://localhost:8000/api/v1/vehicles/"),
        tokenManager.get("http://localhost:8000/api/v1/workshops/")
      ]);
  
      if (appointmentsRes.ok && vehiclesRes.ok && workshopsRes.ok) {
        const [appointmentsData, vehiclesData, workshopsData] = await Promise.all([
          appointmentsRes.json(),
          vehiclesRes.json(),
          workshopsRes.json()
        ]);
  
        const activeAppointments = appointmentsData?.filter(apt => apt.status !== "cancelled") || [];
        
        setAppointments(activeAppointments);
        setVehicles(vehiclesData || []);
        setWorkshops(workshopsData || []);
      } else {
        throw new Error("Failed to fetch data");
      }
    } catch (err) {
      setError("Failed to load service history.");
      console.error("Error fetching data:", err);
    } finally {
      setLoading(false);
    }
  };

  // Filter appointments based on selected criteria
  const filteredAppointments = appointments.filter(appointment => {
    const vehicleMatch = selectedVehicle === "all" || appointment.vehicle_id === selectedVehicle;
    
    let statusMatch = true;
    if (selectedStatus !== "all") {
      const appointmentDate = new Date(appointment.appointment_datetime);
      const isCompleted = appointmentDate < new Date();
      
      if (selectedStatus === "completed" && !isCompleted) statusMatch = false;
      if (selectedStatus === "upcoming" && isCompleted) statusMatch = false;
    }
    
    return vehicleMatch && statusMatch;
  });

  // Sort appointments by date (newest first)
  const sortedAppointments = filteredAppointments.sort((a, b) => 
    new Date(b.appointment_datetime) - new Date(a.appointment_datetime)
  );

  const getVehicleInfo = (vehicleId) => {
    const vehicle = vehicles.find(v => v.id === vehicleId);
    return vehicle ? `${vehicle.make} ${vehicle.model} (${vehicle.license_plate})` : "Vehicle Deleted";
  };

  const getWorkshopInfo = (workshopId) => {
    const workshop = workshops.find(w => w.id === workshopId);
    return workshop ? { name: workshop.name, city: workshop.city, phone: workshop.phone } : null;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const isCompleted = (dateString) => {
    return new Date(dateString) < new Date();
  };

  // Modal handlers
  const openModal = (type, appointment) => {
    setModalType(type);
    setSelectedAppointment(appointment);
    setShowModal(true);
    
    if (type === "reschedule") {
      // Set current date/time as default
      const currentDate = new Date(appointment.appointment_datetime);
      setRescheduleData({
        date: currentDate.toISOString().split('T')[0],
        time: currentDate.toTimeString().slice(0, 5)
      });
    }
  };

  const closeModal = () => {
    setShowModal(false);
    setModalType("");
    setSelectedAppointment(null);
    setRescheduleData({ date: "", time: "" });
  };

  // Button action handlers
  const handleCallWorkshop = (phone) => {
    if (phone) {
      window.open(`tel:${phone}`, '_self');
    }
  };

  const handleCancelAppointment = async () => {
    if (!selectedAppointment) return;
  
    try {      
      const response = await tokenManager.delete(`http://localhost:8000/api/v1/appointments/${selectedAppointment.id}`);
      
      if (response.ok) {
        
        closeModal();
        
        setTimeout(async () => {
          await fetchData();
        }, 500);
        
        localStorage.setItem('appointmentsUpdated', 'true');
        alert("✅ Appointment cancelled successfully!");
      } else {
        throw new Error("Failed to cancel appointment");
      }
    } catch (error) {
      console.error("❌ Error cancelling appointment:", error);
      alert("❌ Failed to cancel appointment. Please try again.");
    }
  };

  const handleRescheduleAppointment = async () => {
    if (!selectedAppointment || !rescheduleData.date || !rescheduleData.time) {
      alert("Please select a date and time");
      return;
    }

    try {
      const newDateTime = `${rescheduleData.date}T${rescheduleData.time}`;
      
      // Simulate API call to reschedule appointment
      const response = await tokenManager.put(`http://localhost:8000/api/v1/appointments/${selectedAppointment.id}`, {
        appointment_datetime: newDateTime
      });
      
      if (response.ok) {
        // Update appointment in local state
        setAppointments(prev => prev.map(apt => 
          apt.id === selectedAppointment.id 
            ? { ...apt, appointment_datetime: newDateTime }
            : apt
        ));
        
        closeModal();
        alert("✅ Appointment rescheduled successfully!");
      } else {
        throw new Error("Failed to reschedule appointment");
      }
    } catch (error) {
      console.error("Error rescheduling appointment:", error);
      alert("❌ Failed to reschedule appointment. Please try again.");
    }
  };

  const handleLeaveReview = (appointment) => {
    // Navigate to review page or open review modal
    const workshop = getWorkshopInfo(appointment.workshop_id);
    alert(`🌟 Review feature coming soon!\n\nYou would be leaving a review for:\n${workshop?.name || 'Workshop'}\nService: ${appointment.service_type}`);
  };

  const openReviewModal = (appointment) => {
    setSelectedAppointmentForReview(appointment);
    setReviewData({
      rating: 0,
      comment: '',
      recommend: true
    });
    setShowReviewModal(true);
  };
  
  const closeReviewModal = () => {
    setShowReviewModal(false);
    setSelectedAppointmentForReview(null);
    setReviewData({
      rating: 0,
      comment: '',
      recommend: true
    });
  };
  
  const handleStarClick = (rating) => {
    setReviewData(prev => ({
      ...prev,
      rating: rating
    }));
  };
  
  const handleReviewSubmit = async () => {
    if (!selectedAppointmentForReview || reviewData.rating === 0) {
      alert('Please select a rating before submitting');
      return;
    }
  
    try {
      setSubmitingReview(true);
      
      const reviewPayload = {
        workshop_id: selectedAppointmentForReview.workshop_id,
        appointment_id: selectedAppointmentForReview.id,
        rating: reviewData.rating,
        comment: reviewData.comment.trim(),
        recommend: reviewData.recommend
      };
  
      console.log('🔍 Submitting review:', reviewPayload);
  
      const response = await tokenManager.post("http://localhost:8000/api/v1/reviews/", reviewPayload);
      
      if (response.ok) {
        const responseData = await response.json();
        console.log('✅ Review submitted successfully:', responseData);
        
        closeReviewModal();
        alert('✅ Thank you for your review! Your feedback helps other users.');
        
        await fetchData();
        
        localStorage.setItem('workshopsUpdated', 'true');
        
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      }
    } catch (error) {
      console.error('❌ Network error submitting review:', error);
      alert('❌ Network error. Please check your connection and try again.');
    } finally {
      setSubmitingReview(false);
    }
  };

  if (loading) {
    return (
      <div className="maintenance-container">
        <div className="maintenance-header">
          <div className="header-buttons">
            <button onClick={() => navigate("/dashboard")} className="back-button">
              ← Back to Dashboard
            </button>
            <button onClick={() => navigate("/appointments/book")} className="new-appointment-button">
              📅 Book New Service
            </button>
          </div>
          <h2>📊 Service History</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="maintenance-container">
      <div className="maintenance-header">
        <button onClick={() => navigate("/dashboard")} className="back-button">
          ← Back to Dashboard
        </button>
        <h2>📊 Service History</h2>
        <button 
          onClick={() => navigate("/appointments/book")}
          className="new-appointment-button"
        >
          📅 Book New Service
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Filters */}
      <div className="filters-container">
        <div className="filter-group">
          <label>Filter by Vehicle:</label>
          <select 
            value={selectedVehicle} 
            onChange={(e) => setSelectedVehicle(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Vehicles</option>
            {vehicles.map(vehicle => (
              <option key={vehicle.id} value={vehicle.id}>
                {vehicle.make} {vehicle.model} ({vehicle.license_plate})
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Filter by Status:</label>
          <select 
            value={selectedStatus} 
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Services</option>
            <option value="completed">Completed Only</option>
            <option value="upcoming">Upcoming Only</option>
          </select>
        </div>
      </div>

      {/* Statistics */}
      <div className="stats-container">
        <div className="stat-card">
          <h3>{appointments.length}</h3>
          <p>Total Services</p>
        </div>
        <div className="stat-card">
          <h3>{appointments.filter(a => isCompleted(a.appointment_datetime)).length}</h3>
          <p>Completed</p>
        </div>
        <div className="stat-card">
          <h3>{appointments.filter(a => !isCompleted(a.appointment_datetime)).length}</h3>
          <p>Upcoming</p>
        </div>
        <div className="stat-card">
          <h3>{vehicles.length}</h3>
          <p>Vehicles</p>
        </div>
      </div>

      {/* Service History List */}
      <div className="history-list">
        {sortedAppointments.length === 0 ? (
          <div className="no-history">
            <h3>📝 No service history found</h3>
            <p>No services match your current filters.</p>
            <button 
              onClick={() => navigate("/appointments/book")}
              className="primary-button"
            >
              📅 Book Your First Service
            </button>
          </div>
        ) : (
          sortedAppointments.map((appointment) => {
            const vehicle = getVehicleInfo(appointment.vehicle_id);
            const workshop = getWorkshopInfo(appointment.workshop_id);
            const completed = isCompleted(appointment.appointment_datetime);

            return (
              <div key={appointment.id} className={`history-card ${completed ? 'completed' : 'upcoming'}`}>
                <div className="history-header">
                  <div className="service-info">
                    <h3>{appointment.service_type || 'General Service'}</h3>
                    <span className={`status-badge ${completed ? 'completed' : 'upcoming'}`}>
                      {completed ? 'COMPLETED' : 'UPCOMING'}
                    </span>
                  </div>
                  <div className="service-date">
                    {formatDate(appointment.appointment_datetime)}
                  </div>
                </div>

                <div className="history-details">
                  <div className="detail-row">
                    <span className="detail-label">🚗 Vehicle:</span>
                    <span className="detail-value">{vehicle}</span>
                  </div>
                  
                  {workshop && (
                    <>
                      <div className="detail-row">
                        <span className="detail-label">🏪 Workshop:</span>
                        <span className="detail-value">{workshop.name}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">📍 Location:</span>
                        <span className="detail-value">{workshop.city}</span>
                      </div>
                      {workshop.phone && (
                        <div className="detail-row">
                          <span className="detail-label">📞 Phone:</span>
                          <span className="detail-value">{workshop.phone}</span>
                        </div>
                      )}
                    </>
                  )}

                  {appointment.estimated_cost && (
                    <div className="detail-row">
                      <span className="detail-label">💰 Estimated Cost:</span>
                      <span className="detail-value">${appointment.estimated_cost}</span>
                    </div>
                  )}

                  {appointment.actual_cost && (
                    <div className="detail-row">
                      <span className="detail-label">💳 Actual Cost:</span>
                      <span className="detail-value">${appointment.actual_cost}</span>
                    </div>
                  )}

                  {appointment.customer_notes && (
                    <div className="detail-row">
                      <span className="detail-label">📝 Notes:</span>
                      <span className="detail-value">{appointment.customer_notes}</span>
                    </div>
                  )}
                </div>
                <div className="history-actions">
                  {!completed && (
                    <>
                    <button className="action-button cancel-button" onClick={() => openModal("cancel", appointment)}>
                      ❌ Cancel
                    </button>
                    <button className="action-button reschedule-button" onClick={() => openModal("reschedule", appointment)}>
                      📅 Reschedule
                    </button>
                    </>
                  )}
                {workshop && (
                  <button className="action-button contact-button" onClick={() => handleCallWorkshop(workshop.phone)}>
                    📞 Call Workshop
                  </button>
                )}
                {completed && (
                  <button 
                    onClick={() => openReviewModal(appointment)}
                    className="action-button review-button"
                  >
                    ⭐ Leave Review
                  </button>
                )}
              </div>
            </div>
            );
          })
        )}
      </div>

      {/* Confirmation Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                {modalType === "cancel" ? "🗑️ Cancel Appointment" : "📅 Reschedule Appointment"}
              </h3>
              <button className="modal-close" onClick={closeModal}>✕</button>
            </div>

            <div className="modal-body">
              {modalType === "cancel" ? (
                <div>
                  <p>Are you sure you want to cancel this appointment?</p>
                  <div className="appointment-summary">
                    <strong>{selectedAppointment?.service_type}</strong>
                    <br />
                    {formatDate(selectedAppointment?.appointment_datetime)}
                    <br />
                    {getWorkshopInfo(selectedAppointment?.workshop_id)?.name}
                  </div>
                  <p className="warning-text">⚠️ This action cannot be undone.</p>
                </div>
              ) : (
                <div>
                  <p>Select a new date and time for your appointment:</p>
                  <div className="appointment-summary">
                    <strong>{selectedAppointment?.service_type}</strong>
                    <br />
                    {getWorkshopInfo(selectedAppointment?.workshop_id)?.name}
                  </div>
                  
                  <div className="reschedule-inputs">
                    <div className="input-group">
                      <label>New Date:</label>
                      <input
                        type="date"
                        value={rescheduleData.date}
                        onChange={(e) => setRescheduleData(prev => ({...prev, date: e.target.value}))}
                        min={new Date().toISOString().split('T')[0]}
                      />
                    </div>
                    <div className="input-group">
                      <label>New Time:</label>
                      <input
                        type="time"
                        value={rescheduleData.time}
                        onChange={(e) => setRescheduleData(prev => ({...prev, time: e.target.value}))}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="modal-actions">
              <button className="modal-button secondary" onClick={closeModal}>
                Cancel
              </button>
              <button 
                className={`modal-button ${modalType === "cancel" ? "danger" : "primary"}`}
                onClick={modalType === "cancel" ? handleCancelAppointment : handleRescheduleAppointment}
              >
                {modalType === "cancel" ? "🗑️ Yes, Cancel" : "📅 Reschedule"}
              </button>
            </div>
          </div>
        </div>
      )}
    {/* Review Modal */}
    {showReviewModal && selectedAppointmentForReview && (
      <div className="modal-overlay" onClick={closeReviewModal}>
        <div className="review-modal" onClick={(e) => e.stopPropagation()}>
          {/* Header */}
          <div className="review-modal-header">
            <h3>⭐ Rate Your Experience</h3>
            <button 
              onClick={closeReviewModal}
              className="modal-close-btn"
            >
              ✕
            </button>
          </div>

          {/* Service Info */}
          <div className="review-service-info">
            <div className="service-details">
              <h4>{selectedAppointmentForReview.service_type}</h4>
              <p>🏪 {workshops.find(w => w.id === selectedAppointmentForReview.workshop_id)?.name || 'Workshop'}</p>
              <p>📅 {new Date(selectedAppointmentForReview.appointment_datetime).toLocaleDateString('en-US', {
                weekday: 'short',
                year: 'numeric',
                month: 'short',
                day: 'numeric'
              })}</p>
            </div>
          </div>

          {/* Star Rating */}
          <div className="rating-section">
            <label className="review-label">How would you rate this service?</label>
            <div className="star-rating">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  className={`star ${star <= reviewData.rating ? 'active' : ''}`}
                  onClick={() => handleStarClick(star)}
                >
                  ⭐
                </button>
              ))}
            </div>
            <p className="rating-text">
              {reviewData.rating === 0 && "Select a rating"}
              {reviewData.rating === 1 && "😞 Poor"}
              {reviewData.rating === 2 && "😐 Fair"}
              {reviewData.rating === 3 && "🙂 Good"}
              {reviewData.rating === 4 && "😊 Very Good"}
              {reviewData.rating === 5 && "🤩 Excellent"}
            </p>
          </div>

          {/* Comment Section */}
          <div className="comment-section">
            <label className="review-label">Tell us about your experience</label>
            <textarea
              value={reviewData.comment}
              onChange={(e) => setReviewData(prev => ({ ...prev, comment: e.target.value }))}
              placeholder="Share details about the service quality, timeliness, staff friendliness, pricing, etc..."
              className="review-textarea"
              maxLength={500}
            />
            <div className="char-count">
              {reviewData.comment.length}/500
            </div>
          </div>

          {/* Recommendation */}
          <div className="recommendation-section">
            <label className="checkbox-container">
              <input
                type="checkbox"
                checked={reviewData.recommend}
                onChange={(e) => setReviewData(prev => ({ ...prev, recommend: e.target.checked }))}
              />
              <span className="checkmark"></span>
              I would recommend this workshop to others
            </label>
          </div>

          {/* Buttons */}
          <div className="review-modal-buttons">
            <button 
              onClick={closeReviewModal}
              className="cancel-review-btn"
              disabled={submitingReview}
            >
              Cancel
            </button>
            <button 
              onClick={handleReviewSubmit}
              className="submit-review-btn"
              disabled={submitingReview || reviewData.rating === 0}
            >
              {submitingReview ? '📤 Submitting...' : '✅ Submit Review'}
            </button>
          </div>
        </div>
      </div>
    )}
    </div>
  );
}

export default MaintenanceLogs;