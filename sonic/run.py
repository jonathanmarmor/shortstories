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


class Song(object):
    title = 'Working Title'
    composer = 'Jonathan Marmor'

    def __init__(self):
        self.ensemble = Ensemble(instruments)

        # self.graph = Graph(self.ensemble)

        self.make_music()

    def make_phrase(self):
        phrase = []
        total_duration = 0  # in microbeats
        length = 4
        while total_duration < length:
            pitch = random.choice(['rest', 60, 61, 62, 63, 64, 65, 66, 67, 68])
            duration = random.choice([.25, .5, .75, 1.0, 1.25, 1.5])
            if total_duration + duration > length:
                duration = length - total_duration

            phrase.append({
                'pitch': pitch,
                'duration': duration
            })
            total_duration += duration
        return phrase

    def make_music(self):
        phrase = self.make_phrase()
        # phrase_duration = sum([n['duration'] for n in phrase])

        # # Make a list of possible gap durations
        # # the range is from a sixteenth note to 1.5 times the duration of the phrase
        # phrase_dur_times_4 = int(phrase_duration * 4)
        # gap_max = phrase_dur_times_4 + (phrase_dur_times_4 / 2)
        # gap_options = [(_ / 4.0) + .25 for _ in range(gap_max)]

        # last_instrument_name = None

        # length = 128
        # total_duration = 0
        # while total_duration < length:

        #     # pick a duration from the start of the last phrase where the next phrase will begin
        #     gap = random.choice(gap_options)

        #     # pick an instrument, that isn't the instrument that just played the phrase
        #     instrument_name = random.choice([i for i in self.ensemble.names if i not last_instrument])
        #     last_instrument_name = instrument_name

        #     # figure out the difference between the total duration already in this instrument and the starting point of the previous phrase in last instrument
        #     # then add gap to that
        #     # and append a rest of that duration to the instrument
        #     # then append the phrase
        #     # then loop

        length = 16
        total_duration = 0
        while total_duration < length:
            for inst in self.ensemble:
                gap = {
                    'pitch': 'rest',
                    'duration': random.choice([1.5, 1.75, 2.0, 2.25, 2.5])
                }
                inst['music'].append(gap)
                inst['music'].extend(phrase)

                dur = sum([n['duration'] for n in inst['music']])
                if dur > total_duration:
                    total_duration = dur


if __name__ == '__main__':
    song = Song()
    notate(song.title, song.composer, song.ensemble._list)
