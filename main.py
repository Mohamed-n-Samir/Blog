from fastapi import Body, FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from starlette.exceptions import HTTPException as StarletteHTTPException

POSTS = [
    {
        "id": 1,
        "slug": "almost-half-of-ai-written-code-fails-in-production",
        "title": "Almost Half of AI-Written Code Fails in Production — Here's Why That Matters",
        "description": "A new report found that 44% of AI-generated code breaks when it hits real users. Not in testing. In production. Here's what's actually going on.",
        "image": "imgs/ai_code_fails.png",
        "date": "Apr 17, 2026",
        "read_time": "6 min read",
        "pinned": True,
        "tags": [
            "AI",
            "Software Engineering",
        ],
    },
    {
        "id": 2,
        "slug": "ai-agents-are-changing-how-we-write-software",
        "title": "AI Agents Are Changing How We Write Software — And Most Developers Aren't Ready",
        "description": "AI agents don't just autocomplete your code anymore. They plan, execute, debug, and ship. Here's what that actually means for developer workflows.",
        "image": "imgs/keyboard_setup.png",
        "date": "Feb 10, 2026",
        "read_time": "4 min read",
        "pinned": True,
        "tags": [
            "AI",
            "Software Engineering",
            "Developer Tools",
        ],
    },
    {
        "id": 3,
        "slug": "your-tools-are-getting-more-expensive",
        "title": "Your Tools Are Getting More Expensive — And It's Only Going to Get Worse",
        "description": "GitHub Copilot paused signups, removed models, and is switching to token billing. Amazon Bedrock keeps locking models. Here is how to keep costs manageable.",
        "image": "imgs/ai_tools_cost.png",
        "date": "May 1, 2026",
        "read_time": "6 min read",
        "pinned": False,
        "tags": [
            "Developer Tools",
            "AI",
        ],
    },
]

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")


# Client pages
@app.get("/", include_in_schema=False, name="root")
@app.get("/blog", include_in_schema=False, name="blog")
def home(request: Request):
    return templates.TemplateResponse(request, "pages/index.html", {"posts": POSTS})


@app.get("/blog/post/{id}", include_in_schema=False, name="post")
def post(id: int, request: Request):
    for post in POSTS:
        if post["id"] == id:
            return templates.TemplateResponse(
                request, "pages/post.html", {"post": post}
            )
    return templates.TemplateResponse(
        request, "errors/404.html",context={"message": "Post Not found"}, status_code=status.HTTP_404_NOT_FOUND
    )


@app.get("/categories", include_in_schema=False, name="categories")
def categories(request: Request):
    return templates.TemplateResponse(request, "pages/categories.html")


# Server API
@app.get("/api/blog/post/{id}", include_in_schema=True)
def get_post(id: int, request: Request):
    for post in POSTS:
        if post["id"] == id:
            return {"post": post}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="there is no post exist with that id",
            )


# Exceptions
@app.exception_handler(status.HTTP_404_NOT_FOUND)
def not_found(request: Request, exc: HTTPException):
    message = "The page you're looking for doesn't exist or has been moved."
    
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": message},
        )

    return templates.TemplateResponse(
        request=request,
        name="errors/404.html",
        context={"message": message},
        status_code=status.HTTP_404_NOT_FOUND,
    )


@app.exception_handler(StarletteHTTPException)
def handle_exceptions(request: Request, exc: StarletteHTTPException):
    message = (
        exc.detail
        if exc.detail
        else "An error occurred. Please check your request and try again."
    )
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": message},
        )

    return templates.TemplateResponse(
        request=request,
        name="errors/error.html",
        context={"message": message, "status_code": exc.status_code},
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
def handle_validation_errors(request: Request, exc: RequestValidationError):
    if request.url.path.startswith('/api'):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exc.errors()},
        )
    
    error_msg = "Invalid request. Please check your input and try again."
    
    return templates.TemplateResponse(
        request=request,
        name="errors/error.html",
        context={"message": error_msg, "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT},
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
