from uuid import UUID


def create_device(client, asset_code="DEMO-0001", status="active"):
    response = client.post(
        "/api/v1/devices",
        json={
            "asset_code": asset_code,
            "name": "Infusion Pump",
            "category": "infusion",
            "department": "Demo Ward",
            "manufacturer": "Demo Manufacturer",
            "model": "DP-100",
            "status": status,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_device_crud_pagination_and_filtering(client):
    first = create_device(client)
    create_device(client, "DEMO-0002", "maintenance")

    UUID(first["id"])
    page = client.get("/api/v1/devices", params={"status": "maintenance"})
    assert page.status_code == 200
    assert page.json()["total"] == 1
    assert page.json()["items"][0]["asset_code"] == "DEMO-0002"

    detail = client.get(f"/api/v1/devices/{first['id']}")
    assert detail.status_code == 200
    assert detail.json()["name"] == "Infusion Pump"

    update = client.patch(
        f"/api/v1/devices/{first['id']}",
        json={"status": "maintenance", "department": "Demo Engineering"},
    )
    assert update.status_code == 200
    assert update.json()["department"] == "Demo Engineering"


def test_duplicate_asset_code_returns_conflict(client):
    create_device(client)
    response = client.post(
        "/api/v1/devices",
        json={
            "asset_code": "DEMO-0001",
            "name": "Second Device",
            "category": "monitor",
            "department": "Demo Ward",
        },
    )

    assert response.status_code == 409
    body = response.json()
    assert body["code"] == "device_asset_code_conflict"
    UUID(body["request_id"])


def test_device_statistics(client):
    create_device(client, "DEMO-0001", "active")
    create_device(client, "DEMO-0002", "maintenance")

    response = client.get("/api/v1/devices/statistics")

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert response.json()["by_status"] == {"active": 1, "maintenance": 1}
