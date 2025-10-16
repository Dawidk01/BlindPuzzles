"""Utilities for managing user-specific variant data."""
from __future__ import annotations

import sqlite3
from typing import Dict, Iterable, Tuple

USER_DB_PATH = "User_Puzzle.db"
DEFAULT_START_RATING = 100
PRIMARY_VARIANTS = [2, 5, 10, 20, 40]
# Variants we want to show in the dropdown by default.
BASE_VARIANT_CHOICES = list(range(0, 51))


def _ensure_tables(cursor: sqlite3.Cursor) -> None:
    """Make sure the auxiliary tables required for the new variant system exist."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_variant_ratings (
            user_id INTEGER NOT NULL,
            blind_moves INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            PRIMARY KEY (user_id, blind_moves)
        );
        """
    )

    # Keep compatibility with the previous structure – create the users table if it
    # disappeared, but do not rely on it anywhere else.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            rating INTEGER
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_puzzles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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


def get_user_variant_rating(user_id: int, blind_moves: int) -> int:
    """Return the rating for a given user/variant, creating a default entry when missing."""
    if blind_moves is None:
        blind_moves = 0

    with sqlite3.connect(USER_DB_PATH) as conn:
        cursor = conn.cursor()
        _ensure_tables(cursor)
        cursor.execute(
            """
            INSERT OR IGNORE INTO user_variant_ratings (user_id, blind_moves, rating)
            VALUES (?, ?, ?)
            """,
            (user_id, blind_moves, DEFAULT_START_RATING),
        )
        conn.commit()

        cursor.execute(
            "SELECT rating FROM user_variant_ratings WHERE user_id = ? AND blind_moves = ?",
            (user_id, blind_moves),
        )
        row = cursor.fetchone()

    return row[0] if row else DEFAULT_START_RATING


def set_user_variant_rating(user_id: int, blind_moves: int, rating: int) -> None:
    """Persist a rating for the selected variant."""
    if blind_moves is None:
        blind_moves = 0

    with sqlite3.connect(USER_DB_PATH) as conn:
        cursor = conn.cursor()
        _ensure_tables(cursor)
        cursor.execute(
            """
            INSERT INTO user_variant_ratings (user_id, blind_moves, rating)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, blind_moves) DO UPDATE SET rating = excluded.rating
            """,
            (user_id, blind_moves, rating),
        )
        conn.commit()


def get_variant_statistics(
    user_id: int,
    base_variants: Iterable[int] | None = None,
) -> Dict[int, Dict[str, int]]:
    """Gather rating and puzzle statistics for every requested variant."""
    considered_variants = set(base_variants or [])

    with sqlite3.connect(USER_DB_PATH) as conn:
        cursor = conn.cursor()
        _ensure_tables(cursor)

        for variant in considered_variants:
            cursor.execute(
                """
                INSERT OR IGNORE INTO user_variant_ratings (user_id, blind_moves, rating)
                VALUES (?, ?, ?)
                """,
                (user_id, variant, DEFAULT_START_RATING),
            )

        cursor.execute(
            "SELECT blind_moves, rating FROM user_variant_ratings WHERE user_id = ?",
            (user_id,),
        )
        rating_rows = cursor.fetchall()
        rating_map = {int(blind_moves): rating for blind_moves, rating in rating_rows}
        considered_variants.update(rating_map.keys())

        cursor.execute(
            """
            SELECT COALESCE(BlindMoves, 0) AS BlindMoves,
                   COUNT(DISTINCT PuzzleId) AS solved_unique,
                   COUNT(*) AS total_attempts
            FROM user_puzzles
            GROUP BY COALESCE(BlindMoves, 0)
            """
        )
        solved_rows = cursor.fetchall()
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
