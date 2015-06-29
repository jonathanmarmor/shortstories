# -*- coding: utf-8 -*-

import itertools
from collections import defaultdict
import random

from utils import weighted_choice, pairwise


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


def build_chord_type_on_root(root, chord_type):
    """
    >>> build_chord_type_on_root(9, [4, 3, 5])
    [9, 1, 4]

    """
    chord = [root]
    for interval in chord_type[:-1]:
        chord.append((chord[-1] + interval) % 12)
    return chord


def build_chord_type_on_all_roots(chord_type):
    """
    >>> build_chord_type_on_all_roots([4, 3, 5])
    [[0, 4, 7],
     [1, 5, 8],
     [2, 6, 9],
     [3, 7, 10],
     [4, 8, 11],
     [5, 9, 0],
     [6, 10, 1],
     [7, 11, 2],
     [8, 0, 3],
     [9, 1, 4],
     [10, 2, 5],
     [11, 3, 6]]

    """
    return [build_chord_type_on_root(root, chord_type) for root in range(12)]


def pitches_to_intervals(chord):
    """
    >>> pitches_to_intervals([12, 16, 31])
    [4, 3, 5]
    """
    # TODO rewrite this
    pcs = sorted(list(set([p % 12 for p in chord])))
    pcs = [p - pcs[0] for p in pcs]
    pcs.reverse()
    pcs.insert(0, 12)
    intervals = []
    for a, b in pairwise(pcs):
        intervals.append(a - b)
    intervals.reverse()
    return intervals
