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
