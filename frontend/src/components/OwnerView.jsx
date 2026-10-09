import { useCallback, useEffect, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap, useMapEvents } from "react-leaflet";
import { api, DAYS } from "../api";
import { truckIcon } from "../leafletIcons";
import AuthForm from "./AuthForm";
import DayPicker from "./DayPicker";

const DEFAULT_CENTER = [48.8566, 2.3522];
const EMPTY_STOP = { day_of_week: 5, start_time: "11:30", end_time: "14:30", latitude: null, longitude: null, address: "", note: "" };

function ClickToPlace({ onPick }) {
  useMapEvents({ click: (e) => onPick(e.latlng.lat, e.latlng.lng) });
  return null;
}

function FlyTo({ target }) {
  const map = useMap();
  useEffect(() => {
    if (target) map.flyTo(target, Math.max(map.getZoom(), 15));
  }, [target, map]);
  return null;
}

function TruckForm({ initial, onSave, onCancel, submitLabel }) {
  const [form, setForm] = useState(initial);
  const [error, setError] = useState("");
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const submit = async (e) => {
    e.preventDefault();
    try {
      await onSave(form);
    } catch (err) {
      setError(err.message);
    }
  };
  return (
    <form className="card" onSubmit={submit}>
      <input placeholder="Truck name" value={form.name} onChange={set("name")} required />
      <input placeholder="Cuisine (e.g. Tacos, Burgers, Vegan)" value={form.cuisine} onChange={set("cuisine")} />
      <textarea placeholder="Short description" value={form.description} onChange={set("description")} rows={2} />
      {error && <p className="error">{error}</p>}
      <div className="row">
        <button className="primary">{submitLabel}</button>
        {onCancel && <button type="button" onClick={onCancel}>Cancel</button>}
      </div>
    </form>
  );
}

export default function OwnerView({ user, onAuth }) {
  const [trucks, setTrucks] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [creating, setCreating] = useState(false);
  const [editingTruck, setEditingTruck] = useState(false);
  const [stop, setStop] = useState(null); // stop being created/edited
  const [addressQuery, setAddressQuery] = useState("");
  const [addressResults, setAddressResults] = useState([]);
  const [focus, setFocus] = useState(null);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    const data = await api.myTrucks();
    setTrucks(data);
    setSelectedId((id) => (data.some((t) => t.id === id) ? id : data[0]?.id ?? null));
    if (!data.length) setCreating(true);
  }, []);

  useEffect(() => {
    if (user) load().catch((e) => setError(e.message));
  }, [user, load]);

  if (!user) return <div className="centered"><AuthForm onAuth={onAuth} /></div>;

  const truck = trucks.find((t) => t.id === selectedId);

  const createTruck = async (body) => {
    const t = await api.createTruck(body);
    setCreating(false);
    setSelectedId(t.id);
    await load();
  };

  const updateTruck = async (body) => {
    await api.updateTruck(truck.id, body);
    setEditingTruck(false);
    await load();
  };

  const deleteTruck = async () => {
    if (!confirm(`Delete "${truck.name}" and all its locations?`)) return;
    await api.deleteTruck(truck.id);
    await load();
  };

  const pickPoint = async (lat, lng) => {
    if (!stop) return;
    setStop((s) => ({ ...s, latitude: lat, longitude: lng }));
    try {
      const r = await api.reverseGeocode(lat, lng);
      if (r) setStop((s) => ({ ...s, address: r.display_name }));
    } catch {
      /* address stays editable by hand */
    }
  };

  const searchAddress = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await api.geocode(addressQuery);
      setAddressResults(res);
      if (!res.length) setError("No address found");
    } catch (err) {
      setError(err.message);
    }
  };

  const chooseAddress = (r) => {
    setStop((s) => ({ ...s, latitude: r.latitude, longitude: r.longitude, address: r.display_name }));
    setFocus([r.latitude, r.longitude]);
    setAddressResults([]);
    setAddressQuery("");
  };

  const saveStop = async (e) => {
    e.preventDefault();
    if (stop.latitude == null) return setError("Pick a point on the map or search an address first");
    const { id, truck_id, ...body } = stop;
    try {
      if (id) await api.updateStop(truck.id, id, body);
      else await api.addStop(truck.id, body);
      setStop(null);
      setError("");
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const deleteStop = async (s) => {
    await api.deleteStop(truck.id, s.id);
    await load();
  };

  const editStop = (s) => {
    setStop({ ...s });
    setFocus([s.latitude, s.longitude]);
  };

  return (
    <div className="split">
      <aside className="sidebar">
        <div className="row spread">
          <h2>My food trucks</h2>
          {!creating && <button onClick={() => setCreating(true)}>+ New truck</button>}
        </div>

        {creating && (
          <TruckForm
            initial={{ name: "", cuisine: "", description: "" }}
            onSave={createTruck}
            onCancel={trucks.length ? () => setCreating(false) : null}
            submitLabel="Create truck"
          />
        )}

        {trucks.length > 1 && (
          <select value={selectedId ?? ""} onChange={(e) => { setSelectedId(Number(e.target.value)); setStop(null); }}>
            {trucks.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
        )}

        {truck && !creating && (
          <>
            {editingTruck ? (
              <TruckForm
                initial={{ name: truck.name, cuisine: truck.cuisine, description: truck.description }}
                onSave={updateTruck}
                onCancel={() => setEditingTruck(false)}
                submitLabel="Save"
              />
            ) : (
              <div className="card">
                <div><strong>{truck.name}</strong> {truck.cuisine && <span className="tag">{truck.cuisine}</span>}</div>
                {truck.description && <p className="muted">{truck.description}</p>}
                <div className="row">
                  <button className="link" onClick={() => setEditingTruck(true)}>Edit</button>
                  <button className="link danger" onClick={deleteTruck}>Delete</button>
                </div>
              </div>
            )}

            <div className="row spread">
              <h3>Weekly locations</h3>
              {!stop && <button onClick={() => setStop({ ...EMPTY_STOP })}>+ Add location</button>}
            </div>

            {stop && (
              <form className="card" onSubmit={saveStop}>
                <strong>{stop.id ? "Edit location" : "New location"}</strong>
                <label>Day</label>
                <DayPicker value={stop.day_of_week} onChange={(d) => setStop({ ...stop, day_of_week: d })} />
                <div className="row">
                  <label>From <input type="time" value={stop.start_time} onChange={(e) => setStop({ ...stop, start_time: e.target.value })} required /></label>
                  <label>To <input type="time" value={stop.end_time} onChange={(e) => setStop({ ...stop, end_time: e.target.value })} required /></label>
                </div>
                <label>Place</label>
                <p className="hint">👉 Click on the map to drop the pin, or search an address:</p>
                <div className="row">
                  <input
                    placeholder="Address…"
                    value={addressQuery}
                    onChange={(e) => setAddressQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && searchAddress(e)}
                  />
                  <button type="button" onClick={searchAddress} disabled={addressQuery.length < 3}>Search</button>
                </div>
                {addressResults.length > 0 && (
                  <ul className="results compact">
                    {addressResults.map((r, i) => (
                      <li key={i} onClick={() => chooseAddress(r)}>{r.display_name}</li>
                    ))}
                  </ul>
                )}
                {stop.latitude != null ? (
                  <input value={stop.address} onChange={(e) => setStop({ ...stop, address: e.target.value })} placeholder="Address label" />
                ) : (
                  <p className="muted small">No place selected yet.</p>
                )}
                <input placeholder="Note (optional, e.g. 'next to the fountain')" value={stop.note} onChange={(e) => setStop({ ...stop, note: e.target.value })} />
                {error && <p className="error">{error}</p>}
                <div className="row">
                  <button className="primary">Save location</button>
                  <button type="button" onClick={() => { setStop(null); setError(""); setAddressResults([]); }}>Cancel</button>
                </div>
              </form>
            )}

            <ul className="results">
              {truck.stops.length === 0 && <li className="empty">No locations yet. Add where your truck will be!</li>}
              {truck.stops.map((s) => (
                <li key={s.id} onClick={() => setFocus([s.latitude, s.longitude])}>
                  <strong>{DAYS[s.day_of_week]}</strong> · {s.start_time}–{s.end_time}
                  <div className="muted small">{s.address || `${s.latitude.toFixed(5)}, ${s.longitude.toFixed(5)}`}</div>
                  <div className="row">
                    <button className="link" onClick={(e) => { e.stopPropagation(); editStop(s); }}>Edit</button>
                    <button className="link danger" onClick={(e) => { e.stopPropagation(); deleteStop(s); }}>Delete</button>
                  </div>
                </li>
              ))}
            </ul>
          </>
        )}
        {error && !stop && <p className="error">{error}</p>}
      </aside>

      <MapContainer center={DEFAULT_CENTER} zoom={12} className={`map ${stop ? "picking" : ""}`}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ClickToPlace onPick={pickPoint} />
        <FlyTo target={focus} />
        {truck?.stops
          .filter((s) => s.id !== stop?.id)
          .map((s) => (
            <Marker key={s.id} position={[s.latitude, s.longitude]} icon={truckIcon} opacity={stop ? 0.5 : 1}>
              <Popup>{DAYS[s.day_of_week]} {s.start_time}–{s.end_time}<br />{s.address}</Popup>
            </Marker>
          ))}
        {stop?.latitude != null && (
          <Marker
            position={[stop.latitude, stop.longitude]}
            draggable
            eventHandlers={{ dragend: (e) => { const p = e.target.getLatLng(); pickPoint(p.lat, p.lng); } }}
          />
        )}
      </MapContainer>
    </div>
  );
}
