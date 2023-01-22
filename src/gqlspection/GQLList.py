# coding: utf-8
from __future__ import unicode_literals
from builtins import str
try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping  # type: ignore
from collections import OrderedDict


class GQLList(Mapping):
    """A very specific data structure for internal use. Acts as an iterable in certain instances and a dict in others.

    Characteristics:

      - Gets initialized from an iterable of some type, which should have a 'name' field
      - Upon iteration, will return original dictionaries, sorted by the 'name' field
      - Allows selecting elements both by index (gqllist[3]) and by the 'name' (gqllist['some-name'])
      - GQLList is meant for read-only data, so there is no way to add, update, delete elements
    """
    _elements = None

    def __init__(self, elements):
        sorted_elements = sorted(elements, key=lambda i: i.name)
        self._elements = OrderedDict(
            ((i.name, i) for i in sorted_elements)
        )

    def __getitem__(self, item):
        if isinstance(item, str):
            return self._elements[item]
        if type(item) == int:
            key = list(self._elements.keys())[item]
            return self._elements[key]
        raise Exception("GQLList: unknown type: %s", type(item))

    def __iter__(self):
        return (self._elements[el] for el in self._elements)

    def __str__(self):
        return '\n'.join((str(el) for el in self._elements))

    def __repr__(self):
        first_line = "GQLList[{inner_type}]".format(
            inner_type=str(type(self._elements[0]))
        )

        other_lines = ['    ' + repr(el) for el in self._elements]

        return '\n'.join([first_line] + other_lines)

    def __bool__(self):
        return not not len(self._elements)

    def __len__(self):
        return len(self._elements)

    def __contains__(self, item):
        if isinstance(item, str):
            return item in list(self._elements.keys())
        else:
            return item in list(self._elements.values())
