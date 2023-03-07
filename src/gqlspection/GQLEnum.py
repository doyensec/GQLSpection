# coding: utf-8
from __future__ import unicode_literals
from gqlspection.six import ensure_text


class GQLEnum(object):
    name = ''
    description = ''
    is_deprecated = False
    deprecation_reason = ''

    def __init__(self, name, description = '', is_deprecated=False, deprecation_reason=''):
        # type: (str, str, bool, str) -> None
        self.name = ensure_text(name)
        self.description = ensure_text(description)
        self.is_deprecated = is_deprecated
        self.deprecation_reason = ensure_text(deprecation_reason)

    @staticmethod
    def from_json(json):
        return GQLEnum(
            name=json['name'],
            description=json.get('description', '') or '',
            is_deprecated=json.get('is_deprecated', False) or False,
            deprecation_reason=json.get('deprecation_reason', '') or ''
        )

    def __repr__(self):
        return '{name} ({description})'.format(
            name = self.name,
            description = self.description
        )
