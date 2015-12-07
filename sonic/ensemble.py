class Ensemble(object):
    def __init__(self, instruments):
        self._list = instruments
        self._dict = {}
        self.names = []

        for item in self._list:
            item['music'] = []

            # Enable getting an instrument object as an attribute or by string
            # Example: ensemble.oboe or ensemble['oboe']
            variable_name = item.get('variable_name', item['name'])

            self.names.append(variable_name)
            self._dict[variable_name] = item
            setattr(self, variable_name, item)

        self.bass = ['piano_left', 'cello']
        self.treble = ['soprano', 'flute', 'oboe', 'piano_right', 'cello']

    def __iter__(self):
        for item in self._list:
            yield item

    def __getitem__(self, arg):
        if arg in range(len(self._list)):
            return self._list[arg]
        if arg in self._dict:
            return self._dict[arg]
