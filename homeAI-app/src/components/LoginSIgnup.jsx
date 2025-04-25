import React, { useState } from "react";
import "./styles.css";
import { useNavigate } from "react-router-dom";
import logo from "../assets/logo.jpg";

const dummyUsers = {
  "test@example.com": {
    username: "testuser",
    password: "password123",
    address: {
      line1: "123 Main St",
      line2: "",
      city: "Anytown",
      state: "CA",
      zipcode: "12345",
    },
    tags: ["Technology"],
  },
};

export default function LoginSignup({ onAuth }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({});
  const [error, setError] = useState(null);

  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleLogin = () => {
    const { email, password } = form;
    if (dummyUsers[email] && dummyUsers[email].password === password) {
      onAuth({ email, username: dummyUsers[email].username });
      navigate("/listings");
    } else {
      setError("Invalid email or password");
    }
  };

  const handleSignup = () => {
    const {
      username,
      email,
      password,
      confirmPassword,
      line1,
      line2,
      city,
      state,
      zipcode,
      tags,
    } = form;

    if (
      !username ||
      !email ||
      !password ||
      !confirmPassword ||
      !line1 ||
      !city ||
      !state ||
      !zipcode
    ) {
      setError("Please fill out all required fields.");
    } else if (password !== confirmPassword) {
      setError("Passwords do not match");
    } else if (dummyUsers[email]) {
      setError("Email already exists");
    } else {
      dummyUsers[email] = {
        username,
        password,
        address: { line1, line2, city, state, zipcode },
        tags: tags ? tags.split(",") : [],
      };
      alert("Account created successfully! Please log in.");
      setMode("login");
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
              name="username"
              placeholder="Username"
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
            <input
              name="line1"
              placeholder="Address Line 1"
              onChange={handleChange}
            />
            <input
              name="line2"
              placeholder="Address Line 2"
              onChange={handleChange}
            />
            <input name="city" placeholder="City" onChange={handleChange} />
            <input name="state" placeholder="State" onChange={handleChange} />
            <input
              name="zipcode"
              placeholder="Zipcode"
              onChange={handleChange}
            />
            <input
              name="tags"
              placeholder="Tags (comma separated)"
              onChange={handleChange}
            />
            <button onClick={handleSignup}>Sign Up</button>
          </div>
        )}
      </div>
    </div>
  );
}
