from app.models import Campaign, Step, StepStatus


def _mk_campaign(session, slug="c"):
    c = Campaign(slug=slug, name=slug)
    session.add(c)
    session.commit()
    return c


def test_steps_tab_empty(client, session):
    _mk_campaign(session)
    r = client.get("/campaigns/c/steps")
    assert r.status_code == 200
    assert "No steps yet" in r.text


def test_steps_tab_lists(client, session):
    c = _mk_campaign(session)
    session.add(
        Step(
            campaign_id=c.id,
            sequence=1,
            name="Wk1",
            channel="r/x",
            status=StepStatus.planned,
            metrics={},
        )
    )
    session.commit()
    r = client.get("/campaigns/c/steps")
    assert "Wk1" in r.text
    assert "r/x" in r.text


def test_create_step(client, session):
    _mk_campaign(session)
    r = client.post(
        "/campaigns/c/steps",
        data={"sequence": "1", "name": "Week 1", "channel": "r/SideProject"},
    )
    assert r.status_code in (200, 204)
    s = session.query(Step).filter_by(name="Week 1").one()
    assert s.channel == "r/SideProject"


def test_step_drawer(client, session):
    c = _mk_campaign(session, "d1")
    s = Step(
        campaign_id=c.id,
        sequence=1,
        name="X",
        channel="",
        status=StepStatus.planned,
        metrics={},
        content="# hello",
    )
    session.add(s)
    session.commit()
    r = client.get(f"/campaigns/d1/steps/{s.id}")
    assert r.status_code == 200
    assert "X" in r.text
    assert "hello" in r.text


def test_step_update(client, session):
    c = _mk_campaign(session, "u")
    s = Step(
        campaign_id=c.id,
        sequence=1,
        name="A",
        channel="",
        status=StepStatus.planned,
        metrics={},
    )
    session.add(s)
    session.commit()
    r = client.post(
        f"/campaigns/u/steps/{s.id}",
        data={
            "sequence": "2",
            "name": "B",
            "channel": "x",
            "status": "live",
            "url": "https://e.com",
            "content": "c",
            "retro": "r",
        },
    )
    assert r.status_code in (200, 204)
    session.expire_all()
    s2 = session.get(Step, s.id)
    assert s2.name == "B"
    assert s2.status == StepStatus.live


def test_step_delete(client, session):
    c = _mk_campaign(session, "x")
    s = Step(
        campaign_id=c.id,
        sequence=1,
        name="A",
        channel="",
        status=StepStatus.planned,
        metrics={},
    )
    session.add(s)
    session.commit()
    step_id = s.id
    r = client.post(f"/campaigns/x/steps/{step_id}/delete")
    assert r.status_code in (200, 204)
    session.expire_all()
    assert session.get(Step, step_id) is None
