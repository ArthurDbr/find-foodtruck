"""Thin proxy over OpenStreetMap Nominatim so the browser never calls it directly."""

import httpx
from fastapi import APIRouter, HTTPException, Query, status

from ..config import NOMINATIM_URL, NOMINATIM_USER_AGENT
from ..schemas import GeocodeResult

router = APIRouter(prefix="/api/geocode", tags=["geocode"])


async def _nominatim(path: str, params: dict) -> list | dict:
    params = {**params, "format": "jsonv2"}
    try:
        async with httpx.AsyncClient(timeout=10, headers={"User-Agent": NOMINATIM_USER_AGENT}) as client:
            resp = await client.get(f"{NOMINATIM_URL}/{path}", params=params)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Geocoding service unavailable") from exc


@router.get("", response_model=list[GeocodeResult])
async def geocode(q: str = Query(min_length=3, max_length=255), limit: int = Query(5, ge=1, le=10)):
    data = await _nominatim("search", {"q": q, "limit": limit})
    return [
        GeocodeResult(display_name=r["display_name"], latitude=float(r["lat"]), longitude=float(r["lon"]))
        for r in data
    ]


@router.get("/reverse", response_model=GeocodeResult | None)
async def reverse_geocode(lat: float = Query(ge=-90, le=90), lng: float = Query(ge=-180, le=180)):
    data = await _nominatim("reverse", {"lat": lat, "lon": lng})
    if not data or "error" in data:
        return None
    return GeocodeResult(display_name=data["display_name"], latitude=float(data["lat"]), longitude=float(data["lon"]))
