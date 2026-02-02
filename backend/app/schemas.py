from datetime import datetime
from pydantic import BaseModel
from typing import Any, Optional


class CaseCreate(BaseModel):
    name: Optional[str] = None


class CaseResponse(BaseModel):
    id: int
    name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: int
    case_id: int
    doc_type: str
    filename: str
    path: str
    page_count: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyzeResponse(BaseModel):
    case_id: int
    extracted_metrics: dict[str, Any]


class ReportResponse(BaseModel):
    case_id: int
    markdown: str


class CaseDetail(BaseModel):
    id: int
    name: Optional[str]
    created_at: datetime
    documents: list[DocumentResponse]
    extracted_metrics: Optional[dict[str, Any]] = None
    report_markdown: Optional[str] = None

    class Config:
        from_attributes = True
