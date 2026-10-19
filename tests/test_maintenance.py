def test_maintenance_record_lifecycle(client):
    device = client.post(
        "/api/v1/devices",
        json={
            "asset_code": "DEMO-0100",
            "name": "Patient Monitor",
            "category": "monitor",
            "department": "Demo ICU",
        },
    ).json()

    created = client.post(
        "/api/v1/maintenance-records",
        json={
            "device_id": device["id"],
            "record_type": "fault",
            "severity": "medium",
            "description": "Intermittent display warning in demonstration data",
            "action_taken": "Connector inspection scheduled",
            "occurred_at": "2026-10-17T08:00:00Z",
        },
    )
    assert created.status_code == 201

    page = client.get("/api/v1/maintenance-records", params={"device_id": device["id"]})
    assert page.status_code == 200
    assert page.json()["total"] == 1
    assert page.json()["items"][0]["severity"] == "medium"

    stats = client.get("/api/v1/maintenance-records/statistics")
    assert stats.status_code == 200
    assert stats.json()["by_type"] == {"fault": 1}


def test_maintenance_rejects_unknown_device(client):
    response = client.post(
        "/api/v1/maintenance-records",
        json={
            "device_id": "d56f5d31-3f87-45d7-8b85-e2b78bce7f82",
            "record_type": "inspection",
            "severity": "low",
            "description": "Demo record",
            "occurred_at": "2026-10-17T08:00:00Z",
        },
    )

    assert response.status_code == 404
    assert response.json()["code"] == "device_not_found"
