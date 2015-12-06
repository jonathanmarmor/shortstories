import itertools

from utils import (weighted_choice, build_chord_type_on_all_roots,
    pitches_to_intervals)


def choose_next_harmony(history, chord_type):
    last = history[-1]
    intervals = pitches_to_intervals(chord_type)
    chords = build_chord_type_on_all_roots(intervals)

    scored = []
    for chord in chords:
        transition_score = score_transition(last, chord)
        scored.append({
            'chord': chord,
            'transition_score': transition_score,
        })

    scored.sort(key=lambda x: x['transition_score'], reverse=True)

    options = scored[:6]
    weights = [10, 5, 3, 2, 1]
    choice = weighted_choice(options, weights)
    return choice['chord']


def score_transition(a, b):
    score = 0
    if a == b:
        return 0
    for ap, bp in itertools.product(a, b):
        interval = ap - bp
        interval = abs(interval)

        if interval > 6:
            interval = 12 - interval

        if interval == 0:
            score += 100
        elif interval == 1:
            score += 20
        elif interval == 2:
            score += 15
        elif interval == 5:
            score += 10

    len_b = len(b)

    score = score / len_b

    if len_b <= 3:
        score += 50

    return score
