import datetime

from music21.note import Note, Rest
from music21.pitch import Pitch
from music21.chord import Chord
from music21.stream import Part, Score
from music21.metadata import Metadata
from music21.duration import Duration
from music21.layout import StaffGroup
from music21.instrument import fromString as get_instrument
from music21.clef import BassClef

from utils import split_at_beats, join_quarters


def notate(song):
    score = setup_score(song)
    parts = setup_parts(song, score)

    make_notation(song, parts)

    score.show('musicxml', '/Applications/Sibelius 7.5.app')


def setup_score(song):
    timestamp = datetime.datetime.utcnow()
    metadata = Metadata()
    metadata.title = song.title
    metadata.composer = song.composer
    metadata.date = timestamp.strftime('%Y/%m/%d')

    score = Score()
    score.insert(0, metadata)

    return score


def setup_parts(song, score):
    parts = []
    for instrument in song.instruments:
        part = Part()
        m21_instrument = get_instrument(instrument['name'])

        part.insert(0, m21_instrument)
        if instrument.get('clef') is 'bass':
            part.insert(0, BassClef())

        parts.append(part)
        score.insert(0, part)

    score.insert(0, StaffGroup(parts))

    return parts


def decorate_notes_with_split_durations(notes):
    """Decorate note objects with durations split at beats, which should be tied together"""
    durations = [note['duration'] for note in notes]
    components_list = split_at_beats(durations)
    components_list = [join_quarters(note_components) for note_components in components_list]
    for note, components in zip(notes, components_list):
        note['durations'] = components


def make_notation(song, parts):
    for part, inst in zip(parts, song.instruments):

        decorate_notes_with_split_durations(inst['music'])

        for note in inst['music']:
            part.append(notate_note(note))


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
