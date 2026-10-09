import { useEffect, useState } from "react";
import { api, getToken, setToken } from "./api";
import FindView from "./components/FindView";
import OwnerView from "./components/OwnerView";

export default function App() {
  const [tab, setTab] = useState("find");
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (getToken()) api.me().then(setUser).catch(() => setToken(null));
  }, []);

  const onAuth = ({ access_token, user }) => {
    setToken(access_token);
    setUser(user);
  };
  const logout = () => {
    setToken(null);
    setUser(null);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🚚 Find Foodtruck</h1>
        <nav>
          <button className={tab === "find" ? "active" : ""} onClick={() => setTab("find")}>
            Find trucks
          </button>
          <button className={tab === "owner" ? "active" : ""} onClick={() => setTab("owner")}>
            My food truck
          </button>
        </nav>
        <div className="user">
          {user ? (
            <>
              <span>{user.email}</span>
              <button className="link" onClick={logout}>Log out</button>
            </>
          ) : null}
        </div>
      </header>
      <main className="main">
        {tab === "find" ? <FindView /> : <OwnerView user={user} onAuth={onAuth} />}
      </main>
    </div>
  );
}
