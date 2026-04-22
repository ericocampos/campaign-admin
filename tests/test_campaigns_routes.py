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
