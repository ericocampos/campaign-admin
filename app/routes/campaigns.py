from datetime import date

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from slugify import slugify
from sqlalchemy.orm import Session

from app.db import get_db
from app.markdown import render_markdown
from app.models import Campaign, CampaignStatus, ChecklistStatus

router = APIRouter()


# ── Index ────────────────────────────────────────────────────────────────────


@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(Campaign.updated_at.desc()).all()
    return request.app.state.templates.TemplateResponse(
        request, "index.html", {"campaigns": campaigns}
    )


# ── New / Create ─────────────────────────────────────────────────────────────


@router.get("/campaigns/new", response_class=HTMLResponse)
def new_form(request: Request):
    return request.app.state.templates.TemplateResponse(request, "campaigns/new.html", {})


@router.post("/campaigns")
def create(
    request: Request,
    name: str = Form(...),
    slug: str = Form(default=""),
    status: str = Form(default="draft"),
    start_date: date | None = Form(default=None),
    end_date: date | None = Form(default=None),
    overview: str = Form(default=""),
    db: Session = Depends(get_db),
):
    final_slug = slug.strip() or slugify(name)
    if db.query(Campaign).filter_by(slug=final_slug).first():
        raise HTTPException(status_code=400, detail=f"Slug '{final_slug}' already exists")
    c = Campaign(
        slug=final_slug,
        name=name,
        status=CampaignStatus(status),
        start_date=start_date,
        end_date=end_date,
        overview=overview,
    )
    db.add(c)
    db.commit()
    response = RedirectResponse(url=f"/campaigns/{final_slug}", status_code=303)
    response.headers["HX-Redirect"] = f"/campaigns/{final_slug}"
    return response


# ── Show ─────────────────────────────────────────────────────────────────────


def _get_or_404(db: Session, slug: str) -> Campaign:
    c = db.query(Campaign).filter_by(slug=slug).first()
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return c


def _overview_context(campaign: Campaign) -> dict:
    return {
        "campaign": campaign,
        "rendered_overview": render_markdown(campaign.overview) if campaign.overview else "",
        "checklist_done": sum(
            1 for i in campaign.checklist_items if i.status == ChecklistStatus.done
        ),
        "checklist_total": len(campaign.checklist_items),
    }


@router.get("/campaigns/{slug}", response_class=HTMLResponse)
def show(slug: str, request: Request, db: Session = Depends(get_db)):
    campaign = _get_or_404(db, slug)
    return request.app.state.templates.TemplateResponse(
        request, "campaigns/show.html", _overview_context(campaign)
    )


@router.get("/campaigns/{slug}/overview", response_class=HTMLResponse)
def overview_tab(slug: str, request: Request, db: Session = Depends(get_db)):
    campaign = _get_or_404(db, slug)
    return request.app.state.templates.TemplateResponse(
        request, "partials/overview.html", _overview_context(campaign)
    )


# ── Edit / Update / Archive ───────────────────────────────────────────────────


@router.get("/campaigns/{slug}/edit", response_class=HTMLResponse)
def edit_form(slug: str, request: Request, db: Session = Depends(get_db)):
    campaign = _get_or_404(db, slug)
    return request.app.state.templates.TemplateResponse(
        request, "campaigns/edit.html", {"campaign": campaign}
    )


@router.post("/campaigns/{slug}/edit")
def update(
    slug: str,
    request: Request,
    name: str = Form(...),
    slug_new: str = Form(alias="slug"),
    status: str = Form(...),
    start_date: date | None = Form(default=None),
    end_date: date | None = Form(default=None),
    overview: str = Form(default=""),
    db: Session = Depends(get_db),
):
    campaign = _get_or_404(db, slug)
    if slug_new != campaign.slug and db.query(Campaign).filter_by(slug=slug_new).first():
        raise HTTPException(status_code=400, detail="Slug already exists")
    campaign.name = name
    campaign.slug = slug_new
    campaign.status = CampaignStatus(status)
    campaign.start_date = start_date
    campaign.end_date = end_date
    campaign.overview = overview
    db.commit()
    response = RedirectResponse(url=f"/campaigns/{slug_new}", status_code=303)
    response.headers["HX-Redirect"] = f"/campaigns/{slug_new}"
    return response


@router.post("/campaigns/{slug}/archive")
def archive(slug: str, db: Session = Depends(get_db)):
    campaign = _get_or_404(db, slug)
    campaign.status = CampaignStatus.archived
    db.commit()
    response = RedirectResponse(url="/", status_code=303)
    response.headers["HX-Redirect"] = "/"
    return response
