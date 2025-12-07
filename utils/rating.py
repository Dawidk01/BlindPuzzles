def update_user_rating(user_rank, puzzle_rank, won):
    """Aktualizuj ranking na podstawie czystego rankingu lichess puzzla."""
    X = puzzle_rank

    # Oblicz różnicę R
    R = abs(user_rank - X) / 100 + 25

    # Oblicz prawdopodobieństwa
    total = user_rank + X
    P_user = user_rank / total
    P_task = X / total

    # Zapamiętaj starą wartość rankingu, by obliczyć zmianę
    old_user_rank = user_rank

    # Aktualizuj ranking na podstawie wyniku
    if won:
        user_rank += R * P_task
    else:
        user_rank -= R * P_user

    # Zaokrąglij nowy ranking do najbliższej liczby całkowitej
    new_user_rank = round(user_rank)

    # Oblicz i zaokrąglij zmianę rankingu
    change = round(new_user_rank - old_user_rank)

    return new_user_rank, change

# Przykładowe użycie:
#if __name__ == "__main__":
 #   initial_user_rank = 100
  #  puzzle_rank = 850
   # blind_moves = 10

    # Przykład: użytkownik wygrał zadanie
   # new_rank, change = update_user_rating(initial_user_rank, puzzle_rank, blind_moves, won=True)
    #print("Nowy ranking po wygranej:", new_rank)
    #print("Zmiana rankingu:", change)

    # Przykład: użytkownik przegrał zadanie
    #new_rank, change = update_user_rating(initial_user_rank, puzzle_rank, blind_moves, won=False)
    #print("Nowy ranking po przegranej:", new_rank)
    #print("Zmiana rankingu:", change)
