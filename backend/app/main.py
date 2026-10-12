from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import seed
from .config import CORS_ORIGINS, FRONTEND_DIST, SEED_DEMO
from .db import Base, engine
from .routers import auth, geocode, stops, trucks


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    if SEED_DEMO:
        seed.main()
    yield


app = FastAPI(title="Find Foodtruck API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(trucks.router)
app.include_router(stops.router)
app.include_router(geocode.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        if path.startswith("api/"):
            raise HTTPException(404)
        file = (FRONTEND_DIST / path).resolve()
        if path and file.is_file() and file.is_relative_to(FRONTEND_DIST.resolve()):
            return FileResponse(file)
        return FileResponse(FRONTEND_DIST / "index.html")
