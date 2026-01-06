"""
Utility modules for YouTube video summarizer.
"""

from utils.oauth import (
    SCOPES,
    REDIRECT_URI,
    load_client_config,
    get_oauth_authorization_url,
    get_user_info,
    exchange_code_for_tokens,
    get_user_by_id,
    get_authenticated_credentials,
)
from utils.youtube import (
    build_youtube_client,
    get_captions_list,
    find_english_caption,
    download_caption,
    get_video_info,
    get_english_caption_for_video,
)
from utils.general import extract_video_id

__all__ = [
    # OAuth
    "SCOPES",
    "REDIRECT_URI",
    "load_client_config",
    "get_oauth_authorization_url",
    "get_user_info",
    "exchange_code_for_tokens",
    "get_user_by_id",
    "get_authenticated_credentials",
    # YouTube
    "build_youtube_client",
    "get_captions_list",
    "find_english_caption",
    "download_caption",
    "get_video_info",
    "get_english_caption_for_video",
    # General
    "extract_video_id",
]
