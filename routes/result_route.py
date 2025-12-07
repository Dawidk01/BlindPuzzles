# routes/result_route.py

from flask import jsonify, request
from rating_diff import update_user_rating

from utils.db_helpers import get_user_variant_rating, set_user_variant_rating
from utils.db import engine
from sqlalchemy import text


USER_ID = 1

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
    with engine.connect() as conn:
        puzzle_row = conn.execute(
            text("SELECT Rating FROM puzzles WHERE PuzzleId = :puzzle_id"),
            {"puzzle_id": puzzle_id},
        ).fetchone()

    if puzzle_row:
        puzzle_rank = puzzle_row[0]
    else:
        puzzle_rank = 1000  # domyślny ranking, jeśli nie znaleziono puzzla

    # Dodaj domyślną wartość, jeśli blind_moves jest None
    if blind_moves is None:
        blind_moves = 0
    try:
        blind_moves = int(blind_moves)
    except (TypeError, ValueError):
        blind_moves = 0

    try:
        result_value = int(result)
    except (TypeError, ValueError):
        result_value = 0
    result = result_value

    won = (result == 1)
    old_rating = get_user_variant_rating(USER_ID, blind_moves)
    new_rating, change_of_rating = update_user_rating(
        old_rating, puzzle_rank, won
    )
    set_user_variant_rating(USER_ID, blind_moves, new_rating)

    # Zapisz dane do bazy user_puzzles
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO user_puzzles
                (PuzzleId, SolveDate, SolveTime, Result, BlindMoves, OldUserRating, NewUserRating, ChangeOfRating)
                VALUES (:puzzle_id, :solve_date, :solve_time, :result, :blind_moves, :old_rating, :new_rating, :change_of_rating)
            """
            ),
            {
                "puzzle_id": puzzle_id,
                "solve_date": solve_date,
                "solve_time": solve_time,
                "result": result,
                "blind_moves": blind_moves,
                "old_rating": old_rating,
                "new_rating": new_rating,
                "change_of_rating": change_of_rating,
            },
        )

    return jsonify({
        'status': 'success',
        'new_rating': new_rating,
        'change': change_of_rating
    })
