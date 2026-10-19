# API Guide

The interactive contract is available at `http://127.0.0.1:8101/docs` after startup. The portfolio root also maintains a cross-service contract for Java orchestration.

| Area | Endpoint | Purpose |
| --- | --- | --- |
| Runtime | `GET /api/v1/health` | Mode and dependency readiness |
| Devices | `GET/POST /api/v1/devices` | Paged query and registration |
| Devices | `GET/PATCH /api/v1/devices/{id}` | Detail and controlled update |
| Statistics | `GET /api/v1/devices/statistics` | Device status/category aggregation |
| Maintenance | `GET/POST /api/v1/maintenance-records` | Operations and fault records |
| Import | `POST /api/v1/imports/devices` | CSV, JSON, or XLSX clean/batch import |
| Knowledge | `POST /api/v1/knowledge/documents` | Parse, chunk, and index a document |
| Retrieval | `POST /api/v1/knowledge/search` | Hybrid retrieval with citations |
| Analysis | `POST /api/v1/analysis/questions` | Grounded structured question answering |
| Reports | `POST /api/v1/reports` | Generate or reuse an aggregate report |
| Reports | `GET /api/v1/reports/{task_id}` | Read report result |
| Reports | `GET /api/v1/reports/{task_id}/download` | Download Markdown export |

## Request example

```powershell
$Body = @{
    question = "设备出现重复告警时应先检查什么？"
    top_k = 3
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8101/api/v1/analysis/questions" `
    -ContentType "application/json" `
    -Body $Body
```

Responses use UUID request IDs. Validation and domain failures share the fields `code`, `message`, `request_id`, and `details`.
