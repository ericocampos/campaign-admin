import bleach
import markdown2

ALLOWED_TAGS = [
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "a",
    "code",
    "pre",
    "blockquote",
    "strong",
    "em",
    "hr",
    "br",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
]

ALLOWED_ATTRS = {
    "a": ["href", "title"],
}

ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def render_markdown(source: str) -> str:
    raw = markdown2.markdown(
        source or "",
        extras=["tables", "fenced-code-blocks", "strike", "break-on-newline"],
    )
    return bleach.clean(
        raw,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
