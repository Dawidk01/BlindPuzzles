"""Seed the `puzzles` table from the Lichess CSV using PostgreSQL."""

from __future__ import annotations

import os
import pandas as pd
from sqlalchemy import text

from utils.db import engine


CSV_FILE = os.environ.get("PUZZLE_CSV", "lichess_db_puzzle.csv")


def main():
    # 1. Drop and recreate the target table.
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS puzzles;"))
        conn.execute(
            text(
                """
                CREATE TABLE puzzles (
                    PuzzleId TEXT PRIMARY KEY,
                    FEN TEXT,
                    Moves TEXT,
                    Rating INTEGER,
                    RatingDeviation INTEGER,
                    Popularity INTEGER,
                    NbPlays INTEGER,
                    Themes TEXT,
                    GameUrl TEXT,
                    OpeningTags TEXT
                );
                """
            )
        )

    # 2. Load the CSV in chunks and append to the database.
    chunksize = 100_000
    reader = pd.read_csv(CSV_FILE, chunksize=chunksize)

    for i, chunk in enumerate(reader):
        chunk.to_sql("puzzles", engine, if_exists="append", index=False)
        print(f"Przetworzono chunk nr {i+1}")

    print("Import puzzles zakończony.")


if __name__ == "__main__":
    main()

