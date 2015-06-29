import random
import itertools
from collections import defaultdict


class S(object):
    def __init__(self, *args, **kwargs):
        if 'arguments' in kwargs:
            args = kwargs['arguments']
        self.weighted_options = args

    def choose(self):
        weights, options = zip(*self.weighted_options)
        choice = weighted_choice(options, weights)
        if isinstance(choice, S):
            return choice.choose()
        return choice


def scale(x, minimum, maximum, floor=0, ceiling=1):
    return ((ceiling - floor) * (float(x) - minimum))/(maximum - minimum) + floor


def scale_list(l, floor=0, ceiling=1):
    minimum = 0
    maximum = sum(l)
    return [scale(x, minimum, maximum, floor, ceiling) for x in l]


def weighted_choice(options, weights):
    rand = random.random()
    rand = scale(rand, 0, 1, 0, sum(weights))
    total = 0
    for i, weight in enumerate(weights):
        total += weight
        if rand < total:
            return options[i]


def frange(x, y, step=1.0):
    if step > 0:
        while x < y:
            yield x
            x += step
    if step < 0:
        while x > y:
            yield x
            x += step


def split_at_offsets(dur, offsets):
    """split a single duration at offsets."""
    if len(offsets) == 0:
        return [dur]

    components = []
    offsets.append(dur)
    start = 0
    for offset in offsets:
        components.append(offset - start)
        start = offset

    return components


def split_at_beats(note_durs):
    """Split a list of durations at quarter notes."""
    beat_indexes = list(frange(0, sum(note_durs)))

    total = 0
    components = []
    for dur in note_durs:
        start = total
        end = total + dur

        split_at = []
        for beat in beat_indexes:
            if start < beat < end:
                split_point = beat - start
                split_at.append(split_point)

        note_components = split_at_offsets(dur, split_at)
        components.append(note_components)
        total += dur

    return components


def join_quarters(dur_components):
    """For duration components of a single note, join together any adjacent quarter note components"""
    new_durs = []
    for key, group in itertools.groupby(dur_components):
        new_dur = key
        len_group = len(list(group))
        if key == 1.0 and len_group > 1:
            new_dur = float(len_group)
        new_durs.append(new_dur)
    return new_durs


def set_start_end(notes):
    offset = 0
    for note in notes:
        note['start'] = offset
        note['end'] = offset + note['duration']
        offset += note['duration']


def get_at(offset, notes):
    for note in notes:
        if note['start'] <= offset < note['end']:
            return note


def exp_weights(n, exponent=2, reverse=True):
    weights = [(x + 1) ** exponent for x in range(n)]
    weights.reverse()
    return weights


def pairwise(iterable):
    """
    >>> list(pairwise(range(5)))
    [(0, 1), (1, 2), (2, 3), (3, 4)]

    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def get_intervals(harmony):
    """
    >>> get_intervals([2, 6, 9])
    {
        3: [(6, 9)],
        4: [(2, 6)],
        5: [(9, 2)]
    }

    """
    intervals = defaultdict(list)
    for interval in range(1, 7):
        for bottom in harmony:
            top = (bottom + interval) % 12
            if top in harmony:
                intervals[interval].append((bottom, top))
    return dict(intervals)
