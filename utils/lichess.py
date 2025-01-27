import requests
import chess.pgn
import io

def get_pgn_data(puzzle, blind_moves):
    game_url = puzzle[8]
    game_id = game_url.split("lichess.org/")[1].split("/")[0]
    halfmove_target = int(game_url.split('#')[-1])
    halfmove_start = max(0, halfmove_target - blind_moves)

    pgn_url = f"https://lichess.org/game/export/{game_id}.pgn"
    response = requests.get(pgn_url)
    pgn_text = response.text

    pgn_io = io.StringIO(pgn_text)
    game = chess.pgn.read_game(pgn_io)
    board = game.board()
    moves_list = list(game.mainline_moves())

    for i in range(halfmove_start):
        board.push(moves_list[i])

    fen_start = board.fen()
    blind_moves_list = moves_list[halfmove_start:halfmove_target]

    temp_board = board.copy()
    blind_moves_san = [temp_board.san(mv) for mv in blind_moves_list]

    return fen_start, blind_moves_san, temp_board.fen()
