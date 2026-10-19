from datetime import UTC, datetime

from fastapi.testclient import TestClient


def _seed_operations(client: TestClient) -> None:
    device = client.post(
        "/api/v1/devices",
        json={
            "asset_code": "DEMO-REPORT-001",
            "name": "输注设备",
            "category": "therapy",
            "department": "demo-ward",
            "status": "maintenance",
        },
    ).json()
    response = client.post(
        "/api/v1/maintenance-records",
        json={
            "device_id": device["id"],
            "record_type": "fault",
            "severity": "high",
            "description": "演示故障记录",
            "action_taken": "完成检查并记录处理过程",
            "occurred_at": datetime(2026, 10, 15, tzinfo=UTC).isoformat(),
        },
    )
    assert response.status_code == 201


def test_generate_and_fetch_markdown_report(client: TestClient) -> None:
    _seed_operations(client)

    created = client.post(
        "/api/v1/reports",
        json={
            "report_type": "weekly",
            "period_start": "2026-10-12",
            "period_end": "2026-10-18",
            "format": "markdown",
        },
    )

    assert created.status_code == 202
    task = created.json()
    assert task["kind"] == "hospital_report"
    assert task["status"] == "succeeded"
    assert task["progress"] == 100

    fetched = client.get(f"/api/v1/reports/{task['task_id']}")
    assert fetched.status_code == 200
    payload = fetched.json()
    assert payload["report_type"] == "weekly"
    assert payload["statistics"]["maintenance_total"] == 1
    assert "# 医疗设备运维周报" in payload["content"]
    assert "DEMO-REPORT-001" not in payload["content"]

    downloaded = client.get(f"/api/v1/reports/{task['task_id']}/download")
    assert downloaded.status_code == 200
    assert downloaded.headers["content-type"].startswith("text/markdown")
    assert "医疗设备运维周报" in downloaded.text


def test_report_request_reuses_completed_result(client: TestClient) -> None:
    request = {
        "report_type": "monthly",
        "period_start": "2026-10-01",
        "period_end": "2026-10-31",
        "format": "markdown",
    }

    first = client.post("/api/v1/reports", json=request)
    second = client.post("/api/v1/reports", json=request)

    assert first.status_code == 202
    assert second.status_code == 202
    assert first.json()["task_id"] == second.json()["task_id"]
    assert second.json()["reused"] is True


def test_report_rejects_invalid_period(client: TestClient) -> None:
    response = client.post(
        "/api/v1/reports",
        json={
            "report_type": "custom",
            "period_start": "2026-10-18",
            "period_end": "2026-10-12",
            "format": "markdown",
        },
    )

    assert response.status_code == 422
