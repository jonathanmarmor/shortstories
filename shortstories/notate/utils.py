import itertools


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
