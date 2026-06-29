from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic import Field

from app.core.enums import ESGMetricCategory
from app.core.enums import ESGReportStatus
from app.core.enums import ESGReportType


class ESGReportGenerateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str | None = None
    report_type: ESGReportType = ESGReportType.ORGANIZATION
    campaign_id: str | None = None
    organization_id: str | None = None
    period_start: datetime | None = None
    period_end: datetime | None = None


class ESGReportMetricResponse(BaseModel):
    id: str
    report_id: str
    category: ESGMetricCategory
    metric_key: str
    metric_name: str
    value_number: float | None
    value_text: str | None
    unit: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class ESGReportResponse(BaseModel):
    id: str
    organization_id: str
    campaign_id: str | None
    created_by: str
    title: str
    description: str | None
    report_type: ESGReportType
    status: ESGReportStatus
    period_start: datetime | None
    period_end: datetime | None
    summary: dict[str, Any] | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ESGReportDetailResponse(ESGReportResponse):
    metrics: list[ESGReportMetricResponse]


class ESGReportListResponse(BaseModel):
    items: list[ESGReportResponse]
    total: int
    limit: int
    offset: int


class ESGSummaryResponse(BaseModel):
    organization_id: str | None = None
    campaign_id: str | None = None
    scope: str
    environmental: dict[str, Any]
    social: dict[str, Any]
    governance: dict[str, Any]
    engagement: dict[str, Any]
    verification: dict[str, Any]