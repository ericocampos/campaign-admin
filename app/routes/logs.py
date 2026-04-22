from collections import Counter

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.markdown import render_markdown
from app.models import Campaign, LogEntry

router = APIRouter()


def _campaign(db: Session, slug: str) -> Campaign:
    c = db.query(Campaign).filter_by(slug=slug).first()
    if not c:
        raise HTTPException(404)
    return c


def _ctx(campaign: Campaign, filter_cat: str | None = None) -> dict:
    entries = campaign.log_entries
    if filter_cat:
        entries = [e for e in entries if e.category == filter_cat]
    counts = Counter(e.category for e in campaign.log_entries)
    return {
        "campaign": campaign,
        "entries": entries,
        "categories": sorted(counts.keys()),
        "category_counts": counts,
        "rendered": {e.id: render_markdown(e.body) for e in entries if e.body},
    }


@router.get("/campaigns/{slug}/logs", response_class=HTMLResponse)
def tab(
    slug: str,
    request: Request,
    category: str | None = None,
    db: Session = Depends(get_db),
):
    return request.app.state.templates.TemplateResponse(
        request, "partials/logs.html", _ctx(_campaign(db, slug), category)
    )


@router.post("/campaigns/{slug}/logs", response_class=HTMLResponse)
def create(
    slug: str,
    request: Request,
    category: str = Form(...),
    title: str = Form(...),
    body: str = Form(default=""),
    source: str = Form(default=""),
    db: Session = Depends(get_db),
):
    campaign = _campaign(db, slug)
    le = LogEntry(
        campaign_id=campaign.id,
        category=category,
        title=title,
        body=body,
        source=source or None,
    )
    db.add(le)
    db.commit()
    db.refresh(campaign)
    return request.app.state.templates.TemplateResponse(
        request, "partials/logs.html", _ctx(campaign)
    )


@router.post("/logs/{log_id}/increment", response_class=HTMLResponse)
def increment(log_id: int, request: Request, db: Session = Depends(get_db)):
    le = db.get(LogEntry, log_id)
    if not le:
        raise HTTPException(404)
    le.count += 1
    db.commit()
    return request.app.state.templates.TemplateResponse(
        request,
        "partials/log_entry.html",
        {
            "le": le,
            "rendered": {le.id: render_markdown(le.body) if le.body else ""},
        },
    )


@router.post("/logs/{log_id}/delete", response_class=HTMLResponse)
def delete(log_id: int, db: Session = Depends(get_db)):
    le = db.get(LogEntry, log_id)
    if not le:
        raise HTTPException(404)
    db.delete(le)
    db.commit()
    return ""
