import datetime

from music21.note import Note, Rest
from music21.pitch import Pitch
from music21.chord import Chord
from music21.stream import Measure, Part, Score
from music21.meter import TimeSignature
from music21.metadata import Metadata
from music21.tempo import MetronomeMark
from music21.duration import Duration
from music21.layout import StaffGroup
from music21.instrument import (
    Flute,
    Oboe,
    Clarinet,
    AltoSaxophone,
    Trumpet,
    Violin,
    Vibraphone,
    Contrabass
)

from utils import split_at_beats, join_quarters


INSTRUMENTS = {
    'flute': Flute,
    'oboe': Oboe,
    'clarinet': Clarinet,
    'alto saxophone': AltoSaxophone,
    'trumpet': Trumpet,
    'violin': Violin,
    'vibraphone': Vibraphone,
    'contrabass': Contrabass
}


def notate(song):
    timestamp = datetime.datetime.utcnow()
    metadata = Metadata()
    metadata.title = song.title
    metadata.composer = song.composer
    metadata.date = timestamp.strftime('%Y/%m/%d')

    score = Score()
    score.insert(0, metadata)

    parts = []
    for instrument in song.instruments:
        part = Part()
        instrument = INSTRUMENTS[instrument['name']]
        part.insert(0, instrument())
        parts.append(part)
        score.insert(0, part)

    score.insert(0, StaffGroup(parts))

    make_notation(song.bars, parts)

    score.show('musicxml', '/Applications/Sibelius 7.5.app')


def make_notation(bars, parts):
    # Make notation
    previous_duration = None
    for bar in bars:
        for i, bar_part in enumerate(bar.parts):
            measure = notate_measure(previous_duration, bar, bar_part)
            parts[i].append(measure)
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
