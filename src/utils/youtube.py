"""
YouTube Data API utility functions.
"""

from googleapiclient.discovery import build, Resource
from googleapiclient.http import HttpRequest

from utils.oauth import get_authenticated_credentials
from utils.general import extract_video_id


def build_youtube_client() -> Resource:
    """
    Build and return an OAuth-authenticated YouTube API client.

    Returns:
        A YouTube API Resource object for making API calls.

    Raises:
        ValueError: If not authenticated (no valid tokens).
    """
    credentials = get_authenticated_credentials()

    if not credentials:
        raise ValueError(
            "Not authenticated. Please authenticate via /auth/login first."
        )

    return build("youtube", "v3", credentials=credentials)


def get_captions_list(youtube: Resource, video_id: str) -> list[dict]:
    """
    Fetch the list of available captions for a video.

    Args:
        youtube: An authenticated YouTube API client.
        video_id: The YouTube video ID.

    Returns:
        A list of caption track metadata dictionaries.
    """
    request: HttpRequest = youtube.captions().list(part="snippet", videoId=video_id)
    response = request.execute()

    return response.get("items", [])


def find_english_caption(captions: list[dict]) -> dict | None:
    """
    Find the first English caption track from a list of captions.

    Looks for language codes starting with 'en' (e.g., 'en', 'en-US', 'en-GB').

    Args:
        captions: A list of caption track metadata dictionaries.

    Returns:
        The first English caption track, or None if not found.
    """
    for caption in captions:
        language = caption.get("snippet", {}).get("language", "")
        if language.startswith("en"):
            return caption

    return None


def download_caption(youtube: Resource, caption_id: str, tfmt: str = "srt") -> str:
    """
    Download the caption content for a given caption track.

    Args:
        youtube: An OAuth-authenticated YouTube API client.
        caption_id: The ID of the caption track to download.
        tfmt: The format for the caption (default: 'srt').

    Returns:
        The caption content as a string.
    """
    request: HttpRequest = youtube.captions().download(id=caption_id, tfmt=tfmt)
    return request.execute()


def get_video_info(youtube: Resource, video_id: str) -> dict:
    """
    Fetch video title and thumbnail for a given video ID.

    Args:
        youtube: An authenticated YouTube API client.
        video_id: The YouTube video ID.

    Returns:
        A dictionary with 'title' and 'thumbnail' keys.
    """
    request: HttpRequest = youtube.videos().list(part="snippet", id=video_id)
    response = request.execute()

    items = response.get("items", [])
    if not items:
        return {"title": "", "thumbnail": ""}

    snippet = items[0].get("snippet", {})
    thumbnails = snippet.get("thumbnails", {})
    # Prefer high quality, fall back to medium, then default
    thumbnail_url = (
        thumbnails.get("high", {}).get("url")
        or thumbnails.get("medium", {}).get("url")
        or thumbnails.get("default", {}).get("url", "")
    )

    return {"title": snippet.get("title", ""), "thumbnail": thumbnail_url}


def get_english_caption_for_video(video_url: str) -> str | None:
    """
    High-level function to get English captions for a YouTube video.

    This is a convenience function that chains together:
    1. Building the YouTube client
    2. Extracting the video ID
    3. Fetching available captions
    4. Finding the first English caption
    5. Downloading the caption content

    Args:
        video_url: A YouTube video URL.

    Returns:
        The English caption content as a string, or None if no English caption exists.

    Raises:
        ValueError: If video ID cannot be extracted or not authenticated.
    """
    youtube = build_youtube_client()
    video_id = extract_video_id(video_url)

    captions = get_captions_list(youtube, video_id)
    english_caption = find_english_caption(captions)

    if not english_caption:
        return None

    caption_id = english_caption.get("id")
    return download_caption(youtube, caption_id)
