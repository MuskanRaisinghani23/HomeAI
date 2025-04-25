import React, { useState } from "react";
import axios from "axios";
import "./styles.css";
import ListingCard from "./ListingCard";

const STATE_CITY_MAP = {
  MA: ["Boston", "Cambridge", "Somerville"],
  CA: ["San Francisco", "Los Angeles", "San Diego"],
  NY: ["New York", "Buffalo", "Rochester"],
};

export default function PreferenceListingsChat() {
  const [state, setState] = useState("MA");
  const [location, setLocation] = useState("Boston");
  const [budget, setBudget] = useState([200, 3000]);
  const [roomType, setRoomType] = useState("Private");
  const [laundryAvailable, setLaundryAvailable] = useState(true);

  const [listings, setListings] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  const handleFetchListings = async () => {
    const params = {
      location,
      min_price: budget[0],
      max_price: budget[1],
      room_type: roomType,
      laundry_availability: laundryAvailable,
    };
    try {
      const res = await axios.get(
        "http://localhost:8001/api/listing/get-listings",
        { params }
      );
      setListings(res.data.data || []);
    } catch (err) {
      alert("Error fetching listings");
    }
  };

  const handleSendChat = async () => {
    if (!chatInput.trim()) return;
    setChatHistory((prev) => [...prev, { role: "user", msg: chatInput }]);
    const userMessage = chatInput;
    setChatInput("");

    try {
      const res = await axios.post(
        "http://localhost:8001/api/listing/search-listings",
        {
          q: userMessage,
          k: 10,
        }
      );

      const results = res.data;
      setListings(results);
      setChatHistory((prev) => [
        ...prev,
        {
          role: "bot",
          msg:
            results.length > 0
              ? `Found ${results.length} listings for "${userMessage}"`
              : `No listings found for "${userMessage}"`,
        },
      ]);
    } catch (err) {
      console.error(err);
      setChatHistory((prev) => [
        ...prev,
        { role: "bot", msg: "Something went wrong." },
      ]);
    }
  };

  return (
    <div className="dashboard-container">
      <div className="left-section">
        <h2>🏡 Preferences</h2>

        <div className="form-grid">
          <div style={{ display: "flex", padding: "10px" }}>
            <div style={{ margin: "10px" }}>
              <label>State</label>
              <select
                value={state}
                onChange={(e) => {
                  setState(e.target.value);
                  setLocation(STATE_CITY_MAP[e.target.value][0]);
                }}
              >
                {Object.keys(STATE_CITY_MAP).map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>
            </div>

            <div style={{ margin: "10px" }}>
              <label>City</label>
              <select
                className="w-full border p-1"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              >
                {STATE_CITY_MAP[state].map((c) => (
                  <option key={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>
          <div style={{ display: "flex", padding: "10px" }}>
            <div style={{ margin: "10px" }}>
              <label>Budget Min</label>
              <input
                type="number"
                className="w-full border p-1"
                value={budget[0]}
                onChange={(e) => setBudget([+e.target.value, budget[1]])}
              />
            </div>

            <div style={{ margin: "10px" }}>
              <label>Budget Max</label>
              <input
                type="number"
                className="w-full border p-1"
                value={budget[1]}
                onChange={(e) => setBudget([budget[0], +e.target.value])}
              />
            </div>
          </div>
          <div>
            <label>Room Type</label>
            <select
              className="w-full border p-1"
              value={roomType}
              onChange={(e) => setRoomType(e.target.value)}
            >
              <option>Private</option>
              <option>Shared</option>
            </select>
          </div>

          <div>
            <label>Laundry Available</label>
            <select
              className="w-full border p-1"
              value={laundryAvailable ? "Yes" : "No"}
              onChange={(e) => setLaundryAvailable(e.target.value === "Yes")}
            >
              <option>Yes</option>
              <option>No</option>
            </select>
          </div>
        </div>

        <button onClick={handleFetchListings}>Get Listings</button>
        {listings? <ListingCard listings={listings} /> : <></>}
      </div>

      {/* Right section: Chatbot */}
      <div className="right-section">
        <h2>💬 Chatbot</h2>
        <div className="chat-history">
          {chatHistory.map((entry, idx) => (
            <div
              key={idx}
              className={entry.role === "user" ? "chat-user" : "chat-bot"}
            >
              {entry.msg}
            </div>
          ))}
        </div>
        <div className="chat-input-row">
          <input
            type="text"
            value={chatInput}
            placeholder="Search for a room..."
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSendChat()}
          />
          <button onClick={handleSendChat}>Send</button>
        </div>
      </div>
    </div>
  );
}
