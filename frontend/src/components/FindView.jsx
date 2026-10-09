import { useEffect, useRef, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import { api, DAYS, todayIndex } from "../api";
import { truckIcon } from "../leafletIcons";
import DayPicker from "./DayPicker";

const DEFAULT_CENTER = [48.8566, 2.3522];

function FlyTo({ target }) {
  const map = useMap();
  useEffect(() => {
    if (target) map.flyTo(target, Math.max(map.getZoom(), 15));
  }, [target, map]);
  return null;
}

function FitBounds({ stops }) {
  const map = useMap();
  useEffect(() => {
    if (stops.length) map.fitBounds(stops.map((s) => [s.latitude, s.longitude]), { padding: [40, 40], maxZoom: 15 });
  }, [stops, map]);
  return null;
}

export default function FindView() {
  const [day, setDay] = useState(todayIndex());
  const [query, setQuery] = useState("");
  const [debounced, setDebounced] = useState("");
  const [me, setMe] = useState(null);
  const [radius, setRadius] = useState("");
  const [stops, setStops] = useState([]);
  const [error, setError] = useState("");
  const [focus, setFocus] = useState(null);
  const markerRefs = useRef({});

  useEffect(() => {
    const t = setTimeout(() => setDebounced(query), 300);
    return () => clearTimeout(t);
  }, [query]);

  useEffect(() => {
    const params = { day: day ?? undefined, q: debounced };
    if (me) Object.assign(params, { lat: me[0], lng: me[1], radius_km: radius || undefined });
    api
      .searchStops(params)
      .then((data) => {
        setStops(data);
        setError("");
      })
      .catch((e) => setError(e.message));
  }, [day, debounced, me, radius]);

  const locateMe = () => {
    if (!navigator.geolocation) return setError("Geolocation not supported by your browser");
    navigator.geolocation.getCurrentPosition(
      (pos) => setMe([pos.coords.latitude, pos.coords.longitude]),
      () => setError("Could not get your location")
    );
  };

  const select = (s) => {
    setFocus([s.latitude, s.longitude]);
    markerRefs.current[s.id]?.openPopup();
  };

  return (
    <div className="split">
      <aside className="sidebar">
        <h2>Where are the trucks{day === null ? "?" : ` on ${DAYS[day]}?`}</h2>
        <DayPicker value={day} onChange={setDay} allowAll />
        <input
          className="search"
          placeholder="Search by name, cuisine or place…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <div className="row">
          <button onClick={locateMe}>📍 Near me</button>
          {me && (
            <>
              <select value={radius} onChange={(e) => setRadius(e.target.value)}>
                <option value="">Any distance</option>
                <option value="2">≤ 2 km</option>
                <option value="5">≤ 5 km</option>
                <option value="10">≤ 10 km</option>
                <option value="25">≤ 25 km</option>
              </select>
              <button className="link" onClick={() => { setMe(null); setRadius(""); }}>clear</button>
            </>
          )}
        </div>
        {error && <p className="error">{error}</p>}
        <ul className="results">
          {stops.length === 0 && <li className="empty">No food truck found for this search.</li>}
          {stops.map((s) => (
            <li key={s.id} onClick={() => select(s)}>
              <strong>{s.truck.name}</strong>
              {s.truck.cuisine && <span className="tag">{s.truck.cuisine}</span>}
              <div className="muted">
                {day === null && `${DAYS[s.day_of_week]} · `}
                {s.start_time}–{s.end_time}
                {s.distance_km != null && ` · ${s.distance_km} km`}
              </div>
              <div className="muted small">{s.address}</div>
            </li>
          ))}
        </ul>
      </aside>
      <MapContainer center={DEFAULT_CENTER} zoom={12} className="map">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FitBounds stops={stops} />
        <FlyTo target={focus} />
        {me && (
          <Marker position={me}>
            <Popup>You are here</Popup>
          </Marker>
        )}
        {stops.map((s) => (
          <Marker
            key={s.id}
            position={[s.latitude, s.longitude]}
            icon={truckIcon}
            ref={(r) => (markerRefs.current[s.id] = r)}
          >
            <Popup>
              <strong>{s.truck.name}</strong>
              {s.truck.cuisine && <> · {s.truck.cuisine}</>}
              <br />
              {DAYS[s.day_of_week]} {s.start_time}–{s.end_time}
              <br />
              {s.address}
              {s.note && <><br /><em>{s.note}</em></>}
              {s.truck.description && <p>{s.truck.description}</p>}
              <a
                href={`https://www.openstreetmap.org/directions?to=${s.latitude},${s.longitude}`}
                target="_blank"
                rel="noreferrer"
              >
                Directions
              </a>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
