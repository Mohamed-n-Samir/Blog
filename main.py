from fastapi import Body, FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
app.mount('/static', StaticFiles(directory=BASE_DIR / 'static'), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")

@app.get('/', include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(request, "home.html")
