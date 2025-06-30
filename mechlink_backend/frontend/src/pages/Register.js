import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Register.css";

function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phone, setPhone] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
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
  
      const data = await response.json(); // ← Parse response data
  
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
          navigate("/dashboard"); // ← Go directly to dashboard
        } else {
          // If auto-login fails, go to login page
          alert("Account created! Please login.");
          navigate("/login");
        }
      } else {
        alert(data.detail || "Registration failed");
      }
    } catch (error) {
      alert("Error connecting to server");
    }
  };

  return (
    <div className="login-container">
      <h2>Register</h2>
      <form className="login-form" onSubmit={handleRegister}>
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
          placeholder="Phone"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
        />
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
        <button type="submit">Register</button>
        <p style={{ marginTop: "10px" }}>
          Already have an account?{" "}
          <span onClick={() => navigate("/")} style={{ cursor: "pointer", color: "#0077cc" }}>
            Login
          </span>
        </p>
      </form>
    </div>
  );
}

export default Register;
