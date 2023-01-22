# coding: utf-8
from __future__ import unicode_literals
from builtins import str, object
import gqlspection
from gqlspection.utils import pad_string


class GQLSubQuery(object):
    field       = None
    name        = ''
    description = ''
    max_depth   = 4

    def __init__(self, field, max_depth=5):
        self.field        = field
        self.name         = field.name
        self.max_depth    = max_depth - 1

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
        PADDING = ' ' * indent if indent else ''
        SPACE   = ' '  if (indent is not None) else ''

        return SPACE, NEWLINE, PADDING

    def str(self, pad=4):
        """Generate a string representation.

        'pad' parameter defines number of space characters to use for indentation. Special values:
        'pad=0'    generates minimized query (oneliner without comments).
        'pad=None' generates super-optimized query where spaces are omitted as much as possible
        """
        # whitespace characters collapse when query gets minimized
        SPACE, NEWLINE, PADDING = self._indent(pad)

        arguments = (',' + SPACE).join([str(x) for x in self.field.args])

        first_line = ''.join((
            self.name,
            "({arguments})".format(arguments=arguments) if arguments else "",
            (SPACE + "{" + NEWLINE) if not self.field.type.kind.is_final else NEWLINE
        ))

        middle_lines = ''
        if self.max_depth:
            for field in self.field.type.fields:
                subquery = GQLSubQuery(field, max_depth=self.max_depth)
                middle_lines += NEWLINE.join(subquery.str(pad).splitlines()) + NEWLINE
        else:
            # Max recursion depth reached
            middle_lines = '!!! MAX RECURSION DEPTH REACHED !!!' + NEWLINE
        middle_lines = pad_string(middle_lines, pad)

        last_line = '}' + NEWLINE if not self.field.type.kind.is_final else ""

        if pad:
            if self.description:
                description_line = gqlspection.utils.format_comment(self.description) + NEWLINE
            else:
                description_line = ''
            result = description_line + first_line + middle_lines + last_line
        else:
            result = first_line + middle_lines + last_line

        return result
