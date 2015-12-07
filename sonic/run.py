#!/usr/bin/env python

"""A piece of music for Sonic Liberation Players

song.title
song.composer
song.instruments
    instrument['name']
    instrument['music']
        note['duration']
        note['pitch']

"""

# import random

from notate import notate

from instruments import instruments
from ensemble import Ensemble
# from graph import Graph


class Song(object):
    title = 'Working Title'
    composer = 'Jonathan Marmor'

    def __init__(self):
        self.ensemble = Ensemble(instruments)

        # self.graph = Graph(self.ensemble)

        self.make_music()

    def make_music(self):
        phrase = []
        for _ in range(16):
            phrase.append({
                'pitch': 60,
                'duration': .25
            })

        self.ensemble.flute['music'].extend(phrase)

    # def ___(self):
    #     offset = 0
    #     for soloist in self.instruments:
    #         offset = random.randint(offset + 4, offset + 16)


if __name__ == '__main__':
    song = Song()
    notate(song.title, song.composer, song.ensemble._list)
