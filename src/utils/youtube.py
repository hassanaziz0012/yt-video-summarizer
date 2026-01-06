"""
YouTube utility functions.

Uses youtube-transcript-api for fetching transcripts (works for any public video)
and YouTube Data API for video metadata.
"""

import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
from youtube_transcript_api.proxies import WebshareProxyConfig

from .general import extract_video_id


def _get_transcript_api() -> YouTubeTranscriptApi:
    """
    Get a YouTubeTranscriptApi instance, optionally configured with Webshare proxy.

    If WEBSHARE_USERNAME and WEBSHARE_PASSWORD environment variables are set,
    the API will use Webshare rotating residential proxies to avoid IP bans.

    Returns:
        A configured YouTubeTranscriptApi instance.
    """
    webshare_username = os.environ.get("WEBSHARE_USERNAME")
    webshare_password = os.environ.get("WEBSHARE_PASSWORD")

    if webshare_username and webshare_password:
        proxy_config = WebshareProxyConfig(
            proxy_username=webshare_username,
            proxy_password=webshare_password,
        )
        return YouTubeTranscriptApi(proxy_config=proxy_config)

    return YouTubeTranscriptApi()


def get_transcript(video_id: str, languages: list[str] = ["en"]) -> str:
    """
    Fetch the transcript for a YouTube video.

    Uses youtube-transcript-api which works for any public video
    without requiring OAuth authentication.

    If WEBSHARE_USERNAME and WEBSHARE_PASSWORD environment variables are set,
    requests will be proxied through Webshare to avoid IP bans on cloud platforms.

    Args:
        video_id: The YouTube video ID.
        languages: List of language codes to try (default: ['en']).

    Returns:
        The transcript as a plain text string.

    Raises:
        ValueError: If no transcript is available for the video.
    """
    try:
        api = _get_transcript_api()
        transcript = api.fetch(video_id, languages=languages)
        # Combine all segments into a single text
        return " ".join(segment.text for segment in transcript)
    except TranscriptsDisabled:
        raise ValueError("Transcripts are disabled for this video")
    except NoTranscriptFound:
        raise ValueError(f"No transcript found in languages: {languages}")
    except VideoUnavailable:
        raise ValueError("Video is unavailable")


def get_video_info(video_id: str) -> dict:
    """
    Fetch video title and thumbnail for a given video ID.

    Uses YouTube's oEmbed endpoint which doesn't require authentication.

    Args:
        video_id: The YouTube video ID.

    Returns:
        A dictionary with 'title' and 'thumbnail' keys.
    """
    # Use high-quality thumbnail URL pattern (works for all public videos)
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

    # For title, we can use oEmbed API (no auth required)
    import urllib.request
    import json

    try:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        with urllib.request.urlopen(oembed_url) as response:
            data = json.loads(response.read().decode())
            return {"title": data.get("title", ""), "thumbnail": thumbnail_url}
    except Exception:
        return {"title": "", "thumbnail": thumbnail_url}


def get_english_caption_for_video(video_url: str) -> str | None:
    """
    High-level function to get English captions for a YouTube video.

    Args:
        video_url: A YouTube video URL.

    Returns:
        The English caption content as a string, or None if no English caption exists.

    Raises:
        ValueError: If video ID cannot be extracted.
    """
    video_id = extract_video_id(video_url)
    try:
        return get_transcript(video_id)
    except ValueError:
        return None
