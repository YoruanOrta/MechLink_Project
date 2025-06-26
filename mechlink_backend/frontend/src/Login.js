import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./styles/Login.css";

function Login() {
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const newFormData = {
      ...formData,
      [e.target.name]: e.target.value,
    };
    console.log("Form data updated:", newFormData);
    setFormData(newFormData);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage("");
    setIsLoading(true);

    console.log("Submitting form with data:", formData);

    // Check if fields are empty
    if (!formData.email || !formData.password) {
      setErrorMessage("Please fill in both email and password");
      setIsLoading(false);
      return;
    }

    try {
      const requestBody = JSON.stringify(formData);
      console.log("Request body:", requestBody);

      // Use the login-json endpoint that accepts JSON
      const response = await fetch("http://localhost:8000/api/v1/auth/login-json", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: requestBody,
      });

      const data = await response.json();
      console.log("Response status:", response.status);
      console.log("Response data:", data);

      if (!response.ok) {
        // Handle different types of error responses
        if (data.detail) {
          // Simple string error
          if (typeof data.detail === 'string') {
            setErrorMessage(data.detail);
          } else if (Array.isArray(data.detail)) {
            // Validation errors array
            const errorMessages = data.detail.map(err => 
              `${err.loc ? err.loc.join('.') : 'Error'}: ${err.msg}`
            ).join(', ');
            setErrorMessage(errorMessages);
          } else {
            setErrorMessage("Login failed");
          }
        } else if (data.message) {
          setErrorMessage(data.message);
        } else {
          setErrorMessage(`Login failed (${response.status})`);
        }
        return;
      }

      // Success - store tokens and navigate
      if (data.access_token) {
        console.log("Login successful!");
        localStorage.setItem("token", data.access_token);
        
        if (data.user) {
          localStorage.setItem("user_id", data.user.id);
          localStorage.setItem("user_email", data.user.email);
          if (data.user.role) {
            localStorage.setItem("user_role", data.user.role);
          }
        }
        
        navigate("/dashboard");
      } else {
        setErrorMessage("Invalid response from server");
      }
    } catch (err) {
      console.error("Login error:", err);
      setErrorMessage("Network error. Please try again later.");
    } finally {
      setIsLoading(false);
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
          disabled={isLoading}
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          required
          value={formData.password}
          onChange={handleChange}
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Logging in..." : "Submit"}
        </button>
      </form>
      {errorMessage && <p className="error">{errorMessage}</p>}
      
      {/* Debug info */}
      <div style={{marginTop: '20px', fontSize: '12px', color: '#666'}}>
        <p>Debug - Email: "{formData.email}"</p>
        <p>Debug - Password: "{formData.password}"</p>
      </div>
    </div>
  );
}

export default Login;
