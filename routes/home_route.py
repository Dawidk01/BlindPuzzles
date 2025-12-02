# routes/home_route.py

from flask import render_template

from utils.db_helpers import (
    BASE_VARIANT_CHOICES,
    PRIMARY_VARIANTS,
    get_variant_statistics,
)


USER_ID = 1


def _format_variant_payload(variant_data):
    """Normalize stats dictionaries so templates can rely on the same keys."""
    variant = variant_data.copy()
    # Polish declination helper for the label used in the UI.
    moves = variant["blind_moves"]
    if moves == 1:
        label = "ruch"
    elif 2 <= moves % 10 <= 4 and (moves % 100 < 10 or moves % 100 >= 20):
        label = "ruchy"
    else:
        label = "ruchów"
    variant["label"] = label
    return variant


def home():
    """Strona główna prezentująca warianty liczby ruchów granych w ciemno."""
    statistics = get_variant_statistics(USER_ID, BASE_VARIANT_CHOICES)

    primary_variants = [
        _format_variant_payload(statistics[variant])
        for variant in PRIMARY_VARIANTS
        if variant in statistics
    ]

    other_variant_keys = sorted(
        variant
        for variant in statistics.keys()
        if variant not in PRIMARY_VARIANTS
    )
    other_variants = [
        _format_variant_payload(statistics[variant]) for variant in other_variant_keys
    ]

    total_unique = sum(item["unique_solved"] for item in statistics.values())
    total_attempts = sum(item["total_attempts"] for item in statistics.values())

    return render_template(
        "home.html",
        primary_variants=primary_variants,
        other_variants=other_variants,
        total_unique=total_unique,
        total_attempts=total_attempts,
    )
