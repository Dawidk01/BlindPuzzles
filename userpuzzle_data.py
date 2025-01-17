import sqlite3

conn = sqlite3.connect("User_Puzzle.db")
cursor = conn.cursor()

# Usunięcie starej tabeli (opcjonalne - jeśli chcesz 'czystą' tabelę za każdym razem)
cursor.execute("DROP TABLE IF EXISTS user_puzzles;")

# Stworzenie nowej tabeli user_puzzles
# W tym przykładzie klucz główny to autoincrement (ID).
# Dzięki temu możemy mieć wiele wpisów dla tego samego PuzzleId.
cursor.execute("""
    CREATE TABLE user_puzzles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        PuzzleId TEXT,
        SolveDate TEXT,
        SolveTime REAL,
        Result INTEGER,
        BlindMoves INTEGER,
        OldUserRating INTEGER,
        NewUserRating INTEGER,
        ChangeOfRating INTEGER,
        FOREIGN KEY(PuzzleId) REFERENCES puzzles(PuzzleId)
    );
""")
print("Tabela 'users_puzzle' została utworzona.")

cursor.execute("DROP TABLE IF EXISTS users;")


cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    rating INTEGER
);
""")

# Dodaj użytkownika z domyślnym rankingiem 100, jeżeli nie istnieje
cursor.execute("""
INSERT OR IGNORE INTO users (id, rating) VALUES (1, 100);
""")

conn.commit()
conn.close()
print("Tabela 'users' została utworzona.")
