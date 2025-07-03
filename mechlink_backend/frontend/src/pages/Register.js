import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Register.css";

function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phone, setPhone] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setMessage("");

    try {
      const response = await fetch("http://localhost:8000/api/v1/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
          first_name: firstName,
          last_name: lastName,
          phone,
        }),
      });
  
      const data = await response.json();
  
      if (response.ok) {
        // ✅ FIX: Login automatically after registration
        const loginResponse = await fetch("http://localhost:8000/api/v1/auth/login-json", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email,
            password,
          }),
        });
  
        const loginData = await loginResponse.json();
  
        if (loginResponse.ok) {
          // Save token and redirect to dashboard
          localStorage.setItem("token", loginData.access_token);
          localStorage.setItem("user_email", loginData.user.email);
          localStorage.setItem("user_role", loginData.user.role || "user");
          localStorage.setItem("user_id", loginData.user.id);
          navigate("/dashboard"); // ← Go directly to dashboard
        } else {
          // If auto-login fails, go to login page
          setMessage("Account created! Please login.");
          setTimeout(() => navigate("/login"), 2000);
        }
      } else {
        setMessage(data.detail || "Registration failed");
      }
    } catch (error) {
      setMessage("Error connecting to server");
    }
  };

  return (
    <div className="register-container">
      <div className="register-form-wrapper">
        <div className="register-brand-section">
          <div className="register-brand-logo">🚗</div>
          <h1 className="register-brand-title">MechLink</h1>
          <p className="register-brand-subtitle">Join thousands of satisfied vehicle owners</p>
          
          <div className="register-features">
            <div className="register-feature">
              <div className="register-feature-icon">⭐</div>
              <div className="register-feature-text">Rate & review services</div>
            </div>
            <div className="register-feature">
              <div className="register-feature-icon">🔔</div>
              <div className="register-feature-text">Smart notifications</div>
            </div>
            <div className="register-feature">
              <div className="register-feature-icon">📱</div>
              <div className="register-feature-text">Mobile-friendly design</div>
            </div>
          </div>
        </div>

        <div className="register-form-section">
          <div className="register-header">
            <h2>Join MechLink</h2>
            <p>Create your account and start managing your vehicles</p>
          </div>

          <form className="register-form" onSubmit={handleRegister}>
            <input
              type="text"
              placeholder="First Name"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              required
            />
            <input
              type="text"
              placeholder="Last Name"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              required
            />
            <input
              type="tel"
              placeholder="Phone Number"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
            <input
              type="email"
              placeholder="Email Address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button type="submit">Create Account</button>
            {message && (
              <div className={`message ${message.includes("created") || message.includes("Account") ? "success" : "error"}`}>
                {message}
              </div>
            )}
          </form>

          <div className="register-link">
            Already have an account?{" "}
            <span onClick={() => navigate("/login")}>Sign in here</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Register;