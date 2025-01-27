# routes/puzzle_route.py

import io
import requests
import chess.pgn
import sqlite3
from flask import render_template, request

def puzzle():
    user_id = 1  
    user_conn = sqlite3.connect("User_Puzzle.db")
    user_cursor = user_conn.cursor()
    user_cursor.execute("SELECT rating FROM users WHERE id = ?", (user_id,))
    user_row = user_cursor.fetchone()

    if user_row:
        user_rating = user_row[0]
    else:
        user_rating = 100  # domyślnie, jeśli nie znaleziono


    """Formularz: liczba ruchów w ciemno (POST); potem losujemy puzzle i pokazujemy wynik."""
    if request.method == 'GET':
        # Zwracamy Twój istniejący szablon form.html
        return render_template("form.html")

    # Gdy POST, przetwarzamy liczbę "ruchów w ciemno"
    blind_moves = int(request.form.get('blind_moves', 0))

    # 1) Połącz się z bazą i wylosuj puzzle
    P_user = 0
    conn = sqlite3.connect("Lichess_Puzzle.db")
    cursor = conn.cursor()

    while P_user <0.01 :    
        cursor.execute("SELECT * FROM puzzles ORDER BY RANDOM() LIMIT 1;")
        puzzle = cursor.fetchone()
        if puzzle[3]:
            PuzzleRating = puzzle[3]
        else:
            PuzzleRating = 1000
        X = PuzzleRating + 100 * blind_moves
        P_user = 1/(1+10**((X-user_rating)/800)) 

    conn.close()

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
        PuzzleRating = PuzzleRating,
        user_rating=user_rating
    )
