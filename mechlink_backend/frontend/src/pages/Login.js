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
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("user_email", data.user.email);
        localStorage.setItem("user_role", data.user.role || "user"); // si tienes roles
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
      <h2>Login</h2>
      <form className="login-form" onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
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

        <button type="submit">Login</button>
        {error && <div className="error">{error}</div>}
        <p style={{ marginTop: "10px" }}>
          Don’t have an account?{" "}
          <span
            onClick={() => navigate("/register")}
            style={{ cursor: "pointer", color: "#0077cc" }}
          >
            Register
          </span>
        </p>
      </form>
    </div>
  );
}

export default Login;
