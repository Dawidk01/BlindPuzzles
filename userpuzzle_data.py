"""Initialize user-facing tables in PostgreSQL."""

from __future__ import annotations

from sqlalchemy import text

from utils.db import engine

DEFAULT_START_RATING = 500


def main():
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS user_puzzles;"))
        conn.execute(text("DROP TABLE IF EXISTS users;"))
        conn.execute(text("DROP TABLE IF EXISTS user_variant_ratings;"))

        conn.execute(
            text(
                """
                CREATE TABLE user_puzzles (
                    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    PuzzleId TEXT,
                    SolveDate TEXT,
                    SolveTime REAL,
                    Result INTEGER,
                    BlindMoves INTEGER,
                    OldUserRating INTEGER,
                    NewUserRating INTEGER,
                    ChangeOfRating INTEGER,
                    FOREIGN KEY (PuzzleId) REFERENCES puzzles(PuzzleId)
                );
                """
            )
        )

        conn.execute(
            text(
                """
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    rating INTEGER
                );
                """
            )
        )

        conn.execute(
            text(
                """
                CREATE TABLE user_variant_ratings (
                    user_id INTEGER NOT NULL,
                    blind_moves INTEGER NOT NULL,
                    rating INTEGER NOT NULL,
                    PRIMARY KEY (user_id, blind_moves)
                );
                """
            )
        )

        conn.execute(
            text("INSERT INTO users (id, rating) VALUES (1, :rating) ON CONFLICT DO NOTHING"),
            {"rating": DEFAULT_START_RATING},
        )

        conn.executemany(
            text(
                """
                INSERT INTO user_variant_ratings (user_id, blind_moves, rating)
                VALUES (:user_id, :blind_moves, :rating)
                ON CONFLICT (user_id, blind_moves) DO NOTHING
                """
            ),
            [
                {"user_id": 1, "blind_moves": variant, "rating": DEFAULT_START_RATING}
                for variant in [0, 5, 10, 20, 40]
            ],
        )

    print("Tabele użytkownika zostały utworzone.")


if __name__ == "__main__":
    main()

