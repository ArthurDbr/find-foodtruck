import { useState } from "react";
import { api } from "../api";

export default function AuthForm({ onAuth }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      onAuth(await (mode === "login" ? api.login : api.register)(email, password));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="card auth" onSubmit={submit}>
      <h2>{mode === "login" ? "Log in" : "Create an owner account"}</h2>
      <p className="muted">Food truck owners log in to publish where their truck will be each day.</p>
      <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      <input
        type="password"
        placeholder="Password (min. 8 characters)"
        value={password}
        minLength={8}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      {error && <p className="error">{error}</p>}
      <button className="primary" disabled={busy}>
        {mode === "login" ? "Log in" : "Sign up"}
      </button>
      <button type="button" className="link" onClick={() => setMode(mode === "login" ? "register" : "login")}>
        {mode === "login" ? "No account yet? Sign up" : "Already have an account? Log in"}
      </button>
    </form>
  );
}
