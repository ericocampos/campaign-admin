from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import (
    Campaign,
    CampaignStatus,
    ChecklistItem,
    ChecklistStatus,
    LogEntry,
    Step,
    StepStatus,
)


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


def test_step_belongs_to_campaign(session):
    c = Campaign(slug="c1", name="C1")
    session.add(c)
    session.commit()
    s = Step(campaign_id=c.id, sequence=1, name="Week 1", channel="r/SideProject",
             status=StepStatus.planned, metrics={"upvotes_24h": 0})
    session.add(s)
    session.commit()
    session.refresh(s)
    assert s.id is not None
    assert s.metrics == {"upvotes_24h": 0}
    assert s.campaign.slug == "c1"


def test_step_cascade_delete(session):
    c = Campaign(slug="c2", name="C2")
    c.steps.append(Step(sequence=1, name="S1", channel="x", status=StepStatus.planned, metrics={}))
    session.add(c)
    session.commit()
    step_id = c.steps[0].id
    session.delete(c)
    session.commit()
    assert session.get(Step, step_id) is None


def test_checklist_item_create(session):
    c = Campaign(slug="c3", name="C3")
    c.checklist_items.append(
        ChecklistItem(group_name="Phase 0", sequence=1, text="Do a thing",
                      status=ChecklistStatus.pending)
    )
    session.add(c)
    session.commit()
    assert len(c.checklist_items) == 1
    assert c.checklist_items[0].text == "Do a thing"


def test_log_entry_defaults(session):
    c = Campaign(slug="c4", name="C4")
    c.log_entries.append(LogEntry(category="bug", title="Crash on open"))
    session.add(c)
    session.commit()
    le = c.log_entries[0]
    assert le.count == 1
    assert le.body == ""
    assert le.occurred_at is not None
