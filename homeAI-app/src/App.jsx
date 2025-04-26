import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
// import ListingsChat from "./components/PreferenceListingsChat";
import { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import LoginSignup from "./components/LoginSIgnup";
import PreferenceListingsChat from "./components/PreferenceListingsChat";
import PreferencesWizard from "./components/PreferencesWizard";

function App() {
  // try to load saved user once on startup
  const [user, setUser] = useState(() => {
    const json = localStorage.getItem('user');
    return json ? JSON.parse(json) : null;
  });

  // whenever user changes, mirror to localStorage
  useEffect(() => {
    if (user) {
      localStorage.setItem('user', JSON.stringify(user));
    } else {
      localStorage.removeItem('user');
    }
  }, [user]);

  const handleLogout = () => {
    setUser(null);
  };

  return (
    <Router>
      {user && <Navbar username={user.first_name} onLogout={handleLogout} />}
      <Routes>
        <Route
          path="/"
          element={
            !user ? (
              <LoginSignup onAuth={setUser} />
            ) : (
              <></>
            )
          }
        />
        <Route
          path="/listings"
          element={<PreferenceListingsChat />}
        />
        <Route
          path="/preferences"
          element={user ? <PreferencesWizard /> : <></>}
        />
      </Routes>
    </Router>
  );
}

export default App;
