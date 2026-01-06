"""
Google OAuth 2.0 authentication utility functions.
"""

import json
from pathlib import Path

import httpx
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from sqlmodel import select

from db import get_session
from models.user import User

# OAuth configuration
SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]
REDIRECT_URI = "http://localhost:8000/auth/google-oauth-callback"

# File paths (relative to project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent
CLIENT_SECRETS_FILE = PROJECT_ROOT / "client.json"


def load_client_config() -> dict:
    """
    Load OAuth client configuration from client.json.

    Returns:
        The client configuration dictionary.

    Raises:
        FileNotFoundError: If client.json doesn't exist.
    """
    if not CLIENT_SECRETS_FILE.exists():
        raise FileNotFoundError(f"Client secrets file not found: {CLIENT_SECRETS_FILE}")

    with open(CLIENT_SECRETS_FILE) as f:
        return json.load(f)


def get_oauth_authorization_url() -> tuple[str, str]:
    """
    Generate the OAuth authorization URL for user consent.

    Returns:
        A tuple of (authorization_url, state) for the OAuth flow.
    """
    flow = Flow.from_client_secrets_file(
        str(CLIENT_SECRETS_FILE), scopes=SCOPES, redirect_uri=REDIRECT_URI
    )

    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )

    return authorization_url, state


def get_user_info(access_token: str) -> dict:
    """
    Fetch user profile info from Google using the access token.

    Args:
        access_token: The OAuth access token.

    Returns:
        Dictionary with user info (name, email).
    """
    response = httpx.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response.raise_for_status()
    return response.json()


def exchange_code_for_tokens(code: str) -> User:
    """
    Exchange the authorization code for tokens and save user to database.

    Args:
        code: The authorization code from the OAuth callback.

    Returns:
        The created or updated User object.
    """
    flow = Flow.from_client_secrets_file(
        str(CLIENT_SECRETS_FILE), scopes=SCOPES, redirect_uri=REDIRECT_URI
    )

    flow.fetch_token(code=code)
    credentials = flow.credentials

    # Fetch user info from Google
    user_info = get_user_info(credentials.token)

    with get_session() as session:
        # Check if user already exists
        statement = select(User).where(User.email == user_info["email"])
        existing_user = session.exec(statement).first()

        if existing_user:
            # Update existing user's tokens
            existing_user.token = credentials.token
            existing_user.refresh_token = credentials.refresh_token
            existing_user.name = user_info.get("name", existing_user.name)
            session.add(existing_user)
            session.commit()
            session.refresh(existing_user)
            return existing_user
        else:
            # Create new user
            user = User(
                name=user_info.get("name", ""),
                email=user_info["email"],
                token=credentials.token,
                refresh_token=credentials.refresh_token,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user


def get_user_by_id(user_id: int) -> User | None:
    """
    Get a user from the database by their ID.

    Args:
        user_id: The database ID of the user.

    Returns:
        The User object if found, otherwise None.
    """
    with get_session() as session:
        statement = select(User).where(User.id == user_id)
        return session.exec(statement).first()


def get_authenticated_credentials(user_email: str | None = None) -> Credentials | None:
    """
    Get valid OAuth credentials for a user, refreshing if needed.

    Args:
        user_email: The email of the user to get credentials for.
                   If None, gets the first user in the database.

    Returns:
        Valid Credentials object, or None if not authenticated.
    """
    # Load client config for token refresh
    client_config = load_client_config()
    web_config = client_config.get("web", {})

    with get_session() as session:
        if user_email:
            statement = select(User).where(User.email == user_email)
            user = session.exec(statement).first()
        else:
            # Get first user if no email specified
            statement = select(User)
            user = session.exec(statement).first()

        if not user:
            return None

        credentials = Credentials(
            token=user.token,
            refresh_token=user.refresh_token,
            token_uri=web_config.get(
                "token_uri", "https://oauth2.googleapis.com/token"
            ),
            client_id=web_config.get("client_id"),
            client_secret=web_config.get("client_secret"),
            scopes=SCOPES,
        )

        # If credentials are expired and we have a refresh token, refresh them
        if credentials.expired and credentials.refresh_token:
            from google.auth.transport.requests import Request

            credentials.refresh(Request())

            # Update user's token in database
            user.token = credentials.token
            session.add(user)
            session.commit()

        return credentials
