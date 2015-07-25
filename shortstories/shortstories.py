#!/usr/bin/env python

import sys
import datetime
import random

from music21.note import Note, Rest
from music21.pitch import Pitch
from music21.chord import Chord
from music21.stream import Measure, Part, Score
from music21.meter import TimeSignature
from music21.metadata import Metadata
from music21.instrument import (
    Oboe,
)
from music21.layout import StaffGroup
from music21.tempo import MetronomeMark
from music21.duration import Duration

from utils import frange, split_at_beats, join_quarters, scale
from song import Song


class Instruments(object):
    def __init__(self):
        self.names = [
            'ob',
        ]
        self.ob = ob = Oboe()

        self.l = [
            ob,
        ]
        self.d = {}
        for name, inst in zip(self.names, self.l):
            inst.nickname = name
            self.d[name] = inst

        # lowest, highest notes
        ranges = [
            ('B-3', 'G#6'),   # Oboe      58 92
        ]
        for r, i in zip(ranges, self.l):
            i.lowest_note = Pitch(r[0])
            i.highest_note = Pitch(r[1])
            i.all_notes = list(frange(i.lowest_note.ps, i.highest_note.ps + 1))
            i.all_notes_24 = list(frange(i.lowest_note.ps, i.highest_note.ps + 1, 0.5))

    def soloists_shared_register(self):
        soloists = [
            'ob',
        ]
        lowest_notes = [self.d[name].lowest_note.ps for name in soloists]
        lowest = int(max(lowest_notes))
        highest_notes = [self.d[name].highest_note.ps for name in soloists]
        highest = int(min(highest_notes))
        return range(lowest, highest + 1)


class Parts(object):
    def __init__(self, instruments):
        self.names = [
            'ob',
        ]

        self.ob = ob = Part()

        self.l = [
            ob,
        ]
        self.d = {}
        for name, part, inst in zip(self.names, self.l, instruments.l):
            part.id = name
            self.d[name] = part
            part.insert(0, inst)


class Piece(object):
    def __init__(self):
        score = self.score = Score()
        self.instruments = self.i = Instruments()
        self.parts = Parts(self.i)

        # Make Metadata
        timestamp = datetime.datetime.utcnow()
        metadata = Metadata()
        metadata.title = 'Short Stories'
        metadata.composer = 'Jonathan Marmor'
        metadata.date = timestamp.strftime('%Y/%m/%d')
        score.insert(0, metadata)

        [score.insert(0, part) for part in self.parts.l]
        score.insert(0, StaffGroup(self.parts.l))

        self.duet_options = None

        # Make a "song"
        self.songs = []
        song = Song(self, 1)
        self.songs.append(song)

        self.make_notation()

    def make_notation(self):
        # Make notation
        previous_duration = None
        for song in self.songs:
            for bar in song.bars:
                for part in bar.parts:
                    measure = self.notate_measure(previous_duration, bar, part)
                    self.parts.d[part['instrument_name']].append(measure)
                previous_duration = bar.duration

    def notate_measure(self, previous_duration, bar, part):
        measure = Measure()
        if bar.tempo:
            mark = MetronomeMark(
                number=bar.tempo,
                referent=Duration(1)
            )
            measure.insert(0, mark)
            measure.leftBarline = 'double'
        if bar.duration != previous_duration:
            ts = TimeSignature('{}/4'.format(bar.duration))
            measure.timeSignature = ts

        # Fix Durations
        durations = [note['duration'] for note in part['notes']]

        components_list = split_at_beats(durations)
        components_list = [join_quarters(note_components) for note_components in components_list]
        for note, components in zip(part['notes'], components_list):
            note['durations'] = components

        # Notate
        for note in part['notes']:
            n = self.notate_note(note)
            measure.append(n)

        return measure

    def notate_note(self, note):
        if note['pitch'] == 'rest':
            n = Rest()
        else:
            if isinstance(note['pitch'], list):
                pitches = []
                for pitch_number in note['pitch']:
                    p = Pitch(pitch_number)
                    # Force all flats
                    if p.accidental.name == 'sharp':
                        p = p.getEnharmonic()
                    pitches.append(p)
                n = Chord(notes=pitches)

            else:
                p = Pitch(note['pitch'])
                # Force all flats
                if p.accidental.name == 'sharp':
                    p = p.getEnharmonic()
                n = Note(p)

        d = Duration()
        if note['duration'] == 0:
            d.quarterLength = .125
            d = d.getGraceDuration()
        else:
            d.fill(note['durations'])
        n.duration = d
        return n


if __name__ == '__main__':
    show = True
    piece = Piece()

    if 'midi' in sys.argv:
        piece.score.show('midi')

    if 'noshow' not in sys.argv:
        if 'muse' in sys.argv:
            piece.score.show('musicxml', '/Applications/MuseScore.app')
        elif 'fin' in sys.argv:
            piece.score.show('musicxml', '/Applications/Finale 2012.app')
        else:
            piece.score.show('musicxml', '/Applications/Sibelius 7.5.app')
