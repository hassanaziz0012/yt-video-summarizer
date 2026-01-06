"""
General utility functions.
"""

import re


def extract_video_id(url: str) -> str:
    """
    Extract the video ID from a YouTube URL.

    Supports formats:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID

    Args:
        url: A YouTube video URL.

    Returns:
        The 11-character video ID.

    Raises:
        ValueError: If the URL format is not recognized.
    """
    patterns = [
        r"(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be\/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError(f"Could not extract video ID from URL: {url}")
