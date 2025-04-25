import React from "react";
import { Link, useNavigate } from "react-router-dom";
import logo from "../assets/logo.jpg";

export default function Navbar({ username, onLogout }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate("/");
  };

  return (
    <nav
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "0.5rem 2rem",
        backgroundColor: "#f5f5f5",
        borderBottom: "1px solid #ddd",
      }}
    >
      {/* Logo or Brand */}
      <Link to="/listings" style={{ color: "#049bde", fontFamily: "Para" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <img
            src={logo}
            alt="HomeAI Logo"
            style={{ height: "32px", objectFit: "contain" }}
          />
          <h2>HomeAI</h2>
        </div>
      </Link>

      {/* Navigation Links */}
      <div style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
        <Link
          to="/listings"
          style={{ textDecoration: "none", color: "#333", fontWeight: "bold" }}
        >
          Listings
        </Link>
        <Link
          to="/dashboard"
          style={{ textDecoration: "none", color: "#333", fontWeight: "bold" }}
        >
          Analytics
        </Link>

        <span style={{ marginLeft: "1rem" }}>👋 Hi, {username}</span>
        <button
          onClick={handleLogout}
          style={{
            padding: "0.5rem 1rem",
            backgroundColor: "#dc3545",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          Logout
        </button>
      </div>
    </nav>
  );
}
