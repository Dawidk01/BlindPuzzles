"""Central database engine configured from ``DATABASE_URL``.

This module exposes a shared SQLAlchemy engine that other helpers/routes can
reuse to talk to the PostgreSQL instance provided via the environment. The
project assumes ``DATABASE_URL`` is always defined; this keeps the code free of
hard-coded SQLite file paths and matches Render's deployment model.
"""

from __future__ import annotations

import os
from sqlalchemy import create_engine


DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Provide a PostgreSQL connection string to run the app."
    )


# A single engine shared across the application; SQLAlchemy handles pooling.
engine = create_engine(DATABASE_URL, future=True)

