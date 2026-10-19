import hashlib
import json
from datetime import UTC, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.models import Device, MaintenanceRecord, TaskRecord
from app.modules.reports.schemas import (
    ReportRequest,
    ReportResult,
    ReportStatistics,
    ReportTaskSummary,
)


def _request_key(payload: ReportRequest) -> str:
    serialized = payload.model_dump_json()
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _counts(db: Session, column, *filters) -> dict[str, int]:
    return dict(db.execute(select(column, func.count()).where(*filters).group_by(column)).all())


def _statistics(db: Session, payload: ReportRequest) -> ReportStatistics:
    start = datetime.combine(payload.period_start, time.min, tzinfo=UTC)
    end = datetime.combine(payload.period_end + timedelta(days=1), time.min, tzinfo=UTC)
    period_filters = (
        MaintenanceRecord.occurred_at >= start,
        MaintenanceRecord.occurred_at < end,
    )
    devices_by_status = _counts(db, Device.status)
    maintenance_by_type = _counts(db, MaintenanceRecord.record_type, *period_filters)
    maintenance_by_severity = _counts(db, MaintenanceRecord.severity, *period_filters)
    return ReportStatistics(
        device_total=sum(devices_by_status.values()),
        maintenance_total=sum(maintenance_by_type.values()),
        devices_by_status=devices_by_status,
        maintenance_by_type=maintenance_by_type,
        maintenance_by_severity=maintenance_by_severity,
    )


def _render_markdown(payload: ReportRequest, statistics: ReportStatistics) -> str:
    titles = {
        "weekly": "医疗设备运维周报",
        "monthly": "医疗设备运维月报",
        "custom": "医疗设备运维分析报告",
    }
    status_lines = (
        "\n".join(
            f"- {status}: {count}" for status, count in sorted(statistics.devices_by_status.items())
        )
        or "- 暂无设备数据"
    )
    severity_lines = (
        "\n".join(
            f"- {severity}: {count}"
            for severity, count in sorted(statistics.maintenance_by_severity.items())
        )
        or "- 本周期暂无运维记录"
    )
    return (
        f"# {titles[payload.report_type]}\n\n"
        f"> 统计周期：{payload.period_start} 至 {payload.period_end}\n\n"
        "## 运行概览\n\n"
        f"- 设备总数：{statistics.device_total}\n"
        f"- 周期内运维记录：{statistics.maintenance_total}\n\n"
        "## 设备状态分布\n\n"
        f"{status_lines}\n\n"
        "## 运维事件风险分布\n\n"
        f"{severity_lines}\n\n"
        "## 使用说明\n\n"
        "本报告由演示环境基于结构化运维记录自动汇总，不包含患者信息或真实机构数据。\n"
    )


def create_report(db: Session, payload: ReportRequest) -> ReportTaskSummary:
    cache_key = _request_key(payload)
    existing_tasks = db.scalars(
        select(TaskRecord).where(
            TaskRecord.kind == "hospital_report", TaskRecord.status == "succeeded"
        )
    ).all()
    for existing in existing_tasks:
        result = json.loads(existing.result_json or "{}")
        if result.get("cache_key") == cache_key:
            return ReportTaskSummary(
                task_id=existing.id,
                status=existing.status,
                progress=existing.progress,
                created_at=existing.created_at,
                updated_at=existing.updated_at,
                reused=True,
                error=existing.error,
            )

    statistics = _statistics(db, payload)
    generated_at = datetime.now(UTC)
    result = {
        "cache_key": cache_key,
        "report_type": payload.report_type,
        "period_start": payload.period_start.isoformat(),
        "period_end": payload.period_end.isoformat(),
        "format": payload.format,
        "content": _render_markdown(payload, statistics),
        "statistics": statistics.model_dump(),
        "generated_at": generated_at.isoformat(),
    }
    task = TaskRecord(
        kind="hospital_report",
        status="succeeded",
        progress=100,
        result_json=json.dumps(result, ensure_ascii=False),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return ReportTaskSummary(
        task_id=task.id,
        status=task.status,
        progress=task.progress,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def get_report(db: Session, task_id: str) -> ReportResult:
    task = db.get(TaskRecord, task_id)
    if task is None or task.kind != "hospital_report":
        raise AppError(404, "report_not_found", "Report task was not found")
    if task.status != "succeeded" or not task.result_json:
        raise AppError(409, "report_not_ready", "Report is not ready")
    data = json.loads(task.result_json)
    return ReportResult(
        task_id=task.id,
        report_type=data["report_type"],
        period_start=data["period_start"],
        period_end=data["period_end"],
        format=data["format"],
        content=data["content"],
        statistics=data["statistics"],
        generated_at=data["generated_at"],
        download_url=f"/api/v1/reports/{task.id}/download",
    )
