# 🚚 Find Foodtruck

A map to find where food trucks are on each day of the week. Food trucks move around (especially on weekends), so each truck publishes a **weekly schedule of locations**.

- **Visitors** pick a day (today is selected by default), search by name / cuisine / place, and optionally filter by distance from their position ("Near me").
- **Owners** create an account, add their truck(s), and add locations per day — either by **clicking on the map** (the pin is draggable and the address is filled automatically) or by **searching an address**.

| Part | Stack |
|------|-------|
| Frontend | React 19 + Vite, Leaflet / react-leaflet, OpenStreetMap tiles |
| Backend | Python, FastAPI, SQLAlchemy (SQLite by default), JWT auth |
| Geocoding | OpenStreetMap Nominatim, proxied by the backend |

## Getting started

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m app.seed               # optional: demo trucks in Paris (login demo@foodtruck.dev / demo1234)
uvicorn app.main:app --reload    # http://localhost:8000, API docs at /docs
```

Run tests: `pytest`

### Frontend

```bash
cd frontend
npm install
npm run dev                      # http://localhost:5173 (proxies /api to :8000)
```

## Configuration (backend env vars)

| Variable | Default | |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./foodtruck.db` | Any SQLAlchemy URL (e.g. PostgreSQL) |
| `SECRET_KEY` | `dev-secret-change-me` | **Change in production** — signs login tokens |
| `TOKEN_EXPIRE_HOURS` | `168` | |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated |
| `NOMINATIM_URL` | `https://nominatim.openstreetmap.org` | Public Nominatim is rate-limited (1 req/s); self-host or use a provider for production |

## API overview

| Method | Path | Auth | |
|---|---|---|---|
| POST | `/api/auth/register`, `/api/auth/login` | – | Returns a bearer token |
| GET | `/api/stops?day=0-6&q=&lat=&lng=&radius_km=` | – | Search locations (0 = Monday … 6 = Sunday) |
| GET | `/api/trucks`, `/api/trucks/{id}` | – | Trucks with their weekly stops |
| GET | `/api/trucks/mine` | ✔ | |
| POST/PUT/DELETE | `/api/trucks[/{id}]` | ✔ owner | |
| POST/PUT/DELETE | `/api/trucks/{id}/stops[/{stop_id}]` | ✔ owner | |
| GET | `/api/geocode?q=`, `/api/geocode/reverse?lat=&lng=` | – | Address ⇄ coordinates |
