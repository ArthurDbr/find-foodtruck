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

## Deploy a free demo (Render)

The `Dockerfile` builds the React app and serves it from the Python API, so the whole app is **one** service.

1. Sign up at [render.com](https://render.com) with your GitHub account (no credit card needed for the free plan).
2. **New → Blueprint**, pick this repository and the branch to deploy. Render reads `render.yaml`.
3. When asked for `DATABASE_URL`, leave it empty (or see below), then **Apply**.
4. After the build (~3–5 min) the app is live at `https://find-foodtruck-xxxx.onrender.com`, with demo trucks loaded.

Free plan limits: the service sleeps after 15 min without visits, so the first visit after that takes about a minute to wake up.

**Keep data across restarts (optional, free):** without a database URL the app uses SQLite, which is **wiped on every restart/redeploy** (demo trucks are re-added automatically). To keep owners' trucks, create a free project on [neon.tech](https://neon.tech), copy its connection string (`postgresql://...`) and set it as `DATABASE_URL` in the Render service's *Environment* tab.

Run the production image locally: `docker build -t foodtruck . && docker run -p 8000:8000 -e SEED_DEMO=1 foodtruck`

## Configuration (backend env vars)

| Variable | Default | |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./foodtruck.db` | SQLite or PostgreSQL (`postgresql://...` URLs work as-is) |
| `SECRET_KEY` | `dev-secret-change-me` | **Change in production** — signs login tokens |
| `TOKEN_EXPIRE_HOURS` | `168` | |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated |
| `SEED_DEMO` | `0` | `1` = add demo trucks on startup if the database is empty |
| `FRONTEND_DIST` | `../frontend/dist` | Built React app served at `/` when present |
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
