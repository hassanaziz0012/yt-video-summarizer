from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Form, Depends

from models.user import User
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db import init_db
from utils import (
    extract_video_id,
    get_transcript,
    get_video_info,
    get_oauth_authorization_url,
    exchange_code_for_tokens,
    get_user_by_id,
)
from utils.gemini import ask, SUMMARIZE_PROMPT
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

# Mount static files directory
app.mount(
    "/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static"
)

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Session cookie configuration
SESSION_COOKIE_NAME = "session_user_id"


def get_current_user(request: Request) -> User | None:
    """Get the currently logged-in user from session cookie."""
    user_id = request.cookies.get(SESSION_COOKIE_NAME)
    if user_id is None:
        return None
    try:
        return get_user_by_id(int(user_id))
    except (ValueError, TypeError):
        return None


@app.get("/auth/login")
async def auth_login():
    """Redirect user to Google OAuth authorization page."""
    authorization_url, state = get_oauth_authorization_url()
    return RedirectResponse(url=authorization_url)


@app.get("/auth/google-oauth-callback")
async def auth_callback(code: str):
    """
    Handle the OAuth callback from Google.

    Exchanges the authorization code for tokens, saves user to database,
    and sets session cookie to keep user logged in.
    """
    try:
        user = exchange_code_for_tokens(code)
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=str(user.id),
            httponly=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 30,  # 30 days
        )
        return response
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": f"Authentication failed: {str(e)}"}
        )


@app.get("/auth/logout")
async def auth_logout():
    """Log out the user by clearing the session cookie."""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key=SESSION_COOKIE_NAME)
    return response


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user: User | None = Depends(get_current_user)):
    return templates.TemplateResponse(request, "index.html", {"user": user})


@app.post("/api/summarize")
async def summarize(video_url: str = Form(...)):
    """
    Accept a YouTube video URL, fetch captions, and summarize using Gemini.

    Args:
        video_url: The YouTube video URL from form data.

    Returns:
        JSON response with video_id, video_title, thumbnail, and summary.
    """
    try:
        # Extract video ID from URL
        video_id = extract_video_id(video_url)

        # Fetch video info (title, thumbnail) - no auth required
        video_info = get_video_info(video_id)

        # Fetch transcript using youtube-transcript-api (works for any public video)
        transcript = get_transcript(video_id)

        # Generate summary using Gemini
        prompt = SUMMARIZE_PROMPT.format(transcript=transcript)
        summary = ask(prompt=prompt)

        return {
            "video_id": video_id,
            "video_title": video_info["title"],
            "thumbnail": video_info["thumbnail"],
            "summary": summary,
        }

    except ValueError as e:
        print(f"ValueError in summarize: {e}")
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        print(f"Unexpected error in summarize: {e}")
        return JSONResponse(
            status_code=500, content={"error": "An unexpected error occurred"}
        )

