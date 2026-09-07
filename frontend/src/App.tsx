import { useState } from "react";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import { clearToken, getToken } from "./services/api";
import "./styles.css";
export default function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(getToken()));
  if (!authenticated) return <Login onLogin={() => setAuthenticated(true)} />;
  return <><Dashboard /><button className="logout" onClick={() => { clearToken(); setAuthenticated(false); }}>Sign out</button></>;
}
