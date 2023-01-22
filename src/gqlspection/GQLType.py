# coding: utf-8
from __future__ import unicode_literals
from builtins import str, object
import gqlspection


class GQLType(object):
    name = ''
    kind = None
    schema = None
    description = ''
    fields = None
    interfaces = None
    enums = None
    args = None
    url = ''

    def __init__(self, name, kind, schema, description='', fields=None, interfaces=None, enums=None, args=None, url=''):
        self.name = name
        self.kind = kind
        self.schema = schema
        # Optional strings
        self.description = description
        self.url         = url
        # Optional GQLWrappers
        self.args       = args       or gqlspection.GQLArgs(schema, {})
        self.fields     = fields     or gqlspection.GQLFields(schema, {})
        self.interfaces = interfaces or gqlspection.GQLInterfaces(schema, {})
        self.enums      = enums      or gqlspection.GQLEnums(schema, {})

    @staticmethod
    def from_json(json, schema):
        wrap = gqlspection.GQLWrapFactory(schema, json)

        return GQLType(
            name=json['name'],
            kind=gqlspection.GQLTypeKind.from_json(json),
            schema=schema,
            description=json.get('description', ''),

            fields     = wrap.fields(),
            interfaces = wrap.interfaces(),
            enums      = wrap.enums(),
            args       = wrap.args(),

            url=json.get('specifiedByURL', '')
        )

    def __repr__(self):
        return '"{name}" ({kind}) - {description} - [fields: {fields}] [interfaces: {interfaces}] [enums: {enums}] [ ' \
               'args: {args}]'.format(
            name        = self.name,
            kind        = self.kind.kind,
            description = self.description,
            fields      = ', '.join([str(x) for x in self.fields]),
            interfaces  = ', '.join([str(x) for x in self.interfaces]),
            enums       = ', '.join([str(x) for x in self.enums]),
            args        = ', '.join([str(x) for x in self.args])
        )
