# coding: utf-8
from __future__ import unicode_literals
import gqlspection
from gqlspection.six import python_2_unicode_compatible, text_type
from gqlspection.utils import pad_string


@python_2_unicode_compatible
class GQLSubQuery(object):
    field       = None
    name        = ''
    description = ''
    depth       = 4

    def __init__(self, field, depth=4):
        # type: (GQLField, int) -> None
        self.field        = field
        self.name         = field.name
        self.depth        = depth - 1

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
        PADDING = ' ' * indent if indent else ''
        SPACE   = ' '  if (indent is not None) else ''

        return SPACE, NEWLINE, PADDING

    def _render_arguments(self, SPACE):
        # In GraphQL all fields can have arguments, even scalars
        args = (',' + SPACE).join([text_type(x) for x in self.field.args])
        return "({args})".format(args=args) if args else ""

    def _render_description(self):
        return gqlspection.utils.format_comment(self.description)

    # FIXME: pad parameter in this function isn't used as described in comments, figure out if it's even necessary
    def to_string(self, pad=4):
        """Generate a string representation.

        'pad' parameter defines number of space characters to use for indentation. Special values:
        'pad=0'    generates minimized query (oneliner without comments).
        'pad=None' generates super-optimized query where spaces are omitted as much as possible
        """
        # whitespace characters collapse when query gets minimized
        SPACE, NEWLINE, PADDING = self._indent(pad)

        # Handle a simple type like scalar or enum (no curly braces)
        if self.field.type.kind.is_final:
            # Return field_name(potential: arguments, if: any)\n
            return self.name + self._render_arguments(SPACE) + NEWLINE
        # Handle a complicated field type involving curly braces

        # Handle a Union
        if self.field.kind.kind == 'UNION':
            first_line = self.name + self._render_arguments(SPACE) + SPACE + '{' + NEWLINE

            middle = ''
            for union in self.field.type.unions:
                union_first_line = '... on ' + union.name + SPACE + '{' + NEWLINE

                union_middle_lines = '__typename' + NEWLINE
                for field in union.fields:
                    subquery = GQLSubQuery(field, depth=self.depth + 1)
                    union_middle_lines += NEWLINE.join(subquery.to_string(pad).splitlines()) + NEWLINE
                union_middle_lines = pad_string(union_middle_lines, pad)

                union_last_line = '}' + NEWLINE
                middle += union_first_line + union_middle_lines + union_last_line
            middle = pad_string(middle, pad)

            last_line = '}' + NEWLINE

            return first_line + middle + last_line

        # Did we reach the depth limit?
        if self.depth < 0:
            if pad:
                # Write a comment to hint at the absent fields not included due to reached depth limit
                return '#' + SPACE + self.name + self._render_arguments(SPACE) + ' {}' + NEWLINE
            else:
                # Minimized query, no comments
                return ''

        # Initiate recursion
        first_line = self.name + self._render_arguments(SPACE) + SPACE + '{' + NEWLINE

        middle_lines = ''
        for field in self.field.type.fields:
            subquery = GQLSubQuery(field, depth=self.depth)
            middle_lines += NEWLINE.join(subquery.to_string(pad).splitlines()) + NEWLINE
        middle_lines = pad_string(middle_lines, pad)

        last_line = '}' + NEWLINE

        if pad and self.description:
            return self._render_description() + NEWLINE + first_line + middle_lines + last_line
        return first_line + middle_lines + last_line
