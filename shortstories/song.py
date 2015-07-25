import random
from collections import Counter

from utils import weighted_choice, frange, set_start_end, get_at
import form
from chord_types import (get_chord_type, diatonic_scales_for_harmony,
    other_scales_for_harmony)
import animal_play_harmony
import harmonic_rhythm
from melody_rhythm import get_melody_rhythm
import scalar_ornaments
import scored_ornaments


def choose(options, chosen):
    choice = random.choice(options)
    if chosen and chosen[-1] == choice:
        choice = choose(options, chosen)
    return choice


def ornament_bridge(a, b, n=None, prev_duration=0.75, width=2):
    """Find notes that bridge the interval between a and b"""

    if n is None:
        # Choose the number of notes in the ornament
        if prev_duration >= 0.75:
            n = weighted_choice([1, 2, 3, 4, 5, 6], [3, 3, 4, 5, 4, 3])
        else:
            n = weighted_choice([1, 2, 3], [3, 4, 5])

    interval = b - a
    direction = 0
    if interval > 0:
        direction = 1
    if interval < 0:
        direction = -1

    if direction == 0:
        option_groups = [range(int(a - width), int(a + width + 1))] * n

    else:
        offset_interval = float(interval) / n
        option_groups = []
        for offset in list(frange(a, b, offset_interval)):
            middle = int(round(offset))
            opts = range(middle - width, middle + width + 1)
            option_groups.append(opts)

    # Prevent the last note in the ornament from being the target note.
    if b in option_groups[-1]:
        option_groups[-1].remove(b)

    ornaments = []
    for opts in option_groups:
        choice = choose(opts, ornaments)
        ornaments.append(choice)

    return ornaments


class Song(object):
    def __init__(self, piece, movement):
        """
        self.duration = total song duration
        self.bars =
            bar.parts =
                part['instrument_name']
                part['notes']
                    note['pitch']
                    note['duration'] = total note duration


        """
        self.piece = piece
        self.movement = movement
        self.prev_root = random.randint(0, 11)

        self.instruments = self.piece.instruments

        self.melody_register = self.instruments.soloists_shared_register()

        history = {}
        for name in self.instruments.names:
            history[name] = []

        self.form = form.choose()

        print self.form.form_string

        self.bars = self.form.bars
        self.duration_beats = self.form.duration

        tempo_options = range(32, 50, 2)
        self.tempo = random.choice(tempo_options)

        self.bars[0].tempo = self.tempo
        self.duration_minutes = self.duration_beats / float(self.tempo)

        root = random.randint(0, 12)
        self.harmony_history = [[(p * root) % 12 for p in get_chord_type()]]

        # for each bar_type pick a transposition pattern
        # for each bar of that type, assign the next transposition in the
        # pattern
        # make a sub register of the soloists' common register for the
        # bar_type, that has a buffer to allow the melody to be transposed the
        # amount that it will be transposed
        trans_patterns = {
            'descending': [
                [0, -1, -2, -3, -4],
                [0, -2, -1, -3, -2],
                [0, -1, -3, -5, -7],
                [0, -2, -4, -6, -8],
                [0, -2, -4, -5, -7],
            ],
            'ascending': [
                [0, 1, 2, 3, 4],
                [0, 2, 1, 3, 2],
                [0, 2, 4, 5, 7],
                [0, 2, 3, 5, 7],
                [0, 2, 4, 6, 8],
            ]
        }
        for name in self.form.bar_types:
            bar_type = self.form.bar_types[name]

            bar_type.direction = random.choice(trans_patterns.keys())
            options = trans_patterns[bar_type.direction]
            bar_type.trans_pattern = random.choice(options)
            bar_type.trans_pattern = bar_type.trans_pattern[:bar_type.count + 1]

            if bar_type.direction == 'descending':
                bar_type.furthest_transposition = min(bar_type.trans_pattern)
                bar_type.register = self.melody_register[abs(bar_type.furthest_transposition):]
            else:
                bar_type.furthest_transposition = max(bar_type.trans_pattern)
                bar_type.register = self.melody_register[:-bar_type.furthest_transposition]

        bar_type_counter = Counter()
        for bar in self.bars:
            bar_type = self.form.bar_types[bar.type]
            i = bar_type_counter[bar.type]
            bar.transposition = bar_type.trans_pattern[i]
            bar_type_counter[bar.type] += 1

        for name in self.form.bar_types:
            bar_type = self.form.bar_types[name]
            bar_type.harmonic_rhythm = harmonic_rhythm.choose(bar_type.duration)

            # Harmony
            bar_type.harmony = []
            for harm_dur in bar_type.harmonic_rhythm:

                chord_type = get_chord_type()

                # print 'CHORD TYPE:', chord_type

                harmony = animal_play_harmony.choose_next_harmony(
                    self.harmony_history,
                    chord_type
                )
                self.harmony_history.append(harmony)

                # print 'HARMONY:', harmony

                h = {
                    'duration': harm_dur,
                    'pitch': harmony
                }
                bar_type.harmony.append(h)

            # Melody
            bar_type.melody = self.choose_melody_notes(
                bar_type.duration,
                bar_type.harmony,
                bar_type
            )

        # Turn Bar Types into Bars

        for bar in self.bars:

            bar.parts = []

            bar.melody = bar.type_obj.melody
            bar.harmony = bar.type_obj.harmony

            soloists = ['ob']

            transposition = self.add_soloists_melody(soloists, bar)

            if transposition != 0:
                harmony = []
                for note in bar.harmony:
                    harmony.append({
                        'pitch': [p + transposition for p in note['pitch']],
                        'duration': note['duration']
                    })
                bar.harmony = harmony

    def is_melody_in_instrument_register(self, melody, instrument_name):
        instrument = self.instruments.d[instrument_name]
        register = instrument.all_notes

        return self.is_melody_in_register(melody, register)

    def is_melody_in_register(self, melody, register):
        for note in melody:
            if note['pitch'] != 'rest' and note['pitch'] not in register:
                return False
            for orn in note.get('ornaments', []):
                if orn['pitch'] not in register:
                    return False
        return True

    def can_transpose(self, transposition, melody, instrument_name):
        instrument = self.instruments.d[instrument_name]
        register = instrument.all_notes

        for note in melody:
            if note['pitch'] != 'rest' and note['pitch'] + transposition not in register:
                return False
            for orn in note.get('ornaments', []):
                if orn['pitch'] + transposition not in register:
                    return False
        return True

    def transpose_melody(self, melody, transposition):
        new_melody = []
        for note in melody:
            new_note = note.copy()

            if note['pitch'] == 'rest':
                new_note['pitch'] = 'rest'
            else:
                new_note['pitch'] = note['pitch'] + transposition

            new_note['ornaments'] = []
            for orn in note.get('ornaments', []):
                new_orn = orn.copy()
                new_orn['pitch'] = orn['pitch'] + transposition
                new_note['ornaments'].append(new_orn)

            new_melody.append(new_note)
        return new_melody

    def add_soloists_melody(self, soloists, bar):
        transposition = bar.transposition

        melody = self.transpose_melody(bar.melody, transposition)

        for soloist in soloists:
            can_go_up = self.can_transpose(12, melody, soloist)
            can_go_down = self.can_transpose(-12, melody, soloist)

            if not self.is_melody_in_instrument_register(melody, soloist):
                if can_go_up:
                    melody = self.transpose_melody(melody, 12)
                if can_go_down:
                    melody = self.transpose_melody(melody, -12)

            else:
                if can_go_up and random.random() < .8:
                    melody = self.transpose_melody(melody, 12)

            bar.parts.append({
                'instrument_name': soloist,
                'notes': melody,
            })

        return transposition

    def choose_melody_notes(self, duration, harmonies, bar_type):
        # return a list of {pitch, duration} dicts
        notes = []

        # choose a register
        # register = self.choose_violin_register()
        # register_by_pitch_classes = defaultdict(list)
        # for p in register:
        #     register_by_pitch_classes[p % 12].append(p)

        rhythm = get_melody_rhythm(duration)

        # One in four bars that have more than 3 notes will start with a rest
        start_with_rest = False
        if rhythm[0] <= 1.0:
            if len(rhythm) > 2 and random.random() < .4:
                start_with_rest = True

        for r in rhythm:
            notes.append({
                'pitch': None,
                'duration': r
            })

        self.choose_melody_pitches(
            notes,
            bar_type.register,
            harmonies,
            start_with_rest
        )

        notes = self.add_ornaments(notes)

        return notes

    def get_pitch_options(self, note_harmonies, prev):
        pitch_options = [prev - 2, prev - 1, prev + 1, prev + 2]
        pitch_options = [p for p in pitch_options if p % 12 in note_harmonies and p in self.melody_register]
        if len(pitch_options) == 0:
            if prev % 12 in note_harmonies and random.random() < .12:
                pitch_options = [prev]
            else:
                pitch_options = [prev - 5, prev - 4, prev - 3, prev + 3, prev + 4, prev + 5]
                pitch_options = [p for p in pitch_options if p % 12 in note_harmonies and p in self.melody_register]
            # if len(pitch_options) == 0:
            #     pitch_options = [prev - 8, prev - 7, prev - 6, prev + 6, prev + 7, prev + 8]
            #     pitch_options = [p for p in pitch_options if p % 12 in note_harmonies]
        return pitch_options

    def choose_melody_pitches(self, notes, register, harmonies, start_with_rest):
        # print 'Choosing pitches'
        for h in harmonies:
            h['pitch_classes'] = [p % 12 for p in h['pitch']]

        set_start_end(notes)
        set_start_end(harmonies)

        # Pick a random pitch from the instrument's register on which to start
        previous_note_index = random.choice(range(int(len(register))))
        prev = register[previous_note_index]

        previous_note = {'duration': 1.0, 'pitch': prev}

        pitch_history = []

        first = True
        # print '-'*10
        for note in notes:
            if first and start_with_rest:
                note['pitch'] = 'rest'
                first = False
                continue
            beats = list(frange(note['start'], note['start'] + note['duration'], .25))
            note_harmonies = []
            for b in beats:
                h = get_at(b, harmonies)
                h = h['pitch_classes']
                if h not in note_harmonies:
                    note_harmonies.append(h)

            if len(note_harmonies) == 1:
                pitch_options = self.get_pitch_options(note_harmonies[0], prev)
            else:
                pitch_options = []

                c = Counter()
                for h in note_harmonies:
                    for p in h:
                        c[p] += 1

                common = []
                for p, count in c.most_common():
                    if count == len(note_harmonies):
                        common.append(p)

                if len(common) > 0:
                    pitch_options = self.get_pitch_options(common, prev)

                if len(pitch_options) == 0:
                    ranked = [p for p, _ in c.most_common() if p not in common]

                    for p in ranked:
                        pitch_options = self.get_pitch_options([p], prev)
                        if len(pitch_options) > 0:
                            break

            if len(pitch_options) == 0:
                pitch_options = [prev - 2, prev - 1, prev + 1, prev + 2]

            note['pitch'] = random.choice(pitch_options)

            self.add_ornament(note, previous_note, note_harmonies, first)

            # print note

            prev = note['pitch']
            previous_note = note
            pitch_history.append(note['pitch'])

            first = False

    def add_scalar_ornament(self, note, prev, harmonies):
        interval = prev['pitch'] - note['pitch']
        if interval > 0:
            direction = 'ascending'
        if interval < 0:
            direction = 'descending'
        if interval == 0:
            direction = random.choice(['ascending', 'descending'])

        # Choose the number of notes in the ornament
        if prev['duration'] >= 1:
            n = weighted_choice([1, 2, 3, 4, 5, 6], [2, 3, 4, 6, 5, 4])
        elif prev['duration'] >= 0.75:
            n = weighted_choice([1, 2, 3], [1, 2, 4])
        else:
            n = random.randint(1, 2)

        orn = scalar_ornaments.choose(n, direction)

        harm = []
        for chord in harmonies:
            for p in chord:
                if p not in harm:
                    harm.append(p)

        scale_options = diatonic_scales_for_harmony(harm)

        if random.random() < .16 or not scale_options:
            scale_options = other_scales_for_harmony(harm)

        if scale_options:
            scale_type = random.choice(scale_options)

            note_pitch = int(note['pitch'])

            note_pitch_class = note_pitch % 12

            diff = note_pitch - note_pitch_class
            scale = []
            for octave in [diff - 12, diff, diff + 12]:
                for pc in scale_type:
                    p = pc + octave
                    scale.append(p)

            i = scale.index(note_pitch)
            scale = scale[i - 2:i + 3]

            orn_type = []
            for i in orn:
                pitch = scale[i + 2]
                orn_type.append(pitch)

            return orn_type

    def add_chromatic_interval(self, note, prev):
        interval = prev['pitch'] - note['pitch']
        if interval > 0:
            direction = 'ascending'
        if interval < 0:
            direction = 'descending'
        if interval == 0:
            direction = random.choice(['ascending', 'descending'])

        # Choose the number of notes in the ornament
        if prev['duration'] >= 1:
            max_notes = 4
            n = weighted_choice(range(1, max_notes + 1), [10, 9, 7, 5])
        elif prev['duration'] >= 0.75:
            max_notes = 3
            n = random.randint(1, max_notes)
        else:
            max_notes = 2
            n = random.randint(1, max_notes)

        orn = scored_ornaments.choose(n, direction)

        np = int(note['pitch'])
        orn_type = [np + p for p in orn]
        return orn_type

    def add_ornament(self, note, prev, harmonies, first):
        if prev['duration'] <= .25 or random.random() < .1:
            return

        # Choose between three completely different ways of making ornaments

        orn_type = None
        rand = random.random()

        if rand < .7:
            orn_type = self.add_scalar_ornament(note, prev, harmonies)
        elif rand < .9:
            orn_type = ornament_bridge(
                prev['pitch'],
                note['pitch'],
                n=None,
                prev_duration=prev['duration'],
                width=2
            )

        if not orn_type or rand >= .9:
            orn_type = self.add_chromatic_interval(note, prev)

        note['ornaments'] = []
        for n in orn_type:
            note['ornaments'].append({
                'pitch': n,
                'duration': 0
            })

    def add_ornaments(self, notes):
        new_notes = []
        for note in notes:
            if note.get('ornaments'):
                for orn in note['ornaments']:
                    new_notes.append(orn)
            new_notes.append(note)
        return new_notes
