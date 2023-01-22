# coding: utf-8
from __future__ import unicode_literals
from builtins import object


class GQLEnum(object):
    name = ''
    description = ''
    is_deprecated = False
    deprecation_reason = ''

    def __init__(self, name, description = '', is_deprecated=False, deprecation_reason=''):
        self.name = name
        self.description = description
        self.is_deprecated = is_deprecated
        self.deprecation_reason = deprecation_reason

    @staticmethod
    def from_json(json):
        return GQLEnum(
            name=json['name'],
            description=json.get('description', ''),
            is_deprecated=json.get('is_deprecated', False),
            deprecation_reason=json.get('deprecation_reason', '')
        )

    def __repr__(self):
        return '{name} ({description})'.format(
            name = self.name,
            description = self.description
        )
