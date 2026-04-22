from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Campaign, Step, StepStatus

router = APIRouter()


def _get_campaign(db: Session, slug: str) -> Campaign:
    c = db.query(Campaign).filter_by(slug=slug).first()
    if not c:
        raise HTTPException(404)
    return c


def _get_step(db: Session, slug: str, step_id: int) -> Step:
    s = db.query(Step).filter_by(id=step_id).first()
    if not s or s.campaign.slug != slug:
        raise HTTPException(404)
    return s


@router.get("/campaigns/{slug}/steps", response_class=HTMLResponse)
def list_steps(slug: str, request: Request, db: Session = Depends(get_db)):
    campaign = _get_campaign(db, slug)
    return request.app.state.templates.TemplateResponse(
        request, "partials/steps.html", {"campaign": campaign}
    )


@router.post("/campaigns/{slug}/steps", response_class=HTMLResponse)
def create_step(
    slug: str,
    request: Request,
    db: Session = Depends(get_db),
    sequence: int = Form(default=0),
    name: str = Form(...),
    channel: str = Form(default=""),
    status: str = Form(default="planned"),
):
    campaign = _get_campaign(db, slug)
    s = Step(
        campaign_id=campaign.id, sequence=sequence, name=name, channel=channel,
        status=StepStatus(status), metrics={},
    )
    db.add(s)
    db.commit()
    db.refresh(campaign)
    return request.app.state.templates.TemplateResponse(
        request, "partials/steps.html", {"campaign": campaign}
    )


@router.get("/campaigns/{slug}/steps/{step_id}", response_class=HTMLResponse)
def step_drawer(slug: str, step_id: int, request: Request, db: Session = Depends(get_db)):
    step = _get_step(db, slug, step_id)
    return request.app.state.templates.TemplateResponse(
        request, "partials/step_drawer.html", {"campaign": step.campaign, "step": step}
    )


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    return datetime.fromisoformat(s)


@router.post("/campaigns/{slug}/steps/{step_id}", response_class=HTMLResponse)
async def update_step(
    slug: str, step_id: int, request: Request, db: Session = Depends(get_db),
):
    step = _get_step(db, slug, step_id)
    form = await request.form()
    step.sequence = int(form.get("sequence", step.sequence))
    step.name = (form.get("name") or "").strip() or step.name
    step.channel = form.get("channel", step.channel)
    step.status = StepStatus(form.get("status", step.status.value))
    step.url = form.get("url") or None
    step.scheduled_at = _parse_dt(form.get("scheduled_at"))
    step.posted_at = _parse_dt(form.get("posted_at"))
    step.content = form.get("content", step.content)
    step.retro = form.get("retro", step.retro)
    metrics = {}
    for key in form:
        if key.startswith("metric_"):
            v = form.get(key)
            if v == "" or v is None:
                continue
            try:
                metrics[key[len("metric_"):]] = int(v)
            except ValueError:
                metrics[key[len("metric_"):]] = v
    step.metrics = metrics
    db.commit()
    db.refresh(step.campaign)
    return request.app.state.templates.TemplateResponse(
        request, "partials/steps.html", {"campaign": step.campaign}
    )


@router.post("/campaigns/{slug}/steps/{step_id}/delete", response_class=HTMLResponse)
def delete_step(slug: str, step_id: int, request: Request, db: Session = Depends(get_db)):
    step = _get_step(db, slug, step_id)
    campaign = step.campaign
    db.delete(step)
    db.commit()
    db.refresh(campaign)
    return request.app.state.templates.TemplateResponse(
        request, "partials/steps.html", {"campaign": campaign}
    )
