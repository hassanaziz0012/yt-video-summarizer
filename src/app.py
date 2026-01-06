from pathlib import Path
import json

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils import (
    extract_video_id,
    get_transcript,
    get_video_info,
)
from utils.gemini import ask, SUMMARIZE_PROMPT
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Mount static files directory
app.mount(
    "/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static"
)

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


def sse_event(event_type: str, data: dict) -> str:
    """Format a server-sent event."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


@app.post("/api/summarize")
async def summarize(video_url: str = Form(...)):
    """
    Accept a YouTube video URL, fetch captions, and summarize using Gemini.
    Uses Server-Sent Events to stream progress updates.

    Args:
        video_url: The YouTube video URL from form data.

    Returns:
        StreamingResponse with SSE events for progress and final result.
    """
    
    def generate_events():
        try:
            # Extract video ID from URL
            video_id = extract_video_id(video_url)

            # Step 1: Fetching video info
            yield sse_event("progress", {"message": "Fetching video info"})
            video_info = get_video_info(video_id)

            # Step 2: Fetching transcript
            yield sse_event("progress", {"message": "Fetching video transcript"})
            transcript = get_transcript(video_id)

            # Step 3: Summarizing with AI
            yield sse_event("progress", {"message": "Summarizing with AI"})
            prompt = SUMMARIZE_PROMPT.format(transcript=transcript)
            summary = ask(prompt=prompt)

            # Send complete event with all data
            yield sse_event("complete", {
                "video_id": video_id,
                "video_title": video_info["title"],
                "thumbnail": video_info["thumbnail"],
                "summary": summary,
            })

        except ValueError as e:
            print(f"ValueError in summarize: {e}")
            yield sse_event("error", {"error": str(e)})
        except Exception as e:
            print(f"Unexpected error in summarize: {e}")
            yield sse_event("error", {"error": "An unexpected error occurred"})

    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

