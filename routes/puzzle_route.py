# routes/puzzle_route.py

import io
import requests
import chess.pgn
import sqlite3
from flask import redirect, render_template, request, url_for

from utils.db_helpers import get_user_variant_rating


USER_ID = 1


def puzzle():
    """Losuje puzzle dla wariantu o zadanej liczbie ruchów w ciemno."""
    if request.method == 'POST':
        blind_moves_raw = request.form.get('blind_moves', 0)
    else:
        if 'blind_moves' not in request.args:
            return redirect(url_for('home'))
        blind_moves_raw = request.args.get('blind_moves', 0)

    try:
        blind_moves = max(0, int(blind_moves_raw))
    except (TypeError, ValueError):
        return redirect(url_for('home'))

    user_rating = get_user_variant_rating(USER_ID, blind_moves)

    # Pobierz userpuzzles
    conn = sqlite3.connect("User_Puzzle.db")
    cursor = conn.cursor()

    # Zapytanie o puzzle rozwiązane w ramach tego wariantu
    cursor.execute(
        "SELECT PuzzleID FROM user_puzzles WHERE COALESCE(BlindMoves, 0) = ?;",
        (blind_moves,)
    )
    puzzleid_rows = cursor.fetchall()  # to jest lista krotek
    puzzleid = [row[0] for row in puzzleid_rows]
    conn.close()


    # Połącz się z bazą i wylosuj puzzle
    P_user = 0
    loop_count = 0

    conn = sqlite3.connect("Lichess_Puzzle.db")
    cursor = conn.cursor()

    while P_user < 0.02 or P_user > 0.98 :    
        loop_count += 1

        cursor.execute("SELECT * FROM puzzles ORDER BY RANDOM() LIMIT 1;")
        puzzle = cursor.fetchone()
        if puzzle[3]:
            PuzzleRating = puzzle[3]
        else:
            PuzzleRating = 1000
        X = round(PuzzleRating)
        P_user = 1/(1+10**((X-user_rating)/800))
        # Sprawdzenie warunku puzzla ID
        if puzzle[0] in puzzleid:
            P_user = 0
        game_url = puzzle[8]
        halfmove_str = game_url.split('#')[-1]
        halfmove_target = int(halfmove_str)

        if halfmove_target < blind_moves:
            # Za mało ruchów, puzzle się nie nadaje; odrzuć i losuj kolejny
            P_user = 0


    conn.close()
    print(f"Pętla wykonała się {loop_count} razy.")

    # puzzle ma strukturę: (PuzzleId, Fen, Moves, Rating, ...)
    game_url = puzzle[8]  
    solution_str = puzzle[2]
    PuzzleId = puzzle[0]
    solutionMoves = solution_str.split()

    # 2) ...
    game_id = game_url.split("lichess.org/")[1].split("/")[0]
    halfmove_str = game_url.split('#')[-1]
    halfmove_target = int(halfmove_str)

    # 3) ...
    halfmove_start = max(0, halfmove_target - blind_moves)

    # 4) ...
    pgn_url = f"https://lichess.org/game/export/{game_id}.pgn"
    try:
        response = requests.get(pgn_url)
        pgn_text = response.text
    except Exception as e:
        return f"Błąd pobierania PGN: {e}"

    # 5) ...
    pgn_io = io.StringIO(pgn_text)
    game = chess.pgn.read_game(pgn_io)
    board = game.board()

    # 6) ...
    moves_list = list(game.mainline_moves())

    # 7) ...
    for i in range(halfmove_start):
        board.push(moves_list[i])
    fen_start = board.fen()

    # 8) ...
    blind_moves_list = moves_list[halfmove_start:halfmove_target]
    temp_board = board.copy()
    blind_moves_san = []
    for mv in blind_moves_list:
        blind_moves_san.append(temp_board.san(mv))
        temp_board.push(mv)

    puzzle_fen = temp_board.fen()

    # 9) Renderujemy index.html
    return render_template(
        'index.html',
        fen=fen_start,
        puzzle_fen=puzzle_fen,
        blind_moves_list=blind_moves_san,
        blind_moves=blind_moves,
        game_url=game_url,
        PuzzleId=PuzzleId,
        solutionMoves=solutionMoves,
        halfmove_start=halfmove_start,
        halfmove_target=halfmove_target,
        P_user=P_user,
        X = X,
        user_rating=user_rating
    )
