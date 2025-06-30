import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Favorites.css';

function Favorites() {
  const navigate = useNavigate();
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCity, setSelectedCity] = useState('');

  useEffect(() => {
    console.log("🔍 useEffect ejecutándose - llamando loadFavorites");
    loadFavorites();
  }, []);

  const loadFavorites = () => {
    try {
      setLoading(true);
      const savedFavorites = JSON.parse(localStorage.getItem('favorites') || '[]');
      
      console.log("🔍 loadFavorites - raw localStorage:", localStorage.getItem('favorites'));
      console.log("🔍 loadFavorites - parsed favorites:", savedFavorites);
      console.log("🔍 loadFavorites - favorites length:", savedFavorites.length);
      
      setFavorites(savedFavorites);
    } catch (error) {
      console.error('Error loading favorites:', error);
      setFavorites([]);
    } finally {
      setLoading(false);
    }
  };

  const removeFavorite = (workshopId) => {
    try {
      const updatedFavorites = favorites.filter(workshop => workshop.id !== workshopId);
      localStorage.setItem('favorites', JSON.stringify(updatedFavorites));
      setFavorites(updatedFavorites);
      alert('❌ Workshop removed from favorites');
    } catch (error) {
      console.error('Error removing favorite:', error);
      alert('❌ Error removing from favorites');
    }
  };

  const clearAllFavorites = () => {
    if (window.confirm('Are you sure you want to remove all favorites? This action cannot be undone.')) {
      try {
        localStorage.setItem('favorites', JSON.stringify([]));
        setFavorites([]);
        alert('✅ All favorites cleared');
      } catch (error) {
        console.error('Error clearing favorites:', error);
        alert('❌ Error clearing favorites');
      }
    }
  };

  const filteredFavorites = favorites.filter(workshop => {
    const matchesSearch = workshop.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         workshop.city.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCity = selectedCity === '' || workshop.city === selectedCity;
    return matchesSearch && matchesCity;
  });

  const cities = [...new Set(favorites.map(workshop => workshop.city))].sort();

  return (
    <div className="favorites-container">
      <div className="favorites-header">
        <div className="header-top">
          <button 
            onClick={() => navigate('/dashboard')} 
            className="back-button"
          >
            ← Back to Dashboard
          </button>
          
          <h1 className="header-title">⭐ Favorite Workshops</h1>
          
          {favorites.length > 0 && (
            <button onClick={clearAllFavorites} className="clear-all-button">
              🗑️ Clear All
            </button>
          )}
        </div>
      </div>
  
      {loading ? (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading your favorite workshops...</p>
        </div>
      ) : favorites.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">⭐</div>
          <h3>No Favorite Workshops Yet</h3>
          <p>Start adding workshops to your favorites from the search page!</p>
          <button 
            onClick={() => navigate('/dashboard')} 
            className="cta-button"
          >
            🔍 Search Workshops
          </button>
        </div>
      ) : (
        <>
          <div className="stats-container">
            <div className="stat-card">
              <div className="stat-number">{favorites.length}</div>
              <div className="stat-label">Total Favorites</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{cities.length}</div>
              <div className="stat-label">Cities</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{filteredFavorites.length}</div>
              <div className="stat-label">Showing</div>
            </div>
          </div>
  
          <div className="filters-container">
            <div className="filters-grid">
              <div className="filter-group">
                <label className="filter-label">Search Workshops</label>
                <input
                  type="text"
                  placeholder="🔍 Search by name or city..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="search-input"
                />
              </div>
              
              <div className="filter-group">
                <label className="filter-label">Filter by City</label>
                <select
                  value={selectedCity}
                  onChange={(e) => setSelectedCity(e.target.value)}
                  className="city-filter"
                >
                  <option value="">🏙️ All Cities</option>
                  {cities.map(city => (
                    <option key={city} value={city}>{city}</option>
                  ))}
                </select>
              </div>
  
              {(searchTerm || selectedCity) && (
                <button 
                  onClick={() => {
                    setSearchTerm('');
                    setSelectedCity('');
                  }}
                  className="clear-filters-button"
                >
                  ✨ Clear Filters
                </button>
              )}
            </div>
          </div>
  
          <div className="favorites-list">
            {filteredFavorites.length === 0 ? (
              <div className="no-results">
                <p>No workshops match your search criteria.</p>
                <button 
                  onClick={() => {
                    setSearchTerm('');
                    setSelectedCity('');
                  }}
                  className="clear-filters-button"
                >
                  Clear Filters
                </button>
              </div>
            ) : (
              filteredFavorites.map((workshop) => (
                <div key={workshop.id} className="favorite-card">
                  <div className="favorite-header">
                    <h3>{workshop.name}</h3>
                    <div className="favorite-actions">
                      <span className="added-date">
                        Added {new Date(workshop.addedToFavorites).toLocaleDateString()}
                      </span>
                      <button
                        onClick={() => removeFavorite(workshop.id)}
                        className="remove-button"
                        title="Remove from favorites"
                      >
                        ❌
                      </button>
                    </div>
                  </div>
  
                  <div className="favorite-info">
                    <div className="info-section">
                      <p><span className="icon">📍</span> {workshop.address || workshop.city}</p>
                      <p><span className="icon">📞</span> {workshop.phone}</p>
                      <p><span className="icon">⏰</span> {workshop.business_hours || 'Mon-Fri 8:00 AM - 6:00 PM'}</p>
                    </div>
                    
                    <div className="info-section">
                      <p><span className="icon">🔧</span> {workshop.services?.join(', ') || workshop.specialties?.join(', ') || 'General Repair'}</p>
                      <p><span className="icon">⭐</span> {workshop.rating_average || workshop.rating || '4.5'}/5 ({workshop.total_reviews || workshop.review_count || '12'} reviews)</p>
                      {workshop.description && (
                        <p><span className="icon">📝</span> {workshop.description}</p>
                      )}
                    </div>
                  </div>
  
                  <div className="favorite-actions-bottom">
                    <button 
                      onClick={() => navigate("/appointments/book")}
                      className="book-button"
                    >
                      📅 Book Appointment
                    </button>
                    <button 
                      onClick={() => window.open(`tel:${workshop.phone}`, '_self')}
                      className="call-button"
                    >
                      📞 Call
                    </button>
                    <button 
                      onClick={() => window.open(`https://maps.google.com/?q=${encodeURIComponent((workshop.address || '') + ', ' + workshop.city)}`, '_blank')}
                      className="directions-button"
                    >
                      🗺️ Directions
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default Favorites;