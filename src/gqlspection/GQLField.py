# coding: utf-8
from __future__ import unicode_literals
import gqlspection
from gqlspection.six import ensure_text

# FIXME: Add support for InputFields


class GQLField(object):
    name = ''
    description = ''
    kind  = None
    type  = None
    args = None
    is_deprecated = False
    deprecation_reason = ''
    schema = None

    def __init__(self, name, kind, schema, description='', args=None, is_deprecated=False, deprecation_reason=''):
        # type: (str, GQLTypeKind, GQLSchema, str, Optional[GQLArgs], bool, str) -> None
        self.name = ensure_text(name)
        self.kind = kind
        self.type = gqlspection.GQLTypeProxy(kind.name, schema)
        self.schema = schema
        self.description = ensure_text(description)
        self.args = args or gqlspection.GQLArgs(schema, {})
        self.is_deprecated = is_deprecated
        self.deprecation_reason = ensure_text(deprecation_reason)

    @staticmethod
    def _wrap_args(json, schema):
        args = []
        for i in (json.get('args', []) or []):
            args.append(gqlspection.GQLArg.from_json(i, schema))
        return args

    @staticmethod
    def from_json(field, schema):
        return GQLField(
            name=field['name'],
            kind=gqlspection.GQLTypeKind.from_json(field['type']),
            schema=schema,
            description=field.get('description', '') or '',
            args=GQLField._wrap_args(field, schema),
            is_deprecated=field.get('isDeprecated', False) or False,
            deprecation_reason=field.get('deprecationReason', '') or ''
        )
