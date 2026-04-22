from app.models import Campaign


def test_index_empty(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "No campaigns yet" in r.text


def test_index_lists_campaigns(client, session):
    session.add(Campaign(slug="rl", name="Reddit Launch"))
    session.commit()
    r = client.get("/")
    assert "Reddit Launch" in r.text


def test_new_form_renders(client):
    r = client.get("/campaigns/new")
    assert r.status_code == 200
    assert "<form" in r.text
    assert 'name="name"' in r.text


def test_create_campaign(client, session):
    r = client.post(
        "/campaigns",
        data={"name": "Reddit Launch", "slug": "reddit-launch"},
        follow_redirects=False,
    )
    assert r.status_code in (302, 303)
    # Either Location header or HX-Redirect should point to the new campaign
    target = r.headers.get("location") or r.headers.get("HX-Redirect")
    assert target == "/campaigns/reddit-launch"
    c = session.query(Campaign).filter_by(slug="reddit-launch").one()
    assert c.name == "Reddit Launch"


def test_create_autoderives_slug(client, session):
    r = client.post("/campaigns", data={"name": "My Big Launch"}, follow_redirects=False)
    assert r.status_code in (302, 303)
    assert session.query(Campaign).filter_by(slug="my-big-launch").one() is not None


def test_create_rejects_duplicate_slug(client, session):
    session.add(Campaign(slug="dup", name="A"))
    session.commit()
    r = client.post("/campaigns", data={"name": "B", "slug": "dup"})
    assert r.status_code == 400


def test_show_renders_dashboard(client, session):
    session.add(Campaign(slug="rl2", name="Reddit Launch 2", overview="# Reddit"))
    session.commit()
    r = client.get("/campaigns/rl2")
    assert r.status_code == 200
    assert "Reddit Launch 2" in r.text
    assert "Overview" in r.text
    assert "Steps" in r.text
    assert "Checklist" in r.text
    assert "Logs" in r.text


def test_show_404_for_missing(client):
    r = client.get("/campaigns/missing")
    assert r.status_code == 404


def test_overview_partial_renders_markdown(client, session):
    session.add(Campaign(slug="o", name="O", overview="# Hello"))
    session.commit()
    r = client.get("/campaigns/o/overview")
    assert r.status_code == 200
    assert "<h1>Hello</h1>" in r.text
