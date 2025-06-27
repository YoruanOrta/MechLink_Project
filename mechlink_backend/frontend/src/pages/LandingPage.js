import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/LandingPage.css";
import { Wrench } from "lucide-react";

function LandingPage() {
  const navigate = useNavigate();

  const testimonials = [
    {
      name: "Robert Fonseca",
      image: "/images/user1.jpg",
      quote: "MechLink saved me from missing a major service appointment. Fantastic platform!"
    },
    {
      name: "Sarah Williams",
      image: "/images/user2.jpg",
      quote: "The reminders and smooth booking made it super easy. Highly recommend!"
    },
    {
      name: "Carlos Rivera",
      image: "/images/user3.jpg",
      quote: "Thanks to MechLink, I always know when to take my car for maintenance!"
    }
  ];

  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) =>
        prevIndex === testimonials.length - 1 ? 0 : prevIndex + 1
      );
    }, 5000);

    return () => clearInterval(interval);
  }, [testimonials.length]);

  const prevTestimonial = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === 0 ? testimonials.length - 1 : prevIndex - 1
    );
  };

  const nextTestimonial = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === testimonials.length - 1 ? 0 : prevIndex + 1
    );
  };

  return (
    <div className="landing-page">
      <header className="navbar">
        <div className="logo">
          <span className="logo-text">MechLink</span>
          <Wrench className="logo-icon" />
        </div>
        <nav>
          <ul>
            <li><a href="#features">Features</a></li>
            <li><a href="#how-it-works">How it Works</a></li>
            <li className="auth-buttons">
              <button onClick={() => navigate("/login")}>Login</button>
              <span className="divider">/</span>
              <button onClick={() => navigate("/register")}>Register</button>
            </li>
          </ul>
        </nav>
      </header>

      <section className="hero">
        <img
          src="/images/Mechanic-image.jpeg"
          alt="Mechanic working"
          className="hero-bg"
        />
        <div className="hero-content">
          <h1>Your Vehicle Maintenance Assistant</h1>
          <p>Schedule services, manage vehicles, and never miss maintenance again.</p>
          <button onClick={() => navigate("/register")}>Get Started</button>
        </div>
      </section>
      <section className="why-choose-us">
  <h2>Why Choose MechLink?</h2>
  <ul>
    <li>🔒 Verified Workshops</li>
    <li>📅 Automated Service Reminders</li>
    <li>📘 Digital Service History</li>
    <li>💬 Fast and Reliable Customer Support</li>
  </ul>
</section>

      <section className="testimonial-section">
        <h2 className="testimonial-title">Testimonials</h2>
        <p className="testimonial-subtitle">Here’s what our customers are saying about MechLink</p>
        <div className="testimonial-wrapper">
          <button className="arrow left" onClick={prevTestimonial}>‹</button>

          <div className="testimonial-card">
            <img
              src={testimonials[currentIndex].image}
              alt={testimonials[currentIndex].name}
              className="testimonial-image"
            />
            <p className="testimonial-quote">"{testimonials[currentIndex].quote}"</p>
            <p className="testimonial-name">— {testimonials[currentIndex].name}</p>
          </div>

          <button className="arrow right" onClick={nextTestimonial}>›</button>
        </div>
      </section>

      <section id="how-it-works" className="how-it-works-modern">
  <h2>How it Works</h2>
  <div className="how-cards">
    <div className="how-card">
      <span className="how-icon">📝</span>
      <h4>Create an account</h4>
      <p>Register and add your vehicle to your personal garage.</p>
    </div>
    <div className="how-card">
      <span className="how-icon">🔧</span>
      <h4>Find a workshop</h4>
      <p>Browse and book services from nearby workshops.</p>
    </div>
    <div className="how-card">
      <span className="how-icon">📅</span>
      <h4>Track & Remind</h4>
      <p>Stay updated with reminders and maintenance logs.</p>
    </div>
  </div>
</section>
<section className="map-preview-section">
  <h2>📍 Find Mechanic Workshops near of you in just seconds!</h2>
  <p>Use our smart search and easily locate workshops based on your location.</p>
  <img src="/images/map-preview.png" alt="Mapa con talleres" className="map-image" />
  <button onClick={() => navigate("/dashboard")} className="map-cta">
    Explore Workshops
  </button>
</section>

      <footer className="footer">
        <p>© {new Date().getFullYear()} MechLink | All rights reserved</p>
      </footer>
    </div>
  );
}

export default LandingPage;

