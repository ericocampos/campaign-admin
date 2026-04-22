from datetime import date

from pydantic import BaseModel, Field


class CampaignCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    slug: str | None = Field(default=None, max_length=100)
    status: str = "draft"
    start_date: date | None = None
    end_date: date | None = None
    overview: str = ""


class CampaignUpdate(CampaignCreate):
    pass
