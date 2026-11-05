"""Readings-based NLI label for an equivocation-induced pair.

Neutral here means, in the three-way NLI scheme, "neither
Entailment nor Contradiction". It is computed from readings,
not from a model call: H is true on one reading of the
homonymous keyword and false on the other, and no reading
forces it either way until the lexeme is disambiguated.
"""


def nli_label():
    """Return the NLI label for the unresolved pair."""
    readings = {
        "mammal_reading": True,    # Brown bat / Brown A as mammal: H true
        "baseball_reading": False,  # Brown bat / Brown A as equipment: H false
    }
    values = set(readings.values())
    if values == {True}:
        label = "Entailment"
    elif values == {False}:
        label = "Contradiction"
    else:
        label = "Neutral"
    return {
        "label": label,
        "readings": readings,
        "entailment_forced": False,
        "contradiction_forced": False,
        "neutral_because_readings_disagree": label == "Neutral",
    }
