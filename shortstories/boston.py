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
    'flute': {
        'name': 'flute',
        'nickname': 'fl',
        'all_notes': range(60, 96 + 1),
    },
    'oboe': {
        'name': 'oboe',
        'nickname': 'ob',
        'all_notes': range(58, 92 + 1),
    }
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
        self.instruments = [
            INSTRUMENTS['oboe'],
            INSTRUMENTS['flute']
        ]

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
                            'pitch': random.choice(instrument['all_notes'])
                        }
                    ]
                }
                bar.parts.append(part)


if __name__ == '__main__':
    song = Song()
    notate(song)
