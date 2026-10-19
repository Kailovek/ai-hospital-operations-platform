from io import BytesIO

from openpyxl import Workbook


def test_csv_import_cleans_rejects_and_deduplicates(client):
    content = (
        b"asset_code,name,category,department,status\n"
        b" DEMO-CSV-1 ,Infusion Pump,infusion,Demo Ward,ACTIVE\n"
        b"DEMO-CSV-1,Duplicate,infusion,Demo Ward,active\n"
        b"DEMO-CSV-2,,monitor,Demo ICU,active\n"
    )

    response = client.post(
        "/api/v1/imports/devices",
        files={"file": ("devices.csv", content, "text/csv")},
    )

    assert response.status_code == 200
    assert response.json() == {
        "received": 3,
        "inserted": 1,
        "updated": 0,
        "rejected": 1,
        "duplicates": 1,
        "errors": ["row 4: name is required"],
    }
    page = client.get("/api/v1/devices").json()
    assert page["total"] == 1
    assert page["items"][0]["asset_code"] == "DEMO-CSV-1"


def test_json_import_updates_existing_device(client):
    client.post(
        "/api/v1/devices",
        json={
            "asset_code": "DEMO-JSON-1",
            "name": "Original",
            "category": "monitor",
            "department": "Demo Ward",
        },
    )
    payload = b"""[{"assetCode":"DEMO-JSON-1","deviceName":"Updated Monitor",
                    "category":"monitor","department":"Demo ICU","status":"maintenance"}]"""

    response = client.post(
        "/api/v1/imports/devices",
        files={"file": ("devices.json", payload, "application/json")},
    )

    assert response.status_code == 200
    assert response.json()["updated"] == 1
    item = client.get("/api/v1/devices").json()["items"][0]
    assert item["name"] == "Updated Monitor"
    assert item["status"] == "maintenance"


def test_excel_import_accepts_standard_columns(client):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["asset_code", "name", "category", "department", "manufacturer"])
    sheet.append(["DEMO-XLSX-1", "Ultrasound", "imaging", "Demo Imaging", "Demo Maker"])
    buffer = BytesIO()
    workbook.save(buffer)

    response = client.post(
        "/api/v1/imports/devices",
        files={
            "file": (
                "devices.xlsx",
                buffer.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["inserted"] == 1


def test_import_rejects_unsupported_file(client):
    response = client.post(
        "/api/v1/imports/devices",
        files={"file": ("devices.txt", b"not supported", "text/plain")},
    )

    assert response.status_code == 415
    assert response.json()["code"] == "unsupported_import_format"
