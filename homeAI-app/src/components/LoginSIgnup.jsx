import React, { useState } from "react";
import "./styles.css";
import { useNavigate } from "react-router-dom";
import logo from "../assets/logo.jpg";

// const dummyUsers = {
//   "test@example.com": {
//     username: "testuser",
//     password: "password123",
//     address: {
//       line1: "123 Main St",
//       line2: "",
//       city: "Anytown",
//       state: "CA",
//       zipcode: "12345",
//     },
//     tags: ["Technology"],
//   },
// };

export default function LoginSignup({ onAuth }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({});
  const [error, setError] = useState(null);

  const base_url = "http://localhost:8001/";

  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleLogin = async () => {
    const { email, password } = form;
  
    if (!email || !password) {
      setError("Please enter email and password.");
      return;
    }
  
    try {
      const response = await fetch(base_url+"auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Login failed");
      }
  
      const userData = await response.json();
      console.log("User data:", userData);
      onAuth(userData); 
      navigate("/listings");
    } catch (err) {
      setError(err.message);
    }
  };
  

  const handleSignup = async () => {
    const { firstName, lastName, email, password, confirmPassword } = form;
  
    if (!firstName || !lastName || !email || !password || !confirmPassword) {
      setError("Please fill out all required fields.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
  
    try {
      const response = await fetch(base_url+"auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          first_name: firstName, 
          last_name: lastName, 
          email, 
          password 
        }),
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Signup failed");
      }
  
      alert("Account created successfully! Please log in.");
      setMode("login");
      setForm({});
    } catch (err) {
      setError(err.message);
    }
  };
  

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <div className="logo-header">
          <img
            src={logo}
            alt="HomeAI Logo"
            style={{ height: "40px", objectFit: "contain" }}
          />
          <h1>HomeAI</h1>
        </div>
        <div className="tabs">
          <button
            onClick={() => setMode("login")}
            className={mode === "login" ? "active" : ""}
          >
            Login
          </button>
          <button
            onClick={() => setMode("signup")}
            className={mode === "signup" ? "active" : ""}
          >
            Sign Up
          </button>
        </div>
        {error && <p className="error">{error}</p>}

        {mode === "login" ? (
          <div className="form-group">
            <input name="email" placeholder="Email" onChange={handleChange} />
            <input
              name="password"
              type="password"
              placeholder="Password"
              onChange={handleChange}
            />
            <button onClick={handleLogin}>Login</button>
          </div>
        ) : (
          <div className="form-group">
            <input
              name="firstName"
              placeholder="First Name"
              onChange={handleChange}
            />
            <input
              name="lastName"
              placeholder="Last Name"
              onChange={handleChange}
            />
            <input name="email" placeholder="Email" onChange={handleChange} />
            <input
              name="password"
              type="password"
              placeholder="Password"
              onChange={handleChange}
            />
            <input
              name="confirmPassword"
              type="password"
              placeholder="Confirm Password"
              onChange={handleChange}
            />
            <button onClick={handleSignup}>Sign Up</button>
          </div>
        )}
      </div>
    </div>
  );
}
