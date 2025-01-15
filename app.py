import io
import requests
import chess.pgn
import sqlite3

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    """Strona główna: link do nowej zagadki."""
    return """
    <h1>Witaj w BlindPuzzles!</h1>
    <p><a href='/puzzle'>New Puzzle</a></p>
    """

@app.route('/puzzle', methods=['GET', 'POST'])
def puzzle():
    """Formularz: liczba ruchów w ciemno (POST); potem losujemy puzzle i pokazujemy wynik."""
    if request.method == 'GET':
        # Zwracamy prosty formularz
        return """
        <h2>Podaj liczbę półruchów w ciemno</h2>
        <form action="/puzzle" method="POST">
          <label for="blind_moves">Blind moves:</label>
          <input type="number" name="blind_moves" min="0" required>
          <button type="submit">Wyślij</button>
        </form>
        """

    # Gdy POST, przetwarzamy liczbę "ruchów w ciemno"
    blind_moves = int(request.form.get('blind_moves', 0))

    # 1) Połącz się z bazą i wylosuj puzzle
    conn = sqlite3.connect("Lichess_Puzzle.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM puzzles ORDER BY RANDOM() LIMIT 1;")
    puzzle = cursor.fetchone()
    conn.close()

    # Zakładamy, że puzzle ma strukturę:
    # (PuzzleId, Fen, Moves, Rating, RatingDeviation, Popularity, NbPlays, Themes, GameUrl, OpeningTags)
    # Interesuje nas głównie puzzle[1] = fen, puzzle[2] = moves, puzzle[8] = game_url.
    game_url = puzzle[8]  # np. 'https://lichess.org/2clM1WU0/black#54'

    # 2) Parsujemy ID partii i numer docelowego półruchu (np. #54)
    #    a) ID partii:
    game_id = game_url.split("lichess.org/")[1].split("/")[0]  # '2clM1WU0'
    #    b) Numer halfmove_target:
    halfmove_str = game_url.split('#')[-1]  # '54'
    halfmove_target = int(halfmove_str)     # 54

    # 3) Obliczamy, do którego półruchu się cofamy
    #    (jeśli blind_moves = 4, to cofamy się do 54 - 4 = 50)
    halfmove_start = max(0, halfmove_target - blind_moves)

    # 4) Pobierz cały PGN partii z Lichess
    pgn_url = f"https://lichess.org/game/export/{game_id}.pgn"
    try:
        response = requests.get(pgn_url)
        pgn_text = response.text
    except Exception as e:
        # Możesz obsłużyć błąd inaczej, tu tylko przykładowo
        return f"Błąd pobierania PGN: {e}"

    # 5) Wczytujemy PGN do python-chess
    pgn_io = io.StringIO(pgn_text)
    game = chess.pgn.read_game(pgn_io)
    board = game.board()

    # 6) Tworzymy listę wszystkich półruchów w partii
    moves_list = list(game.mainline_moves())  # np. 90 halfmove'ów

    # 7) Przesuwamy szachownicę do stanu #halfmove_start
    for i in range(halfmove_start):
        board.push(moves_list[i])  # odtwarzamy ruchy jeden po drugim

    # Teraz 'board' to pozycja cofnięta
    fen_start = board.fen()

    # 8) Wyodrębniamy ruchy w ciemno: od halfmove_start do halfmove_target - 1
    blind_moves_list = moves_list[halfmove_start:halfmove_target]

    # Konwertujemy je do notacji SAN (zrozumiałej dla człowieka)
    temp_board = board.copy()
    blind_moves_san = []
    for mv in blind_moves_list:
        blind_moves_san.append(temp_board.san(mv))
        temp_board.push(mv)

    # Po tym pętleniu 'temp_board' = pozycja #halfmove_target
    puzzle_fen = temp_board.fen()

    # 9) Renderujemy index.html, przekazując wszystkie potrzebne parametry
    return render_template(
        'index.html',
        fen=fen_start,                 # Pozycja, w której zaczyna gracz
        puzzle_fen=puzzle_fen,         # Oryginalna pozycja #target
        blind_moves_list=blind_moves_san,
        game_url=game_url,
        halfmove_start=halfmove_start,
        halfmove_target=halfmove_target
    )

if __name__ == '__main__':
    app.run(debug=True)
