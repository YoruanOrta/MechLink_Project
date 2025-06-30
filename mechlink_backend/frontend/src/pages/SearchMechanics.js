import React, { useState } from 'react';
import axios from 'axios';
import '../styles/SearchMechanics.css';

const SearchMechanics = () => {
  const [city, setCity] = useState('');
  const [service, setService] = useState('');
  const [workshops, setWorkshops] = useState([]);

  const handleSearch = async () => {
    try {
      const response = await axios.get('http://localhost:8000/workshops', {
        params: { city, service_type: service },
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setWorkshops(response.data);
    } catch (error) {
      console.error('Error fetching workshops:', error);
    }
  };

  return (
    <div className="search-mechanics-container">
      <h2>Search Mechanics</h2>

      <div className="search-inputs">
        <input
          type="text"
          placeholder="Enter city"
          value={city}
          onChange={(e) => setCity(e.target.value)}
        />
        <input
          type="text"
          placeholder="Enter service"
          value={service}
          onChange={(e) => setService(e.target.value)}
        />
        <button onClick={handleSearch} className="search-button">
          Search
        </button>
      </div>

      <ul className="results-list">
        {workshops.map((w) => (
          <li key={w.id}>{w.name} - {w.city}</li>
        ))}
      </ul>
    </div>
  );
};

export default SearchMechanics;
