# coding: utf-8
from __future__ import unicode_literals
from gqlspection.six import python_2_unicode_compatible, text_type
from gqlspection.utils import pad_string, format_comment


@python_2_unicode_compatible
class GQLSubQuery(object):
    field       = None
    name        = ''
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

    def _describe_arguments(self):
        # Not using ';' as descriptions could end with a dot which would look ugly.
        return ['{name}: {description}'.format(name=arg.name, description=arg.description)
                for arg in self.field.args if arg.description]

    def _format_comment(self, text):
        """Concatenate text with arguments if they exist and format it as a comment."""
        args = self._describe_arguments()
        if not args:
            # If there are no arguments, just return the main description
            return format_comment(text) if text else ''

        # If there are arguments, add a colon to the main description and list the arguments
        # as a bulleted list
        if text and text[-1] not in ('.', '!', '?', ':', ';'):
            text += ':'

        for arg in args:
            text += '\n - ' + arg
        return format_comment(text) if text else ''

    @property
    def _field_description(self):
        return self.field.description

    @property
    def _type_description(self):
        return self.field.type.description

    @property
    def field_description(self):
        return self._format_comment(self._field_description)

    @property
    def type_description(self):
        return self._format_comment(self._type_description)

    @property
    def _description(self):
        return self._field_description or self._type_description

    @property
    def description(self):
        return self._format_comment(self._description)

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
        # In these cases return field_name(potential: arguments, if: any)\n
        # TODO: The comments below could be aligned for better readability, but it's not trivial to do as lines
        # are parsed one by one and comments are added as they are encountered
        if self.field.kind.kind == 'ENUM':
            if self._description:
                description = '(enum) ' + self._description
            else:
                description = 'enum'

            if description and description[-1] not in ('.', '!', '?', ':', ';'):
                description += ':'
            for enum in self.field.type.enums:
                description += '\n - ' + text_type(enum)
            return format_comment(description) + NEWLINE + self.name + self._render_arguments(SPACE) + NEWLINE
        if self.field.type.kind.is_builtin_scalar:
            # Builtin scalars like INT, STRING, etc. always have description at type level, but it's boring, so only
            # add comment if there's an explicit field description
            if self.field_description:
                args = self._render_arguments(SPACE)
                if args:
                    # If there are arguments, show the description above the field name
                    return self.field_description + NEWLINE + self.name + self._render_arguments(SPACE) + NEWLINE
                # Otherwise show the description as an inline comment
                return self.name + self._render_arguments(SPACE) + ' ' + self.field_description + NEWLINE
            return self.name + self._render_arguments(SPACE) + NEWLINE
        elif self.field.type.kind.is_leaf:
            # Other leaf types (I think only custom scalars are left?) - field
            # level description takes precedence over type level
            if self.description:
                return self.name + self._render_arguments(SPACE) + ' ' + self.description + NEWLINE
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

        if pad:
            if self.description:
                return self.description + NEWLINE + first_line + middle_lines + last_line
        return first_line + middle_lines + last_line
