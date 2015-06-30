import random

import itertools
from collections import defaultdict

from utils import pairwise


def is_good(ornament, biggest_interval=3):
    # Put the target note at the end of the ornament
    # to prevent repeated notes or large intervals
    # between the last note of the ornament and the target note
    ornament = list(ornament)
    ornament.append(0)

    pairs = pairwise(ornament)

    for a, b in pairs:
        # Don't allow repeated pitches
        if a == b:
            return False

        # Don't allow transitions greater than `biggest_interval` steps
        if abs(a - b) > biggest_interval:
            return False

    return True


def make_ornament_types(
        max_length=6,
        max_steps_below=2,
        max_steps_above=2,
        biggest_interval=3):
    ornament_types = defaultdict(lambda: defaultdict(list))
    for n in range(1, max_length + 1):
        steps = range(-max_steps_below, max_steps_above + 1)
        for combination in itertools.product(steps, repeat=n):

            if not is_good(combination, biggest_interval=biggest_interval):
                continue

            sum_comb = sum(combination)
            if sum_comb <= 0:
                direction = 'ascending'
                ornament_types[n][direction].append(combination)

            if sum_comb >= 0:
                direction = 'descending'
                ornament_types[n][direction].append(combination)
    return ornament_types


ornament_types = make_ornament_types()


def choose(n, direction):
    return random.choice(ornament_types[n][direction])
