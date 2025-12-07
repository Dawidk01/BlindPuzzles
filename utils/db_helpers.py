"""Helpers for reading/writing user state in PostgreSQL."""
from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from sqlalchemy import text

from utils.db import engine

DEFAULT_START_RATING = 500
# Wyróżnione warianty w sekcji kafelków na stronie głównej.
PRIMARY_VARIANTS = [5, 10, 20]
# Variants we want to show in the dropdown by default.
BASE_VARIANT_CHOICES = list(range(0, 51))

ATTEMPT_FIELDS = (
    "puzzle_id",
    "solve_date",
    "solve_time",
    "result",
    "blind_moves",
    "old_rating",
    "new_rating",
    "rating_diff",
)


def _ensure_tables(conn) -> None:
    """Make sure the auxiliary tables required for the new variant system exist."""
    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS user_variant_ratings (
                user_id INTEGER NOT NULL,
                blind_moves INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                PRIMARY KEY (user_id, blind_moves)
            );
            """
        )
    )

    # Keep compatibility with the previous structure – create the users table if it
    # disappeared, but do not rely on it anywhere else.
    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                rating INTEGER
            );
            """
        )
    )

    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS user_puzzles (
                id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                PuzzleId TEXT,
                SolveDate TEXT,
                SolveTime REAL,
                Result INTEGER,
                BlindMoves INTEGER,
                OldUserRating INTEGER,
                NewUserRating INTEGER,
                ChangeOfRating INTEGER
            );
            """
        )
    )


def get_user_variant_rating(user_id: int, blind_moves: int) -> int:
    """Return the rating for a given user/variant, creating a default entry when missing."""
    if blind_moves is None:
        blind_moves = 0

    with engine.begin() as conn:
        _ensure_tables(conn)
        conn.execute(
            text(
                """
                INSERT INTO user_variant_ratings (user_id, blind_moves, rating)
                VALUES (:user_id, :blind_moves, :rating)
                ON CONFLICT (user_id, blind_moves) DO NOTHING
                """
            ),
            {"user_id": user_id, "blind_moves": blind_moves, "rating": DEFAULT_START_RATING},
        )

        row = conn.execute(
            text(
                "SELECT rating FROM user_variant_ratings WHERE user_id = :user_id AND blind_moves = :blind_moves"
            ),
            {"user_id": user_id, "blind_moves": blind_moves},
        ).fetchone()

    return row[0] if row else DEFAULT_START_RATING


def set_user_variant_rating(user_id: int, blind_moves: int, rating: int) -> None:
    """Persist a rating for the selected variant."""
    if blind_moves is None:
        blind_moves = 0

    with engine.begin() as conn:
        _ensure_tables(conn)
        conn.execute(
            text(
                """
                INSERT INTO user_variant_ratings (user_id, blind_moves, rating)
                VALUES (:user_id, :blind_moves, :rating)
                ON CONFLICT(user_id, blind_moves) DO UPDATE SET rating = excluded.rating
                """
            ),
            {"user_id": user_id, "blind_moves": blind_moves, "rating": rating},
        )


def get_variant_statistics(
    user_id: int,
    base_variants: Iterable[int] | None = None,
) -> Dict[int, Dict[str, int]]:
    """Gather rating and puzzle statistics for every requested variant."""
    considered_variants = set(base_variants or [])

    with engine.begin() as conn:
        _ensure_tables(conn)

        for variant in considered_variants:
            conn.execute(
                text(
                    """
                    INSERT INTO user_variant_ratings (user_id, blind_moves, rating)
                    VALUES (:user_id, :blind_moves, :rating)
                    ON CONFLICT (user_id, blind_moves) DO NOTHING
                    """
                ),
                {"user_id": user_id, "blind_moves": variant, "rating": DEFAULT_START_RATING},
            )

        rating_rows = conn.execute(
            text("SELECT blind_moves, rating FROM user_variant_ratings WHERE user_id = :user_id"),
            {"user_id": user_id},
        ).fetchall()
        rating_map = {int(blind_moves): rating for blind_moves, rating in rating_rows}
        considered_variants.update(rating_map.keys())

        solved_rows = conn.execute(
            text(
                """
                SELECT COALESCE(BlindMoves, 0) AS BlindMoves,
                       COUNT(DISTINCT PuzzleId) AS solved_unique,
                       COUNT(*) AS total_attempts
                FROM user_puzzles
                GROUP BY COALESCE(BlindMoves, 0)
                """
            )
        ).fetchall()
        solved_map: Dict[int, Tuple[int, int]] = {
            int(blind_moves): (int(unique_count), int(total_attempts))
            for blind_moves, unique_count, total_attempts in solved_rows
        }
        considered_variants.update(solved_map.keys())

    statistics: Dict[int, Dict[str, int]] = {}
    for variant in considered_variants:
        unique_solved, total_attempts = solved_map.get(variant, (0, 0))
        statistics[variant] = {
            "blind_moves": variant,
            "rating": rating_map.get(variant, DEFAULT_START_RATING),
            "unique_solved": unique_solved,
            "total_attempts": total_attempts,
        }

    return statistics


def get_user_attempts(limit: int | None = 500) -> List[Dict[str, object]]:
    """Pobiera historię prób użytkownika w formie listy słowników."""
    with engine.begin() as conn:
        _ensure_tables(conn)
        base_query = (
            """
            SELECT PuzzleId, SolveDate, SolveTime, Result, COALESCE(BlindMoves, 0) AS BlindMoves,
                   OldUserRating, NewUserRating, ChangeOfRating
            FROM user_puzzles
            ORDER BY COALESCE(NULLIF(SolveDate, '')::timestamp, '1970-01-01 00:00:00'::timestamp) DESC, id DESC
            """
        )
        if limit is not None:
            base_query += "\n            LIMIT :limit"
            rows = conn.execute(text(base_query), {"limit": limit}).fetchall()
        else:
            rows = conn.execute(text(base_query)).fetchall()

    attempts: List[Dict[str, object]] = []
    for row in rows:
        record = dict(zip(ATTEMPT_FIELDS, row))
        # Ujednolicenie typów i zabezpieczenie przed wartościami None.
        record["blind_moves"] = int(record.get("blind_moves") or 0)
        record["result"] = int(record.get("result") or 0)
        attempts.append(record)

    return attempts
