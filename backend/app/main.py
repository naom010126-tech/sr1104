from __future__ import annotations

import json
import os
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from .db import Base, engine, SessionLocal, settings
from . import models, schemas
from .services.pdf_extraction import extract_pages
from .services.metrics_extraction import PageRecord, extract_metrics, compute_values
from .services.report_generation import generate_report
from .services.pdf_report import markdown_to_pdf

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    os.makedirs(settings.storage_path, exist_ok=True)
    os.makedirs("./data", exist_ok=True)
    Base.metadata.create_all(bind=engine)


@app.post("/cases", response_model=schemas.CaseResponse)
def create_case(payload: schemas.CaseCreate, db: Session = Depends(get_db)):
    case = models.Case(name=payload.name)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@app.post("/cases/{case_id}/documents", response_model=schemas.DocumentResponse)
def upload_document(
    case_id: int,
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    case = db.get(models.Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if doc_type not in {"重調", "工事", "規約", "細則", "長修"}:
        raise HTTPException(status_code=400, detail="Invalid document type")

    case_dir = os.path.join(settings.storage_path, str(case_id))
    os.makedirs(case_dir, exist_ok=True)
    file_path = os.path.join(case_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    doc = models.Document(
        case_id=case_id,
        doc_type=doc_type,
        filename=file.filename,
        path=file_path,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc


@app.post("/cases/{case_id}/analyze", response_model=schemas.AnalyzeResponse)
def analyze_case(case_id: int, db: Session = Depends(get_db)):
    case = db.get(models.Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    db.query(models.Page).filter(
        models.Page.document_id.in_([doc.id for doc in case.documents])
    ).delete(synchronize_session=False)
    db.query(models.ExtractedMetrics).filter_by(case_id=case_id).delete(synchronize_session=False)

    pages: List[PageRecord] = []
    for doc in case.documents:
        extracted = extract_pages(doc.path)
        doc.page_count = len(extracted)
        for page in extracted:
            page_record = models.Page(document_id=doc.id, page_index=page.page_index, text=page.text)
            db.add(page_record)
            pages.append(PageRecord(doc_type=doc.doc_type, page_index=page.page_index, text=page.text))

    metrics = extract_metrics(pages)
    metrics_entry = models.ExtractedMetrics(case_id=case_id, json=json.dumps(metrics, ensure_ascii=False))
    db.add(metrics_entry)

    db.add(models.AuditEvent(case_id=case_id, type="analyze", payload_json=json.dumps({"documents": [d.id for d in case.documents]}, ensure_ascii=False)))

    db.commit()

    return schemas.AnalyzeResponse(case_id=case_id, extracted_metrics=metrics)


@app.post("/cases/{case_id}/generate-report", response_model=schemas.ReportResponse)
def generate_case_report(case_id: int, db: Session = Depends(get_db)):
    case = db.get(models.Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    pages = (
        db.query(models.Page, models.Document)
        .join(models.Document, models.Page.document_id == models.Document.id)
        .filter(models.Document.case_id == case_id)
        .order_by(models.Document.id, models.Page.page_index)
        .all()
    )

    doc_text_with_page_refs = ""
    for page, document in pages:
        doc_text_with_page_refs += f"[{document.doc_type} p{page.page_index + 1}]\n{page.text}\n\n"

    metrics_entry = db.query(models.ExtractedMetrics).filter_by(case_id=case_id).order_by(models.ExtractedMetrics.id.desc()).first()
    if not metrics_entry:
        raise HTTPException(status_code=400, detail="Metrics not found. Run analyze first.")
    metrics = json.loads(metrics_entry.json)
    computed = compute_values(metrics)

    markdown = generate_report(doc_text_with_page_refs, metrics, computed)

    report = db.query(models.Report).filter_by(case_id=case_id).first()
    if report:
        report.markdown = markdown
    else:
        report = models.Report(case_id=case_id, markdown=markdown)
        db.add(report)

    db.add(models.AuditEvent(case_id=case_id, type="report", payload_json=json.dumps({"pages": len(pages)}, ensure_ascii=False)))

    db.commit()

    return schemas.ReportResponse(case_id=case_id, markdown=markdown)


@app.get("/cases/{case_id}", response_model=schemas.CaseDetail)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.get(models.Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    metrics_entry = db.query(models.ExtractedMetrics).filter_by(case_id=case_id).order_by(models.ExtractedMetrics.id.desc()).first()
    report = db.query(models.Report).filter_by(case_id=case_id).first()

    return schemas.CaseDetail(
        id=case.id,
        name=case.name,
        created_at=case.created_at,
        documents=case.documents,
        extracted_metrics=json.loads(metrics_entry.json) if metrics_entry else None,
        report_markdown=report.markdown if report else None,
    )


@app.get("/cases/{case_id}/report.pdf")
def download_report(case_id: int, db: Session = Depends(get_db)):
    report = db.query(models.Report).filter_by(case_id=case_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    pdf_bytes = markdown_to_pdf(report.markdown)
    return Response(content=pdf_bytes, media_type="application/pdf")
