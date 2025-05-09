import sqlite3
import pandas as pd

# 1. Łączymy się (lub tworzymy) bazę SQLite
conn = sqlite3.connect("Lichess_Puzzle.db")
cursor = conn.cursor()

# 2. Usunięcie tabeli, jeśli istnieje (opcjonalne, jeśli chcesz mieć "świeżą" tabelę)
cursor.execute("DROP TABLE IF EXISTS puzzles;")

# 3. Tworzymy tabelę z kolumnami odpowiadającymi CSV
#    - PuzzleId jako PRIMARY KEY (zakładamy, że jest unikalny)
cursor.execute("""
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
""")
conn.commit()

# 4. Wczytanie pliku CSV w partiach i zapisywanie do SQL
chunksize = 100_000  # można dostosować do ilości RAM i wydajności
csv_file = "lichess_db_puzzle.csv"

reader = pd.read_csv(csv_file, chunksize=chunksize)

for i, chunk in enumerate(reader):
    # if_exists='append' – dopisujemy do istniejącej już tabeli
    chunk.to_sql("puzzles", conn, if_exists="append", index=False)
    print(f"Przetworzono chunk nr {i+1}")

# 5. (Opcjonalnie) można dodatkowo założyć indeksy na inne kolumny
#    np. jeśli często filtrowana jest kolumna Rating:
# cursor.execute("CREATE INDEX IF NOT EXISTS idx_rating ON puzzles (Rating);")
# conn.commit()

# 6. Zamknięcie połączenia
conn.close()