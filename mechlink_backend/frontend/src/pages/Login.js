import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Login.css";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/v1/auth/login-json", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("user_email", data.user.email);
        localStorage.setItem("user_role", data.user.role || "user");
        localStorage.setItem("user_id", data.user.id);
        navigate("/dashboard");
      } else {
        setError(data.detail || "Login failed");
      }
    } catch (error) {
      setError("Server error");
    }
  };

  return (
    <div className="login-container">
      <div className="login-form-wrapper">
        <div className="login-form-section">
          <div className="login-header">
            <h2>Welcome Back</h2>
            <p>Sign in to your MechLink account</p>
          </div>

          <form className="login-form" onSubmit={handleLogin}>
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
            <button type="submit">Sign In</button>
            {error && <div className="error">{error}</div>}
          </form>

          <div className="login-link">
            Don't have an account?{" "}
            <span onClick={() => navigate("/register")}>Create one here</span>
          </div>
        </div>

        <div className="login-brand-section">
          <div className="login-brand-logo">🚗</div>
          <h1 className="login-brand-title">MechLink</h1>
          <p className="login-brand-subtitle">Your ultimate vehicle maintenance companion</p>
          
          <div className="login-features">
            <div className="login-feature">
              <div className="login-feature-icon">🔧</div>
              <div className="login-feature-text">Find trusted mechanics</div>
            </div>
            <div className="login-feature">
              <div className="login-feature-icon">📅</div>
              <div className="login-feature-text">Easy appointment booking</div>
            </div>
            <div className="login-feature">
              <div className="login-feature-icon">📊</div>
              <div className="login-feature-text">Track maintenance history</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;