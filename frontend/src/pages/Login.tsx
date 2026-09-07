import { FormEvent, useState } from "react";
import { api, setToken } from "../services/api";

export default function Login({ onLogin }: { onLogin: () => void }) {
  const [username, setUsername] = useState("admin"); const [password, setPassword] = useState(""); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent) { event.preventDefault(); setBusy(true); setError(""); try { const result = await api.login(username, password); setToken(result.access_token); onLogin(); } catch (e) { setError(e instanceof Error ? e.message : "Login failed"); } finally { setBusy(false); } }
  return <div className="login"><form onSubmit={submit} className="login-card"><span className="eyebrow">JOBFLOW</span><h1>Operations Console</h1><p>Sign in to monitor and control background jobs.</p>{error && <div className="alert">{error}</div>}<label>Username<input value={username} onChange={e => setUsername(e.target.value)} autoComplete="username"/></label><label>Password<input type="password" value={password} onChange={e => setPassword(e.target.value)} autoComplete="current-password" required/></label><button disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button></form></div>;
}
