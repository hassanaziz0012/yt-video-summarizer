"""
Database configuration and session management.

NOTE: Database is no longer needed since we use youtube-transcript-api
which doesn't require OAuth authentication or storing user information.
"""

# import os
# from pathlib import Path
# from dotenv import load_dotenv
# from sqlmodel import SQLModel, Session, create_engine

# if not os.getenv("POSTGRES_URL"):
#     load_dotenv()

# # Use PostgreSQL if POSTGRES_URL is set, otherwise fall back to SQLite
# POSTGRES_URL = os.getenv("POSTGRES_URL")

# # if POSTGRES_URL:
# DATABASE_URL = POSTGRES_URL
# engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
# # else:
# #     DATABASE_URL = f"sqlite:///{Path(__file__).parent.parent / 'database.db'}"
# #     engine = create_engine(DATABASE_URL, echo=False)


# def init_db() -> None:
#     """Initialize the database and create all tables."""
#     SQLModel.metadata.create_all(engine)


# def get_session() -> Session:
#     """Get a new database session."""
#     return Session(engine)
