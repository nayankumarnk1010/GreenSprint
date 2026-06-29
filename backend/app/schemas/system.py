from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic import ConfigDict


class DatabaseHealthResponse(BaseModel):
    status: str
    message: str
    database_url: str


class ModuleHealthResponse(BaseModel):
    module_number: int
    module_name: str
    status: str
    tables_required: int
    tables_found: int
    missing_tables: list[str]
    checks_required: int = 0
    checks_found: int = 0
    missing_checks: list[str] = []
    details: dict[str, Any] = {}


class SystemHealthResponse(BaseModel):
    status: str
    database: DatabaseHealthResponse
    modules: list[ModuleHealthResponse]
    checked_at: datetime


class SystemPingResponse(BaseModel):
    status: str
    message: str
    app_name: str
    checked_at: datetime


class SystemIntegrationSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str
    database: DatabaseHealthResponse
    module_status: dict[str, Any]
    counts: dict[str, int]
    ai_runtime: dict[str, Any]
    checked_at: datetime