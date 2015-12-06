#!/usr/bin/env python

"""A song with the bare minimum to be notated.

song.title
song.composer
song.instruments
    instrument['name']
song.bars
    bar.tempo
    bar.duration
    bar.parts
        part['notes']
            note['duration']
            note['pitch']

"""

import random

from notate import notate


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


class Bar(object):
    def __init__(self, tempo=None):
        self.tempo = tempo
        self.duration = 4  # Hard coded to 4/4
        self.parts = []


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

        self.bars = []
        # Hard coded to 5 bars
        for n in range(5):
            bar = Bar(tempo=60)
            self.bars.append(bar)
            for instrument in self.instruments:

                part = {
                    'notes': [
                        {
                            'duration': 4,
                            'pitch': 60  # random.choice(instrument['all_notes'])
                        }
                    ]
                }
                bar.parts.append(part)


if __name__ == '__main__':
    song = Song()
    notate(song)
