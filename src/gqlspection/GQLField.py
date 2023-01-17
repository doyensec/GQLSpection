# coding: utf-8
import gqlspection

# FIXME: Add support for InputFields


class GQLField(object):
    name = ''                # type: str
    description = ''         # type: str
    kind  = None             # type: gqlspection.GQLTypeKind
    type  = None             # type: gqlspection.GQLTypeProxy
    args = None              # type: gqlspection.GQLArgs
    is_deprecated = False    # type: bool
    deprecation_reason = ''  # type: str
    schema = None            # type: gqlspection.GQLSchema

    def __init__(self, name, kind, schema, description='', args=None, is_deprecated=False, deprecation_reason=''):
        self.name = name
        self.kind = kind
        self.type = gqlspection.GQLTypeProxy(kind.name, schema)
        self.schema = schema
        self.description = description
        self.args = args or gqlspection.GQLArgs(schema, {})
        self.is_deprecated = is_deprecated
        self.deprecation_reason = deprecation_reason

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
            description=field.get('description', ''),
            args=GQLField._wrap_args(field, schema),
            is_deprecated=field.get('isDeprecated', False),
            deprecation_reason=field.get('deprecationReason', '')
        )
