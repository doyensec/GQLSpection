# coding: utf-8
from __future__ import unicode_literals
from builtins import str, object
import gqlspection


class GQLArg(object):
    name         = ''
    kind         = None
    description  = ''
    type         = None
    default_value = ''

    def __init__(self, name, kind, type_, description='', default_value=''):
        self.name = name
        self.kind = kind
        self.type = type_
        self.description = description
        self.default_value = default_value

    @staticmethod
    def from_json(json, schema):
        kind = gqlspection.GQLTypeKind.from_json(json['type'])

        return GQLArg(
            name=json['name'],
            kind=kind,
            type_=gqlspection.GQLTypeProxy(kind.name, schema),
            description=json.get('description', ''),
            default_value=json.get('default_value', '')
        )

    def __repr__(self):
        return '{name}: {type}'.format(
            name = self.name,
            type = str(self.kind)
        )
