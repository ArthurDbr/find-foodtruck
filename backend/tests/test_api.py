from .conftest import register

STOP = {
    "day_of_week": 5,
    "start_time": "18:00",
    "end_time": "22:00",
    "latitude": 48.8566,
    "longitude": 2.3522,
    "address": "Hôtel de Ville, Paris",
}


def _truck(client, headers, name="Taco Loco", cuisine="Mexican"):
    resp = client.post("/api/trucks", json={"name": name, "cuisine": cuisine}, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_register_login_me(client):
    register(client)
    assert client.post("/api/auth/register", json={"email": "owner@example.com", "password": "password123"}).status_code == 409
    bad = client.post("/api/auth/login", json={"email": "owner@example.com", "password": "wrongpass1"})
    assert bad.status_code == 401
    ok = client.post("/api/auth/login", json={"email": "OWNER@example.com", "password": "password123"})
    assert ok.status_code == 200
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {ok.json()['access_token']}"})
    assert me.json()["email"] == "owner@example.com"


def test_create_truck_requires_auth(client):
    assert client.post("/api/trucks", json={"name": "X"}).status_code == 401


def test_stop_validation(client):
    h = register(client)
    truck = _truck(client, h)
    bad = client.post(f"/api/trucks/{truck['id']}/stops", json={**STOP, "end_time": "17:00"}, headers=h)
    assert bad.status_code == 422
    bad = client.post(f"/api/trucks/{truck['id']}/stops", json={**STOP, "day_of_week": 7}, headers=h)
    assert bad.status_code == 422


def test_only_owner_can_edit(client):
    owner = register(client)
    other = register(client, email="other@example.com")
    truck = _truck(client, owner)
    assert client.post(f"/api/trucks/{truck['id']}/stops", json=STOP, headers=other).status_code == 403
    assert client.delete(f"/api/trucks/{truck['id']}", headers=other).status_code == 403
    assert client.post(f"/api/trucks/{truck['id']}/stops", json=STOP, headers=owner).status_code == 201


def test_search_by_day_query_and_distance(client):
    h = register(client)
    tacos = _truck(client, h)
    burgers = _truck(client, h, name="Burger Bros", cuisine="Burgers")
    client.post(f"/api/trucks/{tacos['id']}/stops", json=STOP, headers=h)
    client.post(f"/api/trucks/{tacos['id']}/stops", json={**STOP, "day_of_week": 0}, headers=h)
    # Lyon, ~390 km from Paris
    client.post(
        f"/api/trucks/{burgers['id']}/stops",
        json={**STOP, "latitude": 45.764, "longitude": 4.8357, "address": "Lyon"},
        headers=h,
    )

    saturday = client.get("/api/stops", params={"day": 5}).json()
    assert {s["truck"]["name"] for s in saturday} == {"Taco Loco", "Burger Bros"}
    assert len(client.get("/api/stops", params={"day": 0}).json()) == 1
    assert len(client.get("/api/stops", params={"day": 3}).json()) == 0

    assert [s["truck"]["name"] for s in client.get("/api/stops", params={"q": "burg"}).json()] == ["Burger Bros"]

    near = client.get("/api/stops", params={"day": 5, "lat": 48.85, "lng": 2.35, "radius_km": 50}).json()
    assert [s["truck"]["name"] for s in near] == ["Taco Loco"]
    assert near[0]["distance_km"] < 1


def test_update_and_delete_stop(client):
    h = register(client)
    truck = _truck(client, h)
    stop = client.post(f"/api/trucks/{truck['id']}/stops", json=STOP, headers=h).json()
    upd = client.put(f"/api/trucks/{truck['id']}/stops/{stop['id']}", json={**STOP, "day_of_week": 6}, headers=h)
    assert upd.json()["day_of_week"] == 6
    assert client.delete(f"/api/trucks/{truck['id']}/stops/{stop['id']}", headers=h).status_code == 204
    assert client.get(f"/api/trucks/{truck['id']}").json()["stops"] == []
