from fastapi.templating import Jinja2Templates
from app.constants.constant import ROOT_DIR
from fastapi import Request

def inject_user(request: Request):
    return {"current_user": getattr(request.state, "user", None)}

templates = Jinja2Templates(
    directory=ROOT_DIR / "templates",
    context_processors=[inject_user]
)
