from app.markdown import render_markdown


def test_renders_basic_markdown():
    html = render_markdown("# Hello\n\nworld")
    assert "<h1>Hello</h1>" in html
    assert "<p>world</p>" in html


def test_strips_script_tags():
    html = render_markdown("<script>alert(1)</script>ok")
    assert "<script" not in html.lower()
    assert "ok" in html


def test_strips_event_handlers():
    html = render_markdown('<a href="#" onclick="alert(1)">x</a>')
    assert "onclick" not in html.lower()


def test_strips_javascript_urls():
    html = render_markdown('<a href="javascript:alert(1)">x</a>')
    assert "javascript:" not in html.lower()


def test_strips_iframe():
    html = render_markdown('<iframe src="x"></iframe>')
    assert "<iframe" not in html.lower()


def test_allows_tables():
    md = "| a | b |\n|---|---|\n| 1 | 2 |"
    html = render_markdown(md)
    assert "<table>" in html
    assert "<td>1</td>" in html


def test_preview_route_returns_html(client):
    r = client.post("/markdown/preview", data={"source": "# hi"})
    assert r.status_code == 200
    assert "<h1>hi</h1>" in r.text
