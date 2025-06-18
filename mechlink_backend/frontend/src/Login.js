import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./styles/Login.css";

function Login() {
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage("");

    try {
      const response = await fetch("http://localhost:8000/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const data = await response.json();
        setErrorMessage(data.detail || "Login failed");
        return;
      }

      const data = await response.json();

      // Guarda el token y el user_id en localStorage
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user_id", data.user.id);
      localStorage.setItem("user_email", data.user.email);
      localStorage.setItem("user_role", data.user.role); // si manejas roles

      navigate("/dashboard"); // redirige al dashboard
    } catch (err) {
      setErrorMessage("Network error. Please try again later.");
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit} className="login-form">
        <input
          type="email"
          name="email"
          placeholder="Email"
          required
          value={formData.email}
          onChange={handleChange}
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          required
          value={formData.password}
          onChange={handleChange}
        />
        <button type="submit">Submit</button>
      </form>
      {errorMessage && <p className="error">{errorMessage}</p>}
    </div>
  );
}

export default Login;