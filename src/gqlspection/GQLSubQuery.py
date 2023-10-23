# coding: utf-8
from __future__ import unicode_literals
from gqlspection.six import python_2_unicode_compatible, text_type
from gqlspection.utils import pad_string, format_comment
from gqlspection.GQLField import GQLField
from gqlspection.GQLTypeProxy import GQLTypeProxy
import copy


# TODO: Figure out if it's better to split this monstrosity in two classes
class QueryBuilder(object):
    def __init__(self, query, indent=4):
        # Used for building the query string
        self.indent = indent
        self.lines = []
        self.level = 0
        # Used for holding the stack of subqueries to be processed (to avoid recursion)
        self.stack = [query]
        # Is this the last level of depth? If so, comment out the rest of the query at this level
        self.max_depth = query.max_depth

    # String building methods
    def add_line(self, line):
        initial = '#' if self.last_leg else ''
        if line:
            self.lines.append(' ' * self.indent * self.level + line)

    def add_lines(self, lines):
        for line in lines:
            self.add_line(line)

    # If this is the last level of depth, comment out the current line (field name) and place {} on the same line
    def open_brace(self):
        leaf_achieved = self.last_leg and (not len(self.lines) or '...' not in self.lines[-1])
        symbol = '{}' if leaf_achieved else '{'

        if self.lines:
            self.lines[-1] += ' ' + symbol
        else:
            self.add_line(symbol)

        if leaf_achieved:
            # Place '#' at the first non-space character of the last line
            self.lines[-1] = ' ' * self.indent * self.level + '#' + self.lines[-1].lstrip()
        else:
            self.level += 1

            # TODO: Separation of concerns anyone?
            # Schedule a closing brace to be printed after all subfields are processed
            self.schedule_close_brace()

    def close_brace(self):
        self.level -= 1
        self.add_line('}')

    def add_field(self, field, args=None):
        line = field
        if args:
            line += '(' + ', '.join(['{k}: {v}'.format(k=k, v=v) for k, v in args.items()]) + ')'
        self.add_line(line)

    def build(self):
        return '\n'.join(self.lines)

    # Stack management
    def __iter__(self):
        return self

    def __next__(self):
        item = None
        while not item:
            if not self.stack:
                raise StopIteration

            item = self.stack.pop()

            # None signals a closing brace
            if item is None:
                self.close_brace()

        return item

    @property
    def last_leg(self):
        return self.level >= self.max_depth

    def schedule_close_brace(self):
        self.stack.append(None)

    def schedule(self, items):
        self.stack.extend(reversed(items))


@python_2_unicode_compatible
class GQLSubQuery(object):
    field       = None
    name        = ''
    indent      = 4
    max_depth   = 4
    depth       = 1
    union       = None

    def __init__(self, field, indent = 4, max_depth = 4, current_depth = 1, union=None):
        # type: (GQLField, int) -> None
        self.field        = field
        self.name         = field.name
        self.indent       = indent
        self.max_depth    = max_depth
        self.depth        = current_depth
        self.union        = union

    @property
    def depth_limit_reached(self):
        return self.depth >= self.max_depth

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

    @property
    def name_and_args(self):
        return self.name + self._render_arguments(' ')

    def _format_comment(self, text):
        """Concatenate text with arguments if they exist and format it as a comment."""
        args = self._describe_arguments()
        if args:
            # If there are arguments, add a colon to the main description and list the arguments
            # as a bulleted list
            if text and text[-1] not in ('.', '!', '?', ':', ';'):
                text += ':'

            for arg in args:
                text += '\n - ' + arg
        return format_comment(text) if text else ''

    @property
    def current_padding(self):
        # max_depth and indent are set per query, but each subquery has its own effective depth
        return self.depth * self.indent

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
        """Raw description of the field or type, without formatting."""
        return self._field_description or self._type_description

    @property
    def description(self):
        """Description of the field or type, formatted as a comment, appropriate for type and indentation level."""
        if self.field.kind.kind == 'ENUM':
            if self._description:
                description = '(enum) ' + self._description
            else:
                description = 'enum'

            if description and description[-1] not in ('.', '!', '?', ':', ';'):
                description += ':'
            for enum in self.field.type.enums:
                description += '\n - ' + text_type(enum)
            return self._format_comment(description)

        if self.field.type.kind.is_builtin_scalar:
            # Don't add a comment for builtin scalars, they are boring
            return self._format_comment(self._field_description)

        return self._format_comment(self._description)

    def subquery(self, field):
        """Create a subquery for the given field."""
        if isinstance(field, GQLField):
            return GQLSubQuery(field, indent=self.indent, max_depth=self.max_depth, current_depth=self.depth + 1)
        elif isinstance(field, GQLTypeProxy):
            return GQLSubQuery(self.field, indent=self.indent, max_depth=self.max_depth, current_depth=self.depth + 1, union=field)

    # TODO: A hacky way to handle unions, figure out a better way later
    def subunion(self, union):
        """Create a subquery for the given union."""
        query = copy.deepcopy(self)
        query.union = union
        return query

    def to_string(self, pad=4):
        """Generate a string representation of the GraphQL query, iteratively."""
        self.builder = QueryBuilder(self, pad)

        for query in self.builder:
            # Union handling is a bit hacky, but it works
            if query.union:
                self.builder.add_line('... on ' + query.union.name)
                self.builder.open_brace()
                self.builder.add_line('__typename')
                self.builder.schedule([query.subquery(field) for field in query.union.fields])
                continue

            # Print out description and field name
            description_lines = query.description.splitlines()

            if len(description_lines) == 1 and query.field.type.kind.is_leaf:
                # Inline comment for a leaf type, like a scalar or enum, assuming description fits in a single line
                self.builder.add_line(query.name_and_args + ' ' + query.description)
            else:
                # Multiline comment precedes the field name
                self.builder.add_lines(description_lines)
                self.builder.add_field(query.name_and_args)

            # A complicated type, like an object or union - open a curly brace and iterate over subfields
            if not query.field.type.kind.is_leaf:
                # Opens a curly brace and schedules a closing brace to be printed after all subfields are processed
                self.builder.open_brace()

                if query.depth_limit_reached:
                    # If we reached the depth limit, don't add any subfields
                    continue

                # Add subfields
                if query.field.kind.kind == 'UNION':
                    self.builder.schedule([query.subquery(union) for union in query.field.type.unions])

                else:
                #if query.field.kind.kind == 'OBJECT':
                    self.builder.schedule([query.subquery(field) for field in query.field.type.fields])


        return self.builder.build()
