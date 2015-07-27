#!/usr/bin/env python

import sys
import datetime

from music21.note import Note, Rest
from music21.pitch import Pitch
from music21.chord import Chord
from music21.stream import Measure, Part, Score
from music21.meter import TimeSignature
from music21.metadata import Metadata
from music21.instrument import Oboe
from music21.tempo import MetronomeMark
from music21.duration import Duration

from utils import frange, split_at_beats, join_quarters
from song import Song


class Piece(object):
    def __init__(self):
        self.score = Score()

        self.instrument = Oboe()
        self.instrument.nickname = 'ob'
        oboe_range = ('B-3', 'G#6')   # Oboe      58 92
        self.instrument.lowest_note = Pitch(oboe_range[0])
        self.instrument.highest_note = Pitch(oboe_range[1])
        self.instrument.all_notes = list(
            frange(
                self.instrument.lowest_note.ps,
                self.instrument.highest_note.ps + 1
            )
        )

        self.part = Part()
        self.part.id = 'ob'
        self.part.insert(0, self.instrument)

        # Make Metadata
        timestamp = datetime.datetime.utcnow()
        metadata = Metadata()
        metadata.title = 'Short Stories'
        metadata.composer = 'Jonathan Marmor'
        metadata.date = timestamp.strftime('%Y/%m/%d')
        self.score.insert(0, metadata)

        self.score.insert(0, self.part)
        # self.score.insert(0, StaffGroup(self.parts.l))

        # Make a "song"
        self.song = Song(self.instrument)

        self.make_notation()

    def make_notation(self):
        # Make notation
        previous_duration = None
        for bar in self.song.bars:
            for part in bar.parts:
                measure = self.notate_measure(previous_duration, bar, part)
                self.part.append(measure)
                # self.parts.d[part['instrument_name']].append(measure)
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
