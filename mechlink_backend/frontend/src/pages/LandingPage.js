import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

function NewLandingPage() {
  const navigate = useNavigate();

  const testimonials = [
    {
      name: "María González",
      location: "San Juan",
      image: "/images/user1.jpg",
      quote: "Finally found a reliable mechanic in Bayamón! MechLink made it so easy"
    },
    {
      name: "Carlos Rivera", 
      location: "Ponce",
      image: "/images/user2.jpg",
      quote: "Never miss my oil changes anymore. The reminders are perfect!"
    },
    {
      name: "Ana Morales",
      location: "Caguas", 
      image: "/images/user3.jpg",
      quote: "Best app for car maintenance in PR. Super easy to use!"
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

  const nextTestimonial = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === testimonials.length - 1 ? 0 : prevIndex + 1
    );
  };

  const prevTestimonial = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === 0 ? testimonials.length - 1 : prevIndex - 1
    );
  };

  return (
    <div className="premium-landing">
      {/* Navigation */}
      <nav className="premium-nav">
        <div className="nav-container">
          <div className="logo-section">
            <span className="car-icon">🚗</span>
            <span className="logo-text">MechLink</span>
          </div>
          
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#how-it-works">How it Works</a>
            <a href="#team">Team</a>
            <a href="#testimonials">Reviews</a>
          </div>
          
          <div className="auth-section">
            <button className="btn-login" onClick={() => navigate("/login")}>
              Login
            </button>
            <button className="btn-signup" onClick={() => navigate("/register")}>
              Sign Up
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-container">
          <div className="hero-content">
            <h1 className="hero-title">
              Never Miss Vehicle<br />
              <span className="highlight">Maintenance Again</span>
            </h1>
            <p className="hero-subtitle">
              Find trusted workshops, schedule appointments, and get smart reminders
              — all in Puerto Rico
            </p>
            <div className="hero-buttons">
              <button className="btn-primary" onClick={() => navigate("/register")}>
                🚀 Get Started Free
              </button>
              <button className="btn-secondary">
                ▶️ Watch Demo
              </button>
            </div>
          </div>
          
          <div className="hero-visual">
            <div className="phone-mockup">
              <img src="/images/logo_de_mi_app.jpg" alt="MechLink App" className="app-screenshot" />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <div className="container">
          <h2 className="section-title">Why Choose MechLink?</h2>
          <p className="section-subtitle">Everything you need in one app</p>
          
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🗺️</div>
              <h3>Find Workshops</h3>
              <p>Locate trusted mechanics nearby with ratings and reviews</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">📅</div>
              <h3>Easy Booking</h3>
              <p>Schedule appointments in seconds with real-time availability</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🔔</div>
              <h3>Smart Alerts</h3>
              <p>Never miss maintenance with automated reminders</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Track History</h3>
              <p>Complete service records and maintenance tracking</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">⭐</div>
              <h3>Reviews & Ratings</h3>
              <p>See what others say about workshops and services</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🇵🇷</div>
              <h3>Made for Puerto Rico</h3>
              <p>Optimized for the island with local workshop network</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="how-it-works-section">
        <div className="container">
          <h2 className="section-title">How It Works</h2>
          <p className="section-subtitle">Simple as 1-2-3-4</p>
          
          <div className="steps-container">
            <div className="step">
              <div className="step-number">1</div>
              <div className="step-content">
                <h3>Add Vehicle</h3>
                <p>Register your car with make, model, and mileage</p>
              </div>
            </div>
            
            <div className="step-arrow">→</div>
            
            <div className="step">
              <div className="step-number">2</div>
              <div className="step-content">
                <h3>Find Workshop</h3>
                <p>Search nearby mechanics by location or service</p>
              </div>
            </div>
            
            <div className="step-arrow">→</div>
            
            <div className="step">
              <div className="step-number">3</div>
              <div className="step-content">
                <h3>Book Service</h3>
                <p>Schedule appointment with available time slots</p>
              </div>
            </div>
            
            <div className="step-arrow">→</div>
            
            <div className="step">
              <div className="step-number">4</div>
              <div className="step-content">
                <h3>Get Reminded</h3>
                <p>Receive smart notifications for upcoming services</p>
              </div>
            </div>
          </div>
          
          <div className="demo-button-container">
            <button className="btn-demo">🎬 See It In Action</button>
          </div>
        </div>
      </section>

      {/* Meet the Team */}
      <section id="team" className="team-section">
        <div className="container">
          <h2 className="section-title">Meet the Team</h2>
          <p className="section-subtitle">The minds behind MechLink</p>
          
          <div className="team-grid">
            <div className="team-member">
              <div className="member-photo">
                <img src="/images/user1.jpg" alt="Backend Developer" />
              </div>
              <div className="member-info">
                <h3>🔧 Backend Developer</h3>
                <h4>[Your Name]</h4>
                <p>"Built the powerful API that makes everything work"</p>
                <div className="tech-stack">
                  <span className="tech-tag">🚀 FastAPI + Python</span>
                  <span className="tech-tag">📧 Email System</span>
                  <span className="tech-tag">🗺️ Puerto Rico Maps</span>
                  <span className="tech-tag">🔔 Notifications</span>
                </div>
                <div className="social-links">
                  <button className="social-btn">🔗 LinkedIn</button>
                  <button className="social-btn">📧 Email</button>
                </div>
              </div>
            </div>
            
            <div className="team-member">
              <div className="member-photo">
                <img src="/images/user2.jpg" alt="Frontend Developer" />
              </div>
              <div className="member-info">
                <h3>🎨 Frontend Developer</h3>
                <h4>[Friend's Name]</h4>
                <p>"Created the beautiful user experience"</p>
                <div className="tech-stack">
                  <span className="tech-tag">⚛️ React + JS</span>
                  <span className="tech-tag">🎨 UI/UX Design</span>
                  <span className="tech-tag">📱 Mobile First</span>
                  <span className="tech-tag">🗺️ Map Integration</span>
                </div>
                <div className="social-links">
                  <button className="social-btn">🔗 LinkedIn</button>
                  <button className="social-btn">📧 Email</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="testimonials-section">
        <div className="container">
          <h2 className="section-title">What Puerto Rico Says</h2>
          
          <div className="testimonial-container">
            <button className="testimonial-arrow left" onClick={prevTestimonial}>
              ‹
            </button>
            
            <div className="testimonial-card">
              <div className="stars">⭐⭐⭐⭐⭐</div>
              <p className="testimonial-text">
                "{testimonials[currentIndex].quote}"
              </p>
              <div className="testimonial-author">
                <img 
                  src={testimonials[currentIndex].image} 
                  alt={testimonials[currentIndex].name}
                  className="author-photo"
                />
                <div className="author-info">
                  <span className="author-name">{testimonials[currentIndex].name}</span>
                  <span className="author-location">{testimonials[currentIndex].location}</span>
                </div>
              </div>
            </div>
            
            <button className="testimonial-arrow right" onClick={nextTestimonial}>
              ›
            </button>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-content">
            <h2>Ready to take control of your vehicle maintenance?</h2>
            <p>Join hundreds of Puerto Rican drivers already using MechLink</p>
            <button className="btn-cta-final" onClick={() => navigate("/register")}>
              🚗 Start Managing Your Car Now
            </button>
            <div className="cta-features">
              <span>Free forever</span>
              <span>•</span>
              <span>No credit card</span>
              <span>•</span>
              <span>Works on any device 📱💻</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="premium-footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand">
              <div className="footer-logo">
                <span className="car-icon">🚗</span>
                <span>MechLink</span>
              </div>
              <p>Puerto Rico's vehicle management platform</p>
            </div>
            
            <div className="footer-links">
              <div className="link-group">
                <h4>Product</h4>
                <a href="#features">Features</a>
                <a href="#how-it-works">How it Works</a>
                <a href="/dashboard">Mobile App</a>
              </div>
              
              <div className="link-group">
                <h4>Company</h4>
                <a href="#team">About Us</a>
                <a href="#testimonials">Reviews</a>
                <a href="/contact">Contact</a>
              </div>
              
              <div className="link-group">
                <h4>Support</h4>
                <a href="/help">Help Center</a>
                <a href="/privacy">Privacy</a>
                <a href="/terms">Terms</a>
              </div>
            </div>
          </div>
          
          <div className="footer-bottom">
            <p>Made with ❤️ in Puerto Rico 🇵🇷</p>
            <p>© 2025 MechLink. All rights reserved.</p>
          </div>
        </div>
      </footer>

      <style jsx>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        .premium-landing {
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
          color: #1f2937;
          line-height: 1.6;
        }

        /* Navigation */
        .premium-nav {
          background: rgba(15, 23, 42, 0.95);
          backdrop-filter: blur(10px);
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          z-index: 1000;
          border-bottom: 1px solid rgba(59, 130, 246, 0.2);
        }

        .nav-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 1rem 2rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .logo-section {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 1.5rem;
          font-weight: bold;
          color: white;
        }

        .car-icon {
          font-size: 1.8rem;
        }

        .nav-links {
          display: flex;
          gap: 2rem;
        }

        .nav-links a {
          color: #e2e8f0;
          text-decoration: none;
          font-weight: 500;
          transition: color 0.3s ease;
        }

        .nav-links a:hover {
          color: #3b82f6;
        }

        .auth-section {
          display: flex;
          gap: 1rem;
        }

        .btn-login {
          background: transparent;
          color: #e2e8f0;
          border: 1px solid #475569;
          padding: 0.5rem 1rem;
          border-radius: 0.5rem;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .btn-login:hover {
          border-color: #3b82f6;
          color: #3b82f6;
        }

        .btn-signup {
          background: linear-gradient(135deg, #3b82f6, #1d4ed8);
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 0.5rem;
          cursor: pointer;
          font-weight: 500;
          transition: transform 0.3s ease;
        }

        .btn-signup:hover {
          transform: translateY(-2px);
        }

        /* Hero Section */
        .hero-section {
          background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
          color: white;
          padding: 8rem 2rem 4rem;
          margin-top: 4rem;
        }

        .hero-container {
          max-width: 1200px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 4rem;
          align-items: center;
        }

        .hero-title {
          font-size: 3.5rem;
          font-weight: bold;
          line-height: 1.1;
          margin-bottom: 1.5rem;
        }

        .highlight {
          background: linear-gradient(135deg, #3b82f6, #06b6d4);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .hero-subtitle {
          font-size: 1.25rem;
          color: #cbd5e1;
          margin-bottom: 2rem;
          line-height: 1.6;
        }

        .hero-buttons {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
        }

        .btn-primary {
          background: linear-gradient(135deg, #3b82f6, #1d4ed8);
          color: white;
          border: none;
          padding: 1rem 2rem;
          border-radius: 0.75rem;
          font-size: 1.1rem;
          font-weight: 600;
          cursor: pointer;
          transition: transform 0.3s ease;
        }

        .btn-primary:hover {
          transform: translateY(-3px);
        }

        .btn-secondary {
          background: transparent;
          color: #e2e8f0;
          border: 2px solid #475569;
          padding: 1rem 2rem;
          border-radius: 0.75rem;
          font-size: 1.1rem;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .btn-secondary:hover {
          border-color: #3b82f6;
          color: #3b82f6;
        }

        .hero-visual {
          display: flex;
          justify-content: center;
          align-items: center;
        }

        .phone-mockup {
          background: linear-gradient(135deg, #1e293b, #334155);
          padding: 2rem;
          border-radius: 2rem;
          box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
          transform: perspective(1000px) rotateY(-15deg);
        }

        .app-screenshot {
          width: 500px;
          height: auto;
          border-radius: 1rem;
        }

        /* Features Section */
        .features-section {
          padding: 5rem 2rem;
          background: #f8fafc;
        }

        .container {
          max-width: 1200px;
          margin: 0 auto;
        }

        .section-title {
          font-size: 2.5rem;
          font-weight: bold;
          text-align: center;
          margin-bottom: 1rem;
          color: #1f2937;
        }

        .section-subtitle {
          font-size: 1.25rem;
          text-align: center;
          color: #6b7280;
          margin-bottom: 3rem;
        }

        .features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 2rem;
        }

        .feature-card {
          background: white;
          padding: 2rem;
          border-radius: 1rem;
          text-align: center;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
          transition: transform 0.3s ease;
          border: 1px solid #e5e7eb;
        }

        .feature-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 20px 25px rgba(0, 0, 0, 0.1);
        }

        .feature-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
        }

        .feature-card h3 {
          font-size: 1.25rem;
          font-weight: 600;
          margin-bottom: 0.5rem;
          color: #1f2937;
        }

        .feature-card p {
          color: #6b7280;
        }

        /* How It Works */
        .how-it-works-section {
          padding: 5rem 2rem;
          background: white;
        }

        .steps-container {
          display: flex;
          justify-content: center;
          align-items: center;
          flex-wrap: wrap;
          gap: 2rem;
          margin-bottom: 3rem;
        }

        .step {
          text-align: center;
          max-width: 200px;
        }

        .step-number {
          width: 4rem;
          height: 4rem;
          background: linear-gradient(135deg, #3b82f6, #1d4ed8);
          color: white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.5rem;
          font-weight: bold;
          margin: 0 auto 1rem;
        }

        .step-content h3 {
          font-size: 1.25rem;
          font-weight: 600;
          margin-bottom: 0.5rem;
          color: #1f2937;
        }

        .step-content p {
          color: #6b7280;
          font-size: 0.9rem;
        }

        .step-arrow {
          font-size: 2rem;
          color: #3b82f6;
          font-weight: bold;
        }

        .demo-button-container {
          text-align: center;
        }

        .btn-demo {
          background: linear-gradient(135deg, #10b981, #059669);
          color: white;
          border: none;
          padding: 1rem 2rem;
          border-radius: 0.75rem;
          font-size: 1.1rem;
          cursor: pointer;
          transition: transform 0.3s ease;
        }

        .btn-demo:hover {
          transform: translateY(-2px);
        }

        /* Team Section */
        .team-section {
          padding: 5rem 2rem;
          background: #f8fafc;
        }

        .team-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
          gap: 3rem;
          max-width: 1000px;
          margin: 0 auto;
        }

        .team-member {
          background: white;
          border-radius: 1.5rem;
          padding: 2rem;
          text-align: center;
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
          transition: transform 0.3s ease;
        }

        .team-member:hover {
          transform: translateY(-5px);
        }

        .member-photo {
          width: 120px;
          height: 120px;
          margin: 0 auto 1.5rem;
          border-radius: 50%;
          overflow: hidden;
          border: 4px solid #3b82f6;
        }

        .member-photo img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .member-info h3 {
          color: #3b82f6;
          font-size: 1.25rem;
          margin-bottom: 0.5rem;
        }

        .member-info h4 {
          color: #1f2937;
          font-size: 1.5rem;
          margin-bottom: 1rem;
        }

        .member-info p {
          color: #6b7280;
          font-style: italic;
          margin-bottom: 1.5rem;
        }

        .tech-stack {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          justify-content: center;
          margin-bottom: 1.5rem;
        }

        .tech-tag {
          background: #eff6ff;
          color: #1d4ed8;
          padding: 0.25rem 0.75rem;
          border-radius: 1rem;
          font-size: 0.8rem;
          font-weight: 500;
        }

        .social-links {
          display: flex;
          gap: 1rem;
          justify-content: center;
        }

        .social-btn {
          background: linear-gradient(135deg, #3b82f6, #1d4ed8);
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 0.5rem;
          cursor: pointer;
          font-size: 0.9rem;
          transition: transform 0.3s ease;
        }

        .social-btn:hover {
          transform: translateY(-2px);
        }

        /* Testimonials */
        .testimonials-section {
          padding: 5rem 2rem;
          background: white;
        }

        .testimonial-container {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 2rem;
          max-width: 800px;
          margin: 0 auto;
        }

        .testimonial-card {
          background: #f8fafc;
          padding: 3rem;
          border-radius: 1.5rem;
          text-align: center;
          min-height: 300px;
          display: flex;
          flex-direction: column;
          justify-content: center;
        }

        .stars {
          font-size: 1.5rem;
          margin-bottom: 1.5rem;
        }

        .testimonial-text {
          font-size: 1.25rem;
          color: #374151;
          font-style: italic;
          margin-bottom: 2rem;
          line-height: 1.6;
        }

        .testimonial-author {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 1rem;
        }

        .author-photo {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          object-fit: cover;
          border: 3px solid #3b82f6;
        }

        .author-info {
          text-align: left;
        }

        .author-name {
          display: block;
          font-weight: 600;
          color: #1f2937;
        }

        .author-location {
          display: block;
          color: #6b7280;
          font-size: 0.9rem;
        }

        .testimonial-arrow {
          background: none;
          border: none;
          font-size: 3rem;
          color: #3b82f6;
          cursor: pointer;
          transition: transform 0.3s ease;
        }

        .testimonial-arrow:hover {
          transform: scale(1.2);
        }

        /* CTA Section */
        .cta-section {
          padding: 5rem 2rem;
          background: linear-gradient(135deg, #1e293b, #0f172a);
          color: white;
          text-align: center;
        }

        .cta-content h2 {
          font-size: 2.5rem;
          margin-bottom: 1rem;
        }

        .cta-content p {
          font-size: 1.25rem;
          color: #cbd5e1;
          margin-bottom: 2rem;
        }

        .btn-cta-final {
          background: linear-gradient(135deg, #3b82f6, #1d4ed8);
          color: white;
          border: none;
          padding: 1.25rem 3rem;
          border-radius: 0.75rem;
          font-size: 1.25rem;
          font-weight: 600;
          cursor: pointer;
          margin-bottom: 1.5rem;
          transition: transform 0.3s ease;
        }

        .btn-cta-final:hover {
          transform: translateY(-3px);
        }

        .cta-features {
          color: #94a3b8;
          font-size: 0.9rem;
        }

        .cta-features span {
          margin: 0 0.5rem;
        }

        /* Footer */
        .premium-footer {
          background: #0f172a;
          color: white;
          padding: 3rem 2rem 1rem;
        }

        .footer-content {
          display: grid;
          grid-template-columns: 1fr 2fr;
          gap: 3rem;
          margin-bottom: 2rem;
        }

        .footer-logo {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 1.5rem;
          font-weight: bold;
          margin-bottom: 1rem;
        }

        .footer-brand p {
          color: #94a3b8;
        }

        .footer-links {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 2rem;
        }

        .link-group h4 {
          color: white;
          margin-bottom: 1rem;
          font-size: 1.1rem;
        }

        .link-group a {
          color: #94a3b8;
          text-decoration: none;
          display: block;
          margin-bottom: 0.5rem;
          transition: color 0.3s ease;
        }

        .link-group a:hover {
          color: #3b82f6;
        }

        .footer-bottom {
          border-top: 1px solid #374151;
          padding-top: 2rem;
          text-align: center;
          color: #94a3b8;
        }

        .footer-bottom p {
          margin-bottom: 0.5rem;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
          .nav-container {
            padding: 1rem;
            flex-direction: column;
            gap: 1rem;
          }

          .nav-links {
            display: none;
          }

          .hero-container {
            grid-template-columns: 1fr;
            gap: 2rem;
            text-align: center;
          }

          .hero-title {
            font-size: 2.5rem;
          }

          .hero-buttons {
            justify-content: center;
          }

          .features-grid {
            grid-template-columns: 1fr;
          }

          .steps-container {
            flex-direction: column;
          }

          .step-arrow {
            transform: rotate(90deg);
            font-size: 1.5rem;
          }

          .team-grid {
            grid-template-columns: 1fr;
          }

          .testimonial-container {
            flex-direction: column;
          }

          .testimonial-arrow {
            order: 3;
          }

          .testimonial-arrow.left {
            order: 1;
          }

          .footer-content {
            grid-template-columns: 1fr;
            text-align: center;
          }

          .footer-links {
            grid-template-columns: 1fr;
            gap: 1rem;
          }
        }

        @media (max-width: 480px) {
          .hero-section {
            padding: 6rem 1rem 3rem;
          }

          .hero-title {
            font-size: 2rem;
          }

          .section-title {
            font-size: 2rem;
          }

          .features-section,
          .how-it-works-section,
          .team-section,
          .testimonials-section,
          .cta-section {
            padding: 3rem 1rem;
          }

          .btn-primary,
          .btn-secondary,
          .btn-cta-final {
            width: 100%;
            margin-bottom: 1rem;
          }

          .hero-buttons {
            flex-direction: column;
          }

          .phone-mockup {
            transform: none;
            padding: 1rem;
          }

          .app-screenshot {
            width: 200px;
          }

          .team-member {
            padding: 1.5rem;
          }

          .testimonial-card {
            padding: 2rem;
            min-height: auto;
          }

          .cta-content h2 {
            font-size: 2rem;
          }

          .premium-footer {
            padding: 2rem 1rem 1rem;
          }
        }

        /* Animations */
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-10px);
          }
        }

        .feature-card,
        .team-member,
        .step {
          animation: fadeInUp 0.6s ease forwards;
        }

        .phone-mockup {
          animation: float 3s ease-in-out infinite;
        }

        /* Hover effects */
        .feature-card:hover .feature-icon {
          transform: scale(1.1);
          transition: transform 0.3s ease;
        }

        .step-number:hover {
          transform: scale(1.1);
          transition: transform 0.3s ease;
        }

        /* Loading states */
        .btn-primary:active,
        .btn-signup:active,
        .btn-cta-final:active {
          transform: scale(0.95);
        }

        /* Focus states for accessibility */
        .btn-primary:focus,
        .btn-secondary:focus,
        .btn-login:focus,
        .btn-signup:focus,
        .social-btn:focus,
        .testimonial-arrow:focus {
          outline: 2px solid #3b82f6;
          outline-offset: 2px;
        }

        /* Smooth scrolling */
        html {
          scroll-behavior: smooth;
        }

        /* Custom scrollbar */
        ::-webkit-scrollbar {
          width: 8px;
        }

        ::-webkit-scrollbar-track {
          background: #f1f5f9;
        }

        ::-webkit-scrollbar-thumb {
          background: #3b82f6;
          border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
          background: #1d4ed8;
        }
      `}</style>
    </div>
  );
}

export default NewLandingPage;