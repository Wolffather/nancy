import sys
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import uvicorn
from jinja2 import Environment, FileSystemLoader, select_autoescape
import markdown

from nancy.config import load_config
from nancy.llm_client import LLMClient
from nancy.orchestrator import Orchestrator
from nancy.analyzers.factory import detect_language

app = FastAPI(title="Nancy Web Interface", version="0.1.0")

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
if not TEMPLATES_DIR.exists():
    TEMPLATES_DIR.mkdir(parents=True)

# Jinja2 окружение
env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(['html', 'xml']),
    enable_async=False,
)

# Фильтр для Markdown
def md_filter(text):
    if not text:
        return ""
    return markdown.markdown(text, extensions=[
        'fenced_code',
        'codehilite',
        'tables',
        'toc'
    ])

env.filters['md'] = md_filter

config = load_config()
llm = LLMClient(config)
orchestrator = Orchestrator(config, llm, mock=False)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    template = env.get_template("index.html")
    content = template.render()
    return HTMLResponse(content=content)


@app.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    description: str = Form(""),
    ticket_id: str = Form(""),
    project_path: str = Form(""),
    language: str = Form(""),
    framework: str = Form(""),
    skill: str = Form("api"),
    strategy: bool = Form(False),
    mock: bool = Form(False),
):
    try:
        if project_path and not language:
            try:
                language = detect_language(Path(project_path))
            except ValueError:
                language = "java"

        result = orchestrator.run(
            ticket_id=ticket_id or None,
            description=description or None,
            project_path=project_path or None,
            language=language or None,
            framework=framework or None,
            skill=skill,
            strategy=strategy,
        )

        template = env.get_template("index.html")
        content = template.render(
            result=result,
            description=description,
            ticket_id=ticket_id,
            project_path=project_path,
            language=language,
            framework=framework,
            skill=skill,
            strategy=strategy,
            mock=mock,
        )
        return HTMLResponse(content=content)

    except Exception as e:
        template = env.get_template("index.html")
        content = template.render(
            error=str(e),
            description=description,
            ticket_id=ticket_id,
            project_path=project_path,
            language=language,
            framework=framework,
            skill=skill,
        )
        return HTMLResponse(content=content)


@app.get("/health")
async def health():
    return {"status": "ok", "message": "Nancy web interface is running"}


def run_server(host="0.0.0.0", port=8000, reload=False):
    uvicorn.run(
        "nancy.web.app:app",
        host=host,
        port=port,
        reload=reload
    )