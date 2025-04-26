import React, { useEffect, useState } from "react";
import axios from "axios";
import "./PreferenceListingsChat.css";
import ListingCard from "./ListingCard";
import STATE_CITY_MAP from "../STATE_CITY_MAP";
import NearbyPlaces from "./NearbyPlaces";
import { Slider, Typography, Box } from "@mui/material";
import { CircularProgress } from "@mui/material";

export default function PreferenceListingsChat() {
  const stored = localStorage.getItem("user") || "";
  let userEmail = "";
  try {
    userEmail = JSON.parse(stored).email;
  } catch {
    console.warn("No valid user in localStorage");
  }

  // filter state
  const [state, setState] = useState("MA");
  const [location, setLocation] = useState("Boston");
  const [budget, setBudget] = useState([200, 3000]);
  const [roomType, setRoomType] = useState("Private");
  const [laundryAvailable, setLaundryAvailable] = useState(true);

  // listings + chat
  const [listings, setListings] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [nearbyPlaces, setNearbyPlaces] = useState(null);
  const [loading, setLoading] = useState(false);

  const base_url = "http://76.152.120.193:8001/";

  const fetchNearbyPlaces = async () => {
    try {
      setLoading(true);
      const nearbyResponse = await fetch(
        `${base_url}/api/map/nearby/${location}`
      );
      const nearbyData = await nearbyResponse.json();

      setNearbyPlaces(nearbyData.nearby_places);
      setListings([]);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching nearby places:", error);
      setLoading(false);
    }
  };

  const handleFetchListings = async () => {
    const params = {
      location,
      min_price: budget[0],
      max_price: budget[1],
      room_type: roomType,
      laundry_availability: laundryAvailable,
    };
    console.log("Fetching listings with params:", params);
    try {
      const res = await axios.get(base_url + "api/listing/get-listings", {
        params,
      });
      setListings(res.data.data || []);
      setNearbyPlaces(null);
    } catch (err) {
      alert("Error fetching listings");
    }
  };

  useEffect(() => {
    if (!userEmail) return;

    axios
      .get(base_url + "api/listing/user-preferences", {
        params: { user_email: userEmail },
      })
      .then((res) => {
        const p = res.data;
        if (p && Object.keys(p).length) {
          if (p.CITY) setState(p.CITY);
          if (p.LOCATION) setLocation(p.LOCATION);
          if (p.MINPRICE != null && p.MAXPRICE != null)
            setBudget([p.MINPRICE, p.MAXPRICE]);
          if (p.ROOM_TYPE) setRoomType(p.ROOM_TYPE);
          if (p.AMENITIES != null) setLaundryAvailable(p.AMENITIES);
        }
        const initState = p.CITY || state;
        const initLocation = p.LOCATION || location;
        const initBudget =
          p.MINPRICE != null && p.MAXPRICE != null
            ? [p.MINPRICE, p.MAXPRICE]
            : budget;
        const initRoomType = p.ROOM_TYPE || roomType;
        const initLaundry =
          p.AMENITIES != null ? p.AMENITIES : laundryAvailable;

        return axios.get(base_url + "api/listing/get-listings", {
          params: {
            location: initLocation,
            min_price: initBudget[0],
            max_price: initBudget[1],
            room_type: initRoomType,
            laundry_availability: initLaundry,
          },
        });
      })
      .then((res) => {
        setListings(res?.data?.data || []);
      })
      .catch((err) => {
        console.error("Error loading prefs or listings:", err);
      });
  }, []); 

  const handleSendChat = async () => {
    if (!chatInput.trim()) return;
    setChatHistory((prev) => [...prev, { role: "user", msg: chatInput }]);
    const userMessage = chatInput;
    setChatInput("");
    setChatLoading(true);
    try {
      const res = await axios.post(base_url + "api/listing/search-listings", {
        q: userMessage,
        k: 10,
      });
      const results = res.data ? res.data[0].response : [];
      setListings(results);
      setChatHistory((prev) => [
        ...prev,
        {
          role: "bot",
          msg:
            results.length > 0
              ? `Found ${results.length} listings for “${userMessage}”`
              : `No listings found for “${userMessage}”`,
        },
      ]);
    } catch (err) {
      console.error(err);
      setChatHistory((prev) => [
        ...prev,
        { role: "bot", msg: "Something went wrong. Please try again." },
      ]);
    }
    setChatLoading(false);
  };

  const handleChange = (event, newValue) => {
    setBudget(newValue);
  };

  return (
    <div className="dashboard-container">
      <div className="left-section panel">
        <h2>Find your Room</h2>

        <div className="form-grid">
          {/* State */}
          <div>
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

          {/* Location */}
          <div>
            <label>Location</label>
            <select
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            >
              {STATE_CITY_MAP[state].map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </div>

          {/* Room Type */}
          <div>
            <label>Room Type</label>
            <select
              value={roomType}
              onChange={(e) => setRoomType(e.target.value)}
            >
              <option>Private</option>
              <option>Shared</option>
            </select>
          </div>

          {/* Laundry */}
          <div>
            <label>Laundry Available</label>
            <select
              value={laundryAvailable ? "Yes" : "No"}
              onChange={(e) => setLaundryAvailable(e.target.value === "Yes")}
            >
              <option>Yes</option>
              <option>No</option>
            </select>
          </div>
        </div>

        <div>
          <Box sx={{ width: 350, padding: "20px" }}>
            <Typography variant="subtitle1" gutterBottom>
              Budget Range: ${budget[0]} – ${budget[1]}
            </Typography>

            <Slider
              value={budget}
              onChange={handleChange}
              valueLabelDisplay="auto"
              min={0}
              max={5000}
              step={50}
            />
          </Box>
        </div>

        <button
          className="btn btn-primary full-width"
          onClick={handleFetchListings}
        >
          Get Listings
        </button>

        <button
          onClick={fetchNearbyPlaces}
          style={{ marginTop: "10px", width: "100%" }}
        >
          Find Nearby Restaurants, Cafes, Gym, Supermarkets and Park for{" "}
          {location}
        </button>
        {loading && <p>Loading nearby places...</p>}
        {nearbyPlaces ? <NearbyPlaces nearbyPlaces={nearbyPlaces} /> : <></>}

        {listings.length > 0 ? (
          <ListingCard listings={listings} />
        ) : (
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              marginTop: "40px",
            }}
          >
            <CircularProgress />
          </div>
        )}
      </div>

      <div className="right-section panel">
        <h2>💬 Chatbot</h2>
        <div className="chat-history">
          {chatHistory.map((entry, idx) => (
            <div key={idx} className={`chat-bubble ${entry.role}`}>
              {entry.msg}
            </div>
          ))}
        </div>

        <div className="chat-input-row">
          <input
            type="text"
            value={chatInput}
            placeholder="Search for rooms..."
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSendChat()}
          />
          <button
            className="btn btn-send"
            onClick={handleSendChat}
            disabled={!chatLoading}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
