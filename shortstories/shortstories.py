#!/usr/bin/env python

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


def main(title='Short Stories', composer='Jonathan Marmor'):
    oboe = make_instrument(Oboe, 'ob', 'B-3', 'G#6')
    song = Song(oboe)
    notate(song, title, composer)


def make_instrument(klass, nickname, lowest_note, highest_note):
    instrument = klass()
    instrument.nickname = nickname
    instrument.lowest_note = Pitch(lowest_note)
    instrument.highest_note = Pitch(highest_note)
    instrument.all_notes = list(
        frange(
            instrument.lowest_note.ps,
            instrument.highest_note.ps + 1
        )
    )
    return instrument


def notate(song, title, composer):
    timestamp = datetime.datetime.utcnow()
    metadata = Metadata()
    metadata.title = title
    metadata.composer = composer
    metadata.date = timestamp.strftime('%Y/%m/%d')

    part = Part()
    part.id = song.instrument.nickname
    part.insert(0, song.instrument)

    score = Score()
    score.insert(0, metadata)
    score.insert(0, part)
    # self.score.insert(0, StaffGroup(self.parts.l))

    make_notation(song.bars, part)

    score.show('musicxml', '/Applications/Sibelius 7.5.app')


def make_notation(bars, part):
    # Make notation
    previous_duration = None
    for bar in bars:
        for bar_part in bar.parts:
            measure = notate_measure(previous_duration, bar, bar_part)
            part.append(measure)
            # self.parts.d[part['instrument_name']].append(measure)
        previous_duration = bar.duration


def notate_measure(previous_duration, bar, part):
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
        n = notate_note(note)
        measure.append(n)

    return measure


def notate_note(note):
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
    main()
