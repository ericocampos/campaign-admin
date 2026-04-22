from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Campaign, CampaignStatus


def test_campaign_create_with_defaults(session):
    c = Campaign(slug="reddit-launch", name="Reddit Launch", overview="hello")
    session.add(c)
    session.commit()
    session.refresh(c)
    assert c.id is not None
    assert c.status == CampaignStatus.draft
    assert c.created_at is not None
    assert c.updated_at is not None


def test_campaign_slug_is_unique(session):
    session.add(Campaign(slug="dup", name="A"))
    session.commit()
    session.add(Campaign(slug="dup", name="B"))
    with pytest.raises(IntegrityError):
        session.commit()


def test_campaign_status_transitions(session):
    c = Campaign(slug="x", name="X", status=CampaignStatus.active, start_date=date(2026, 5, 1))
    session.add(c)
    session.commit()
    c.status = CampaignStatus.paused
    session.commit()
    session.refresh(c)
    assert c.status == CampaignStatus.paused
