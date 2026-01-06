"""
Utility modules for YouTube video summarizer.

NOTE: OAuth imports are commented out since we use youtube-transcript-api
which doesn't require authentication.
"""

# from utils.oauth import (
#     SCOPES,
#     REDIRECT_URI,
#     load_client_config,
#     get_oauth_authorization_url,
#     get_user_info,
#     exchange_code_for_tokens,
#     get_user_by_id,
#     get_authenticated_credentials,
# )
from utils.youtube import (
    get_transcript,
    get_video_info,
    get_english_caption_for_video,
)
from utils.general import extract_video_id

__all__ = [
    # OAuth (commented out)
    # "SCOPES",
    # "REDIRECT_URI",
    # "load_client_config",
    # "get_oauth_authorization_url",
    # "get_user_info",
    # "exchange_code_for_tokens",
    # "get_user_by_id",
    # "get_authenticated_credentials",
    # YouTube
    "get_transcript",
    "get_video_info",
    "get_english_caption_for_video",
    # General
    "extract_video_id",
]

