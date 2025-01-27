# routes/result_route.py

import sqlite3
from flask import request, jsonify
from rating_diff import update_user_rating

def submit_result():
    try:
        data = request.get_json()
        print("Odebrane dane:", data)
        puzzle_id = data.get('PuzzleId')
        solve_date = data.get('SolveDate')
        solve_time = data.get('SolveTime')
        result = data.get('Result')
        blind_moves = data.get('BlindMoves')
    except Exception as e:
        print("Wystąpił błąd:", e)
        return jsonify({'status': 'error', 'message': str(e)}), 500

    # Pobierz ranking zadania z bazy puzzles
    puzzle_conn = sqlite3.connect("Lichess_Puzzle.db")
    puzzle_cursor = puzzle_conn.cursor()
    puzzle_cursor.execute("SELECT Rating FROM puzzles WHERE PuzzleId = ?", (puzzle_id,))
    puzzle_row = puzzle_cursor.fetchone()
    puzzle_conn.close()

    user_id = 1  
    user_conn = sqlite3.connect("User_Puzzle.db")
    user_cursor = user_conn.cursor()
    user_cursor.execute("SELECT rating FROM users WHERE id = ?", (user_id,))
    user_row = user_cursor.fetchone()

    if user_row:
        old_rating = user_row[0]
    else:
        old_rating = 100  # domyślnie, jeśli nie znaleziono

    if puzzle_row:
        puzzle_rank = puzzle_row[0]
    else:
        puzzle_rank = 1000  # domyślny ranking, jeśli nie znaleziono puzzla

    # Dodaj domyślną wartość, jeśli blind_moves jest None
    if blind_moves is None:
        blind_moves = 0

    won = (result == 1)
    new_rating, change_of_rating = update_user_rating(old_rating, puzzle_rank, blind_moves, won)
    user_cursor.execute("UPDATE users SET rating = ? WHERE id = ?", (new_rating, user_id))
    user_conn.commit()
    user_conn.close()

    # Zapisz dane do bazy user_puzzles
    conn = sqlite3.connect("User_Puzzle.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_puzzles 
        (PuzzleId, SolveDate, SolveTime, Result, BlindMoves, OldUserRating, NewUserRating, ChangeOfRating)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (puzzle_id, solve_date, solve_time, result, blind_moves, old_rating, new_rating, change_of_rating))
    conn.commit()
    conn.close()

    return jsonify({
        'status': 'success',
        'new_rating': new_rating,
        'change': change_of_rating
    })
