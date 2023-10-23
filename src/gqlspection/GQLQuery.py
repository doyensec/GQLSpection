# coding: utf-8
from __future__ import unicode_literals
import gqlspection
from gqlspection.six import python_2_unicode_compatible, ensure_text
from gqlspection.utils import pad_string
from gqlspection import log


@python_2_unicode_compatible
class GQLQuery(object):
    type    = None
    operation = ''
    name   = ''
    description = ''
    fields = None

    def __init__(self, gqltype, operation='query', name='', fields=None, depth=4):
        # type: (GQLType, str, str, Optional[GQLFields]) -> None

        self.fields = fields if fields else self.type.fields
        self.operation = ensure_text(operation)
        self.name = ensure_text(name)
        self.type = gqltype
        self.depth = depth

    def __repr__(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()

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

    def to_string(self, pad=4):
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
            if not field.name:
                log.warning("Skipped a field because it does not have a name.")
                continue
            subquery = gqlspection.GQLSubQuery(field, max_depth=self.depth, current_depth=0)
            middle_lines += NEWLINE.join(subquery.to_string(pad).splitlines()) + NEWLINE
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
