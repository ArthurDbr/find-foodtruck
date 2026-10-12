import os
import re
from pathlib import Path

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./foodtruck.db")
# Hosted Postgres providers (Neon, Render...) hand out postgres:// URLs; use the psycopg 3 driver.
DATABASE_URL = re.sub(r"^postgres(ql)?://", "postgresql+psycopg://", DATABASE_URL)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
TOKEN_EXPIRE_HOURS = int(os.getenv("TOKEN_EXPIRE_HOURS", "168"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
NOMINATIM_URL = os.getenv("NOMINATIM_URL", "https://nominatim.openstreetmap.org")
NOMINATIM_USER_AGENT = os.getenv("NOMINATIM_USER_AGENT", "find-foodtruck/0.1")
# Built React app (frontend/dist). When present, the API also serves the website.
FRONTEND_DIST = Path(os.getenv("FRONTEND_DIST", Path(__file__).resolve().parents[2] / "frontend" / "dist"))
# Insert the demo trucks on startup when the database is empty.
SEED_DEMO = os.getenv("SEED_DEMO", "0") == "1"
