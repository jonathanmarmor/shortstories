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

import random

from notate import notate

from instruments import instruments
from ensemble import Ensemble
# from graph import Graph


def make_phrase():
    phrase = []
    total_duration = 0  # in microbeats
    length = 64
    while total_duration < length:
        pitch = random.choice(['rest', 'rest', 'rest', 'rest', 'rest', 'rest', 60, 61, 62, 63, 64, 65, 66, 67, 68])
        duration = random.choice([.25, .5, .75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0])
        if total_duration + duration > length:
            duration = length - total_duration

        phrase.append({
            'pitch': pitch,
            'duration': duration
        })
        total_duration += duration
    return phrase


class Song(object):
    title = 'Working Title'
    composer = 'Jonathan Marmor'

    def __init__(self):
        self.ensemble = Ensemble(instruments)

        # self.graph = Graph(self.ensemble)

        self.make_music()

    def make_music(self):
        phrase = make_phrase()

        for instrument in self.ensemble:
            instrument['music'] = phrase


if __name__ == '__main__':
    song = Song()
    notate(song.title, song.composer, song.ensemble._list)
