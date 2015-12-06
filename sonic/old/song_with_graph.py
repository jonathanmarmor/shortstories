#!/usr/bin/env python

from graph import Graph
from notate_graph import notate


class Bar(object):
    def __init__(self, tempo=None):
        self.tempo = tempo
        self.notes = []

    @property
    def duration_calculated(self):
        return sum([note.get('duration', 0) for note in self.notes])


class Song(Graph):
    title = 'New Song'
    composer = 'Jonathan Marmor'

    def __init__(self):
        super(Song, self).__init__()

        self.add_instruments([
            'oboe',
            'clarinet',
            'electric guitar'
        ])

        # Build up the graph, or a bunch of graphs, then join them

        the_bar = Bar(tempo=60)
        the_bar.notes = [{
            'duration': 4,
            'pitch': 60
        }]

        self.add_bars([the_bar, the_bar, the_bar])


if __name__ == '__main__':
    song = Song()
    notate(song)
