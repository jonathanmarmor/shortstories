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
from music21.instrument import fromString as get_instrument

from utils import split_at_beats, join_quarters


def notate(song):
    timestamp = datetime.datetime.utcnow()
    metadata = Metadata()
    metadata.title = song.title
    metadata.composer = song.composer
    metadata.date = timestamp.strftime('%Y/%m/%d')

    score = Score()
    score.insert(0, metadata)

    parts = []
    for instrument_name in song.instruments:
        part = Part()
        m21_instrument = get_instrument(instrument_name)
        part.insert(0, m21_instrument)
        parts.append(part)
        score.insert(0, part)

    score.insert(0, StaffGroup(parts))

    make_notation(song, parts)

    score.show('musicxml', '/Applications/Sibelius 7.5.app')


def make_notation(song, parts):
    first_instrument = True
    for name, part in zip(song.instruments, parts):
        previous_duration = None
        previous_tempo = None
        for bar in song.graph[name]:
            measure = Measure()

            # Only print the tempo if:
            # - the tempo is not the same as the previous
            if bar.tempo and bar.tempo != previous_tempo:
                mark = MetronomeMark(
                    number=bar.tempo,
                    referent=Duration(1)
                )
                measure.insert(0, mark)

            if first_instrument:
                # Only print time signature if:
                # - it is the first instrument AND
                # - the time signature is not the same as the previous
                if bar.duration_calculated != previous_duration:
                    ts = TimeSignature('{}/4'.format(bar.duration_calculated))
                    measure.timeSignature = ts

            # Fix Durations
            durations = [note['duration'] for note in bar.notes]

            components_list = split_at_beats(durations)
            components_list = [join_quarters(note_components) for note_components in components_list]
            for note, components in zip(bar.notes, components_list):
                note['durations'] = components

            # Notate Measure
            for note in bar.notes:
                n = notate_note(note)
                measure.append(n)

            part.append(measure)

            previous_duration = bar.duration_calculated
            previous_tempo = bar.tempo

        song.graph[name][-1].rightBarline = 'double'

        first_instrument = False


# def notate_measure(bar, part):


#     # Fix Durations
#     durations = [note['duration'] for note in part.notes]

#     components_list = split_at_beats(durations)
#     components_list = [join_quarters(note_components) for note_components in components_list]
#     for note, components in zip(part.notes, components_list):
#         note['durations'] = components

#     # Notate Measure
#     for note in part.notes:
#         n = notate_note(note)
#         measure.append(n)

#     return measure


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
