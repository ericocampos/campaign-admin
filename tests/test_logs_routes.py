from app.models import Campaign, LogEntry


def _mk(session, slug="lg"):
    c = Campaign(slug=slug, name=slug)
    session.add(c)
    session.commit()
    return c


def test_logs_tab(client, session):
    _mk(session)
    r = client.get("/campaigns/lg/logs")
    assert r.status_code == 200


def test_create_log(client, session):
    _mk(session)
    r = client.post(
        "/campaigns/lg/logs",
        data={"category": "bug", "title": "Broken thing"},
    )
    assert r.status_code in (200, 204)
    assert session.query(LogEntry).filter_by(title="Broken thing").one().count == 1


def test_increment_log(client, session):
    c = _mk(session)
    le = LogEntry(campaign_id=c.id, category="feature_request", title="Dark mode")
    session.add(le)
    session.commit()
    r = client.post(f"/logs/{le.id}/increment")
    assert r.status_code == 200
    session.expire_all()
    assert session.get(LogEntry, le.id).count == 2


def test_filter_logs_by_category(client, session):
    c = _mk(session)
    session.add_all(
        [
            LogEntry(campaign_id=c.id, category="bug", title="B"),
            LogEntry(campaign_id=c.id, category="signal", title="S"),
        ]
    )
    session.commit()
    r = client.get("/campaigns/lg/logs?category=signal")
    assert "S" in r.text
    assert "B" not in r.text


def test_delete_log(client, session):
    c = _mk(session)
    le = LogEntry(campaign_id=c.id, category="bug", title="X")
    session.add(le)
    session.commit()
    log_id = le.id
    r = client.post(f"/logs/{log_id}/delete")
    assert r.status_code in (200, 204)
    session.expire_all()
    assert session.get(LogEntry, log_id) is None
