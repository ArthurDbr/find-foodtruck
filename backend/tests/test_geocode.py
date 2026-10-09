import httpx
import pytest

from app.routers import geocode


@pytest.fixture
def fake_nominatim(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/search"):
            return httpx.Response(200, json=[{"display_name": "Eiffel Tower, Paris", "lat": "48.8584", "lon": "2.2945"}])
        return httpx.Response(200, json={"display_name": "Some street, Paris", "lat": "48.85", "lon": "2.35"})

    real = httpx.AsyncClient
    monkeypatch.setattr(geocode.httpx, "AsyncClient", lambda **kw: real(transport=httpx.MockTransport(handler), **kw))


def test_geocode(client, fake_nominatim):
    res = client.get("/api/geocode", params={"q": "tour eiffel"}).json()
    assert res == [{"display_name": "Eiffel Tower, Paris", "latitude": 48.8584, "longitude": 2.2945}]


def test_reverse_geocode(client, fake_nominatim):
    res = client.get("/api/geocode/reverse", params={"lat": 48.85, "lng": 2.35}).json()
    assert res["display_name"] == "Some street, Paris"
