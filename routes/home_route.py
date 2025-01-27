# routes/home_route.py

def home():
    """Strona główna: link do nowej zagadki."""
    return """
    <h1>Witaj w BlindPuzzles!</h1>
    <p><a href='/puzzle'>New Puzzle</a></p>
    """
