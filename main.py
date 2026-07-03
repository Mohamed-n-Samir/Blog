from fastapi import Body, FastAPI, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

templates = Jinja2Templates(directory=BASE_DIR / "templates")

@app.get('/', include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(request, "home.html")
