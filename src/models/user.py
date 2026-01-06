"""
User model for storing OAuth user data.

NOTE: This model is no longer needed since we use youtube-transcript-api
which doesn't require OAuth authentication.
"""

# from sqlmodel import Field, SQLModel


# class User(SQLModel, table=True):
#     """User model storing OAuth credentials and profile info."""

#     id: int | None = Field(default=None, primary_key=True)
#     name: str
#     email: str = Field(unique=True, index=True)
#     token: str
#     refresh_token: str | None = None
