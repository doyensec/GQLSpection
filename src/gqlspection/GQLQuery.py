# coding: utf-8
from __future__ import unicode_literals
from builtins import object
import gqlspection
from gqlspection.utils import pad_string


class GQLQuery(object):
    type    = None
    operation = ''
    name   = ''
    description = ''
    fields = None

    def __init__(self, gqltype, operation='query', name='', fields=None):
        self.fields = fields if fields else self.type.fields
        self.operation = operation
        self.name = name
        self.type = gqltype

    def __repr__(self):
        self.str()

    def __str__(self):
        self.str()

    @staticmethod
    def _indent(indent):
        """Generates characters that should be used for Space and Newline, depending on request indentation level.

        If indent > 0, space is preserved and new lines are started with 'indent' number of spaces.
        If indent = 0, space is preserved, but new lines are removed
        If indent = None, both space and newlines are trimmed.
        """
        NEWLINE = '\n' if indent else ''
        PADDING = ' ' * (indent) if indent else ''
        SPACE   = ' '  if (indent is not None) else ''

        return SPACE, NEWLINE, PADDING

    def str(self, pad=4):
        """Generate a string representation.

        'indent' parameter defines number of space characters to use for indentation. Special values:
        'indent=0'    generates minimized query (oneliner without comments).
        'indent=None' generates super-optimized query where spaces are omitted as much as possible
        """
        # whitespace characters collapse when query gets minimized
        SPACE, NEWLINE, PADDING = self._indent(pad)

        first_line = ''.join((
            self.operation,
            (' ' + self.name) if self.name else '',
            SPACE + '{' + NEWLINE
        ))

        middle_lines = ""
        for field in self.fields:
            subquery = gqlspection.GQLSubQuery(field)
            middle_lines += NEWLINE.join(subquery.str(pad).splitlines()) + NEWLINE
        middle_lines = pad_string(middle_lines, pad)

        last_line = '}' if not self.type.kind.is_final else ""

        if pad:
            if self.description:
                description_line = gqlspection.utils.format_comment(self.description) + NEWLINE
            else:
                description_line = ''
            result = description_line + first_line + middle_lines + last_line
        else:
            result = first_line + middle_lines + last_line

        return result
