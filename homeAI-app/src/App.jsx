import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
// import ListingsChat from "./components/PreferenceListingsChat";
import { useState } from "react";
import Navbar from "./components/Navbar";
import LoginSignup from "./components/LoginSIgnup";
import PreferenceListingsChat from "./components/PreferenceListingsChat";

export default function App() {
  const [user, setUser] = useState(null)

  return (
    <Router>
      {user && <Navbar username={user.username} onLogout={() => setUser(null)} />}

      <Routes>
        <Route path="/" element={!user ? <LoginSignup onAuth={setUser} /> : <></>} />
        <Route path="/listings" element={user ? <PreferenceListingsChat /> : <></>} />
      </Routes>
    </Router>
  )
}
