from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse

from app.markdown import render_markdown

router = APIRouter()


@router.post("/markdown/preview", response_class=HTMLResponse)
def preview(source: str = Form(default="")) -> str:
    return render_markdown(source)
