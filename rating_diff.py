def update_user_rating(user_rank, puzzle_rank, blind_moves, won):
    # Oblicz efektywny ranking zadania X
    X = puzzle_rank + 100 * blind_moves

    # Oblicz prawdopodobieństwa
    P_user = 1/(1+10**((X-user_rank)/800)) 


    # Zapamiętaj starą wartość rankingu, by obliczyć zmianę
    old_user_rank = user_rank

    # Aktualizuj ranking na podstawie wyniku
    if won:
        user_rank += 24*(1-P_user)
    else:
        user_rank += 32*(0-P_user)

    # Zaokrąglij nowy ranking do najbliższej liczby całkowitej
    new_user_rank = round(user_rank)

    # Oblicz i zaokrąglij zmianę rankingu
    change = round(new_user_rank - old_user_rank)

    return new_user_rank, change
