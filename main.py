from fastapi import Body, FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

BLOGS = [
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


# Client
@app.get("/", include_in_schema=False, name="root")
@app.get("/blogs", include_in_schema=False, name="blogs")
def home(request: Request):
    return templates.TemplateResponse(
        request, "pages/index.html", {"blogs": BLOGS, "blogsLen": len(BLOGS)}
    )


@app.get("/blog", include_in_schema=False, name="blog")
def blog(request: Request):
    return templates.TemplateResponse(request, "pages/blog.html", {"blog": BLOGS[1]})


@app.get("/categories", include_in_schema=False, name="categories")
def categories(request: Request):
    return templates.TemplateResponse(request, "pages/categories.html")


# Server



