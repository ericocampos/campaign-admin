from app.models import Campaign, ChecklistItem, ChecklistStatus


def _mk(session, slug="ck"):
    c = Campaign(slug=slug, name=slug)
    session.add(c)
    session.commit()
    return c


def test_checklist_tab_empty(client, session):
    _mk(session)
    r = client.get("/campaigns/ck/checklist")
    assert r.status_code == 200


def test_checklist_create(client, session):
    _mk(session)
    r = client.post(
        "/campaigns/ck/checklist",
        data={"group_name": "Phase 0", "text": "Do X"},
    )
    assert r.status_code in (200, 204)
    assert session.query(ChecklistItem).filter_by(text="Do X").one() is not None


def test_checklist_toggle(client, session):
    c = _mk(session)
    i = ChecklistItem(campaign_id=c.id, text="Y", status=ChecklistStatus.pending)
    session.add(i)
    session.commit()
    r = client.post(f"/checklist/{i.id}/toggle")
    assert r.status_code == 200
    session.expire_all()
    assert session.get(ChecklistItem, i.id).status == ChecklistStatus.done


def test_checklist_delete(client, session):
    c = _mk(session)
    i = ChecklistItem(campaign_id=c.id, text="Z")
    session.add(i)
    session.commit()
    item_id = i.id
    r = client.post(f"/checklist/{item_id}/delete")
    assert r.status_code in (200, 204)
    session.expire_all()
    assert session.get(ChecklistItem, item_id) is None
