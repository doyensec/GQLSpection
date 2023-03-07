# coding: utf-8
from __future__ import unicode_literals
from gqlspection.six import ensure_text, text_type
import gqlspection


class GQLArg(object):
    name         = ''
    kind         = None
    description  = ''
    type         = None
    default_value = ''

    def __init__(self, name, kind, type_, description='', default_value=''):
        # type: (str, GQLTypeKind, GQLType, str, str) -> None
        self.name = ensure_text(name)
        self.kind = kind
        self.type = type_
        self.description = ensure_text(description)
        self.default_value = ensure_text(default_value)

    @staticmethod
    def from_json(json, schema):
        kind = gqlspection.GQLTypeKind.from_json(json['type'])

        return GQLArg(
            name=json['name'],
            kind=kind,
            type_=gqlspection.GQLTypeProxy(kind.name, schema),
            description=json.get('description', '') or '',
            default_value=json.get('default_value', '') or ''
        )

    def __repr__(self):
        return '{name}: {type}'.format(
            name = self.name,
            type = text_type(self.kind)
        )
