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
    Clarinet,
    Flute,
    AltoSaxophone,
    Trumpet,
    Violin,
    Vibraphone,
    Contrabass
)
from music21.layout import StaffGroup
from music21.tempo import MetronomeMark
from music21.duration import Duration

from utils import frange, split_at_beats, join_quarters, scale
from song import Song


class Instruments(object):
    def __init__(self):
        self.names = [
            'fl',
            'ob',
            'cl',
            'sax',
            'tpt',
            'vln',
            'vib',
            'bs'
        ]
        self.fl = fl = Flute()
        self.ob = ob = Oboe()
        self.cl = cl = Clarinet()
        self.sax = sax = AltoSaxophone()
        self.tpt = tpt = Trumpet()
        self.vln = vln = Violin()
        self.vib = vib = Vibraphone()
        self.bs = bs = Contrabass()

        self.l = [
            fl,
            ob,
            cl,
            sax,
            tpt,
            vln,
            vib,
            bs
        ]
        self.d = {}
        for name, inst in zip(self.names, self.l):
            inst.nickname = name
            self.d[name] = inst

        # lowest, highest notes
        ranges = [
            ('C4', 'C7'),     # Flute     60 96
            ('B-3', 'G#6'),   # Oboe      58 92
            ('D3', 'G6'),     # Clarinet  50 91
            ('D-3', 'A-5'),   # Sax       49 80
            ('E3', 'B-5'),    # Trumpet   52 82
            ('G3', 'B6'),     # Violin
            ('F3', 'F6'),     # Vibraphone
            ('E1', 'G3')      # Bass
        ]
        for r, i in zip(ranges, self.l):
            i.lowest_note = Pitch(r[0])
            i.highest_note = Pitch(r[1])
            i.all_notes = list(frange(i.lowest_note.ps, i.highest_note.ps + 1))
            i.all_notes_24 = list(frange(i.lowest_note.ps, i.highest_note.ps + 1, 0.5))

    def soloists_shared_register(self):
        soloists = [
            'ob',
            'cl',
            'sax',
            'fl',
            'tpt',
        ]
        lowest_notes = [self.d[name].lowest_note.ps for name in soloists]
        lowest = int(max(lowest_notes))
        highest_notes = [self.d[name].highest_note.ps for name in soloists]
        highest = int(min(highest_notes))
        return range(lowest, highest + 1)


class Parts(object):
    def __init__(self, instruments):
        self.names = [
            'fl',
            'ob',
            'cl',
            'sax',
            'tpt',
            'vln',
            'vib',
            'bs'
        ]

        self.fl = fl = Part()
        self.ob = ob = Part()
        self.cl = cl = Part()
        self.sax = sax = Part()
        self.tpt = tpt = Part()
        self.vln = vln = Part()
        self.vib = vib = Part()
        self.bs = bs = Part()

        self.l = [
            fl,
            ob,
            cl,
            sax,
            tpt,
            vln,
            vib,
            bs
        ]
        self.d = {}
        for name, part, inst in zip(self.names, self.l, instruments.l):
            part.id = name
            self.d[name] = part
            part.insert(0, inst)


class Piece(object):
    def __init__(self, ranges=False):
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

        if ranges:
            # Don't make a piece, just show the instrument ranges
            for inst, part in zip(self.instruments.l, self.parts.l):
                measure = Measure()
                measure.timeSignature = TimeSignature('4/4')
                low = Note(inst.lowest_note)
                measure.append(low)
                high = Note(inst.highest_note)
                measure.append(high)
                part.append(measure)
            return

        self.duet_options = [
            ('ob', 'sax'),
            ('fl', 'sax'),
            ('cl', 'sax'),
            ('ob', 'tpt'),
            ('sax', 'tpt'),
            ('cl', 'tpt'),
            ('fl', 'tpt'),
            ('fl', 'ob'),
            ('fl', 'cl'),
            ('ob', 'cl'),
        ]

        # 8 to 12 minutes
        max_duration = 12
        piece_duration_minutes = scale(random.random(), 0, 1, 8, max_duration)

        # Make the "songs"
        self.songs = []
        total_minutes = 0
        n = 1
        while total_minutes < piece_duration_minutes - .75:
            print
            print 'Song', n
            song = Song(self, n)
            self.songs.append(song)
            print 'Song Duration:', int(round(song.duration_minutes * 60.0))
            print 'Tempo:', song.tempo
            print 'Number of Beats:', song.duration_beats

            n += 1
            total_minutes += song.duration_minutes

        _minutes, _seconds = divmod(total_minutes, 1.0)
        print
        print 'Total Duration: {}:{}'.format(int(_minutes), int(round(_seconds * 60)))
        print

        self.make_notation()

    def make_notation(self):
        # Make notation
        previous_duration = None
        for song in self.songs:
            for bar in song.bars:
                for part in bar.parts:
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

                    for note in part['notes']:
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

                        measure.append(n)

                    self.parts.d[part['instrument_name']].append(measure)
                previous_duration = bar.duration


if __name__ == '__main__':
    show = True
    if 'ranges' in sys.argv:
        piece = Piece(ranges=True)
    else:
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
