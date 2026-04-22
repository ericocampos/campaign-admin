from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Campaign, ChecklistItem, ChecklistStatus

router = APIRouter()


def _campaign(db: Session, slug: str) -> Campaign:
    c = db.query(Campaign).filter_by(slug=slug).first()
    if not c:
        raise HTTPException(404)
    return c


@router.get("/campaigns/{slug}/checklist", response_class=HTMLResponse)
def tab(slug: str, request: Request, db: Session = Depends(get_db)):
    campaign = _campaign(db, slug)
    return request.app.state.templates.TemplateResponse(
        request, "partials/checklist.html", {"campaign": campaign}
    )


@router.post("/campaigns/{slug}/checklist", response_class=HTMLResponse)
def create(
    slug: str,
    request: Request,
    group_name: str = Form(default=""),
    text: str = Form(...),
    db: Session = Depends(get_db),
):
    campaign = _campaign(db, slug)
    item = ChecklistItem(campaign_id=campaign.id, group_name=group_name or None, text=text)
    db.add(item)
    db.commit()
    db.refresh(campaign)
    return request.app.state.templates.TemplateResponse(
        request, "partials/checklist.html", {"campaign": campaign}
    )


@router.post("/checklist/{item_id}/toggle", response_class=HTMLResponse)
def toggle(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.get(ChecklistItem, item_id)
    if not item:
        raise HTTPException(404)
    if item.status == ChecklistStatus.done:
        item.status = ChecklistStatus.pending
        item.done_at = None
    else:
        item.status = ChecklistStatus.done
        item.done_at = datetime.now(UTC)
    db.commit()
    return request.app.state.templates.TemplateResponse(
        request, "partials/checklist_item.html", {"i": item}
    )


@router.post("/checklist/{item_id}/delete", response_class=HTMLResponse)
def delete(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ChecklistItem, item_id)
    if not item:
        raise HTTPException(404)
    db.delete(item)
    db.commit()
    return ""
