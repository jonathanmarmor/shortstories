#!/usr/bin/env python

"""A song with the bare minimum to be notated.

song.title
song.composer
song.instruments
    instrument['name']
    instrument['music']
        note['duration']
        note['pitch']

"""

import random

from notate import notate
import harmonic_rhythm


INSTRUMENTS = {
    'soprano': {
        'name': 'soprano',
        'nickname': 's',
        'all_notes': range(60, 81 + 1),
    },
    'flute': {
        'name': 'flute',
        'nickname': 'fl',
        'all_notes': range(60, 96 + 1),
    },
    'oboe': {
        'name': 'oboe',
        'nickname': 'ob',
        'all_notes': range(58, 92 + 1),
    },
    'piano_right': {
        'name': 'piano',
        'nickname': 'pno-r',
        'all_notes': range(60, 108 + 1),
    },
    'piano_left': {
        'name': 'piano',
        'nickname': 'pno-l',
        'all_notes': range(21, 60 + 1),
        'clef': 'bass',
    },
    'cello': {
        'name': 'cello',
        'nickname': 'vc',
        'all_notes': range(36, 76 + 1),
    },
}


class Song(object):
    title = 'Test Song'
    composer = 'Jonathan Marmor'

    def __init__(self):
        self.score_order = [
            'soprano',
            'flute',
            'oboe',
            'piano_right',
            'piano_left',
            'cello'
        ]
        self.instruments = [INSTRUMENTS[i] for i in self.score_order]

        for inst in self.instruments:
            inst['music'] = []

            # Hard coded to 10 bars
            # No ties across barlines yet
            rhythm = []
            for n in range(10):
                rhythm.extend(harmonic_rhythm.choose(4))

            for dur in rhythm:
                inst['music'].append({
                    'duration': dur,
                    'pitch': 60  # random.choice(inst['all_notes'])
                })


if __name__ == '__main__':
    song = Song()
    notate(song)
