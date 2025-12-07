# Sprawozdanie projektu Blind Puzzles

## Stos technologiczny
- **Backend**: aplikacja Flask z klasycznym routingiem w `app.py`, logika stron w module `routes`. Pobiera i renderuje dane przez Jinja2 oraz API JSON.
- **Bazy danych**: SQLite w dwóch plikach:
  - `Lichess_Puzzle.db` – baza z zadaniami z Lichess, tworzona z CSV w `blindchess_data.py` przy użyciu pandas i chunkowego importu.
  - `User_Puzzle.db` – baza użytkownika utrzymująca próby i rankingi, inicjalizowana w `userpuzzle_data.py` i uzupełniana w trakcie gry.
- **Szachy i dane**: biblioteka `python-chess` do pracy z PGN/FEN, `requests` do pobierania PGN z lichess.org. Stylowanie w `static/css`, interfejs HTML w `templates/`.

## Model danych i przepływ
- **Ładowanie puzzli**: `blindchess_data.py` tworzy tabelę `puzzles` z kolumnami m.in. `PuzzleId`, `FEN`, `Moves`, `Rating`, `GameUrl` i opcjonalnymi indeksami pod filtrację ratingu. Dane wstawiane są w partiach po 100k wierszy.
- **Struktura użytkownika**: `userpuzzle_data.py` buduje tabelę `user_puzzles` (próby z datą, czasem, wynikiem, liczbą blind moves i zmianą rankingu) oraz `user_variant_ratings` z domyślnym startem 500 punktów na wariant. Utrzymuje też tabelę `users` dla kompatybilności.
- **Dostęp do danych w runtime**:
  - `routes/puzzle_route.py` losuje zadanie z `puzzles` (SQL `ORDER BY RANDOM()`), filtruje już rozwiązane puzzle w danym wariancie, sprawdza próg ruchów z `GameUrl` i wylicza przewidywane P(user) względem bieżącego rankingu wariantu.
  - `routes/result_route.py` pobiera ranking wybranego puzzla, aktualizuje ranking wariantu przez `update_user_rating` oraz zapisuje wynik do `user_puzzles`.
  - `utils/db_helpers.py` zapewnia dostęp do rankingów wariantów, statystyk rozwiązanych zadań oraz historii prób (`get_user_attempts` dla widoku `/history`).

## Obszary do usprawnienia
- **Losowanie puzzli**: unikać `ORDER BY RANDOM()` na pełnej tabeli – losować po zakresie `PuzzleId` lub wstępnie filtrować w SQL (np. po `BlindMoves` i ratingu), by ograniczyć liczbę iteracji pętli.
- **Indeksowanie**: dodać indeksy na `puzzles(Rating)` i `puzzles(PuzzleId)` (jeśli nie istnieje) oraz na `user_puzzles(BlindMoves, PuzzleId)` dla szybszych zapytań o unikalność i statystyki.
- **Walidacja i spójność**: rozważyć klucze obce/ON DELETE CASCADE między `user_puzzles` a `puzzles`, migracje schematu zamiast ręcznego drop/create oraz walidację wejścia przy tworzeniu tabel (np. non-null dla daty/czasu).
- **Warstwa aplikacji**: wynieść stały `USER_ID = 1` do obsługi kont wielu użytkowników, dodać ograniczenie liczby pobieranych prób (`LIMIT`) konfigurowalne i paginację w historii, a także obsługę błędów sieciowych podczas pobierania PGN (cache?).
- **Testy i operacje wsadowe**: dodać testy jednostkowe/regresyjne dla logiki ratingów i selekcji puzzli oraz skrypty do bezpiecznej przebudowy baz (np. CLI do importu i backupu). 
