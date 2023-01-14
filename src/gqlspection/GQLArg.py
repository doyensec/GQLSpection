import gqlspection


class GQLArg(object):
    name         = ''     # type: str
    kind         = None   # type: gqlspection.GQLTypeKind
    description  = ''     # type: str
    type         = None   # type: gqlspection.GQLTypeProxy
    default_value = ''    # type: str

    def __init__(self, name, kind, type_, description='', default_value=''):
        self.name = name
        self.kind = kind
        self.type = type_
        self.description = description
        self.default_value = default_value

    @staticmethod
    def from_json(json, schema):
        kind = gqlspection.GQLTypeKind(json['type'])

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
