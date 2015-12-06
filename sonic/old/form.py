import random
from collections import Counter


FORMS = """a-a- bca- bbcd bca-
a-bc a-bc d--- a-bc
a-b- c-b- d-b- c-b-
a-b- c-b- c-d- a-b-
a-b- ccb- dcb- a-b-
a-b- a-b- c-d- a-b-
a-bc a-dc e-bc a-dc
a-bc a-dc e--- a-dc
a-bc a-dc e--- a-bc
a-bc d-ec f-bc d-ec
a-bc d-ec f--- a-ec
a--- b--- cdef b---
a--- b-c- defg b-c-
a--- b-c- d--- b-c-
a-b- c--- a-b- d-b-
a-bc a-ba- d--- a-bc
a--- b--- c-d b---
a-b- a-b- cdc a-b-
a-a- b-a- cd- b-a-
a-bc a-bd e---bc a-bd
a-bb a-cb a-d--- a-bb
a-b--- a-b--- c-d- b---
a-b--- a-a- ccd a-b---
a---b- a---c- a--- d--- a---
a-b-c-a- d--- b-a-
a-b-c-a- c-a- d--- c-a-
a-b-c-a- d-b-c-a-
a-b-cca- d---b-ca-
a--- bcdc a--- ecfc
abcb aded afgf ahih
abac dedc fgfc hihc
a-b- ccb- d-b- ecb-
a-bc a-bd e-bf a-bg
a-bc d-be f--- bcbe
a-a- a-bc d-d- d-ec
a-a- a-b- d-a- d-b-
abc- abc- d-c- abc-
abc- abd- d-c- abd-
abc- d--- efg- d---
abac d--- aeaf d---
abac d-e- afag h-e-
abac d-e- afag d-h-
abcb d-e- fbgb h-e-
abcb d-e- f-cb abcb
ab---ac- ad---ac-
a-b- a-b- cdef a-b-
a-bc a-bc defc a-bc
a--- b--- cdef a---
abcd abcd bcda abcd
a-bc d-bc e-fc a-bc
a-b- a-b- ccdc a-b-
a-b- c-b- ddb- c-b-
a-b- c-b- ddb- a-b-
a-b- a-b- cdef a-b-
a-bc a-bc defc a-bc
abcd abcd e--- abcd
abcb abcd e--- abcb
abcb abcd e-cd abcb
a-a- b-a- c-de b-a-
a-a- b-a- ccdc b-a-
a-a- b-a- ccde b-a-
a-b- c--- a-d- c---
a-bc d--- a-ec d---
a-bc d--- e-bc d---
a-bc d--- efg- d---"""


FORMS = FORMS.split('\n')


class Form(object):
    def __init__(self, form_string):
        form_string = form_string.strip().replace(' ', '')
        self.form_string = form_string
        self.bars = []
        self.bar_types = {}
        self.type_count = Counter()
        for char in form_string:
            if char != '-':
                b = Bar(char)
                self.bars.append(b)
            else:
                b.duration += 2

        for bar in self.bars:
            self.type_count[bar.type] += 1
            if bar.type not in self.bar_types:
                self.bar_types[bar.type] = BarType(bar.type, bar.duration)
            self.bar_types[bar.type].count += 1
            bar.type_obj = self.bar_types[bar.type]

        self.duration = sum([bb.duration for bb in self.bars])

    def __repr__(self):
        return self.form_string
        # return ' '.join([str(b) for b in self.bars])


class Bar(object):
    def __init__(self, bar_type):
        self.type = bar_type
        self.duration = 2
        self.tempo = None

        self.melody = []
        self.harmony = []

    def __repr__(self):
        return '{}{}'.format(self.type, self.duration)


class BarType(object):
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration

        self.melody = []
        self.harmony = []

        self.count = 0

    def __repr__(self):
        return 'Bar Type: name: {} duration: {} parts: '.format(self.name, self.duration, self.parts)


def choose():
    form_string = random.choice(FORMS)
    return Form(form_string)


if __name__ == '__main__':
    f = choose()
    for b in f.bars:
        print b.type_obj.harmonic_rhythm
