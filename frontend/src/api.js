const TOKEN_KEY = "ft_token";

export const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

// JS getDay(): 0 = Sunday. Backend: 0 = Monday.
export const todayIndex = () => (new Date().getDay() + 6) % 7;

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (t) => (t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY));

async function request(path, { method = "GET", body, params } = {}) {
  const url = new URL(path, window.location.origin);
  Object.entries(params || {}).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, v);
  });
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const resp = await fetch(url, { method, headers, body: body ? JSON.stringify(body) : undefined });
  if (resp.status === 204) return null;
  const data = await resp.json().catch(() => null);
  if (!resp.ok) {
    const detail = data?.detail;
    const msg = Array.isArray(detail) ? detail.map((d) => d.msg).join(", ") : detail || resp.statusText;
    throw new Error(msg);
  }
  return data;
}

export const api = {
  register: (email, password) => request("/api/auth/register", { method: "POST", body: { email, password } }),
  login: (email, password) => request("/api/auth/login", { method: "POST", body: { email, password } }),
  me: () => request("/api/auth/me"),

  searchStops: (params) => request("/api/stops", { params }),

  myTrucks: () => request("/api/trucks/mine"),
  createTruck: (body) => request("/api/trucks", { method: "POST", body }),
  updateTruck: (id, body) => request(`/api/trucks/${id}`, { method: "PUT", body }),
  deleteTruck: (id) => request(`/api/trucks/${id}`, { method: "DELETE" }),
  addStop: (truckId, body) => request(`/api/trucks/${truckId}/stops`, { method: "POST", body }),
  updateStop: (truckId, stopId, body) => request(`/api/trucks/${truckId}/stops/${stopId}`, { method: "PUT", body }),
  deleteStop: (truckId, stopId) => request(`/api/trucks/${truckId}/stops/${stopId}`, { method: "DELETE" }),

  geocode: (q) => request("/api/geocode", { params: { q } }),
  reverseGeocode: (lat, lng) => request("/api/geocode/reverse", { params: { lat, lng } }),
};
