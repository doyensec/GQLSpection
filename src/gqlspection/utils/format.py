# coding: utf-8


# example usage:
#   pretty = PrettyPrinter()
#   formatted = pretty.format(query, minimized=False, spaces=4)
#   print(formatted)

class PrettyPrinter(object):
    """A class for pretty printing GraphQL queries."""

    def __init__(self, minimized=False, spaces=4):
        """Initialize the class."""
        self._minimized = minimized
        self._spaces = spaces
        self._tokens = []

    def _tokenize(self):
        """Tokenize the GraphQL request."""
        # GraphQL ignores whitespace (outside strings and comments) and commas
        # Tokens:
        #   Punctuator      !	$	&	(	)	...	:	=	@	[	]	{	|	}
        #   Name            starts with letter, continues letters, digits, _
        #   IntValue
        #   FloatValue
        #   StringValue     but """ starts a block string
        tokens = []

        # iterate over each character in the query, keeping track of context within the query
        # detect the start & end of tokens and add them to the list
        #   - don't modify strings
        #   - don't modify comments

        self._index = 0
        while self._index < self._length:
            self._move_index_to_next_token()
            if self._index >= self._length:
                break

            char = self._request[self._index]

            # strings and block strings
            if char == '"':
                token = self._read_string()
            # comments
            elif char == '#':
                token = self._read_comment()
            # single char punctuation
            elif char in ('!', '$', '(', ')', '.', ',', ':', '=', '@', '[', ']', '{', '|', '}'):
                token = self._read_punctuator()
            # integers (3, -42) and floats (1.0, 6.674E-11, 2e3, 3e+4, 0.4E-5)
            elif char in ('-', '+') or char.isdigit():
                token = self._read_number()
            # names (/[_A-Za-z][_0-9A-Za-z]*/), including keywords (true, false, null)
            elif char.isalpha() or char == '_':
                token = self._read_name()
            else:
                raise ValueError(f"Unexpected character '{char}' at position {self._index}")

            tokens.append(token)

        return tokens

    # Technically, in GraphQL commas could be ignored as well, but people expect them to be there
    # so we'll keep them in and filter them out later if necessary
    def _move_index_to_next_token(self):
        """Move the index to the next token."""
        while self._index < self._length:
            char = self._request[self._index]

            # ignore whitespace
            if char.isspace():
                self._index += 1
            else:
                break

    def _read_string(self):
        """Consume a string token."""
        start = index = self._index
        length = self._length

        # check for block strings - start with """ and may contain newlines
        if index + 2 < length and self._request[index:index+3] == '"""':
            block_string = True
            index += 3
        else:
            block_string = False
            index += 1

        # read until the end of the string
        while index < length:
            char = self._request[index]

            # check for escaped characters
            if char == '\\':
                # check for escaped unicode (\u + 4 hex digits)
                if index + 5 < length and self._request[index+1] == 'u':
                    # technically should be /[0-9A-Fa-f]{4}/, not worth checking for now
                    index += 6
                else:
                    # otherwise it's a regular escaped character
                    # according to spec, only "\/bfnrt are allowed, but this could vary by implementation
                    index += 2
                continue

            # check for the end of the string
            if char == '"':
                if block_string:
                    if index + 2 < length and self._request[index:index+3] == '"""':
                        index += 3
                        break
                else:
                    index += 1
                    break

            index += 1
        else:
            # if we get here, we've reached the end of the query without finding the end of the string
            raise ValueError(f"Unterminated string starting at position {start}")

        self._index = index
        return self._request[start:index]

    def _read_comment(self):
        """Consume a comment token."""
        start = self._index

        # Comments can be placed on their own line, or at the end of a line
        # From the server's perspective, it doesn't matter, but it does matter to the user
        # As a hack we'll do a lookbehind to see if there was a newline before the comment
        # In order to separate these two styles of comments, we'll store newline (if present) at the end of the token - hack!

        start_of_previous_whitespace = len(self._request[:start].rstrip())
        whitespace = self._request[start_of_previous_whitespace:start]
        add_newline = ('\n' in whitespace)

        # Comment ends at the end of the line (don't include the newline in the token)
        newline_idx = self._request.find('\n', self._index)
        token = self._request[start:newline_idx]
        if newline_idx == -1:
            # if there's no newline, the comment goes to the end of the query
            newline_idx = self._length
            token = self._request[start:]

        self._index = newline_idx + 1

        # add a newline to the end of the token if there was one before the comment (a hack to differentiate inline/whole line comments)
        if add_newline:
            token += '\n'
        return token

    def _read_punctuator(self):
        """Consume a punctuator token."""
        # check for '...'
        if self._request[self._index:self._index+3] == '...':
            token = '...'
            self._index += 3
        else:
            # otherwise it's a single char punctuator
            token = self._request[self._index]
            self._index += 1

        return token

    def _read_number(self):
        """Consume a number token."""
        start = index = self._index
        length = self._length

        # read until the end of the number
        while index < length:
            char = self._request[index]

            # check for the end of the number
            if not char.isdigit() and char not in ('.', 'e', 'E', '+', '-'):
                break

            index += 1

        self._index = index
        return self._request[start:index]

    def _read_name(self):
        """Consume a name token."""
        start = index = self._index
        length = self._length

        # read until the end of the name
        while index < length:
            char = self._request[index]

            # check for the end of the name
            if not char.isalnum() and char != '_':
                break

            index += 1

        self._index = index
        return self._request[start:index]

    def format(self, query, minimized=None, spaces=None):
        """Format the query."""
        if minimized is None:
            minimized = self._minimized
        if spaces is None:
            spaces = self._spaces

        self._request = query
        self._length = len(query)

        result = ""
        indent_level = 0
        first_top_level_token = None
        self._tokens = self._tokenize()
        newline = False

        # count the depth of complex inputs
        complex_input_level = 0

        # iterate over the tokens with ability to jump forward
        index = -1
        while index + 1 < len(self._tokens):
            index += 1
            token = self._tokens[index]

            # process operation names (query, mutation, subscription) and 'fragment' keyword
            # operation names only have special meaning at the top level and only if they are the first token
            if indent_level == 0:
                if not first_top_level_token:
                    result += '\n\n'

                    first_top_level_token = token

                    if token in ('query', 'mutation', 'subscription'):
                        result += token + ' '
                        newline = False
                        continue

                    if token == 'fragment':
                        # fragment A on B { ... }
                        if index + 3 < len(self._tokens) and self._tokens[index+2] == 'on':
                            result += 'fragment ' + self._tokens[index+1] + ' on ' + self._tokens[index+3]
                            index += 3
                            newline = False
                            continue

            else:
                first_top_level_token = None

            # check for the start of a block
            if token == '{':
                # '{' is also used for complex input variables and it shouldn't be followed by newline in that case
                if complex_input_level:
                    complex_input_level += 1
                    result += token + ' '
                    newline = False
                    continue

                if index and self._tokens[index-1] in (':', '='):
                    complex_input_level = 1
                    result += token + ' '
                    newline = False
                    continue

                # if the previous line was a comment, we need to add a newline before the block
                if index and self._tokens[index-1][0] == '#':
                    result += '\n' + ' ' * (indent_level * spaces)

                indent_level += 1

                # '{' should be separated from the previous token by a space, but it might have been added already
                if len(result) > 0 and not result[-1].isspace():
                    result += ' '
                result += token + '\n' + ' ' * (indent_level * spaces)
                newline = False
                continue
            # check for the end of a block
            elif token == '}':
                if complex_input_level:
                    complex_input_level -= 1
                    result += ' ' + token
                    newline = False
                    continue

                indent_level -= 1
                result += '\n' + ' ' * (indent_level * spaces) + token
                newline = True
                continue
            # check for the tokens that has to be followed by a space
            elif token in (',', ':'):
                result += token + ' '
                newline = False
                continue
            # check for the tokens that has to be preceded by a space
            elif token == '@':
                result += ' ' + token
                newline = False
                continue
            # '...' has complex rules, so we'll handle it separately
            elif token == '...':
                # inline fragments are used like this:
                #   ... on User
                # regular fragments are used like this (fragment name can not be 'on'):
                #   ...UserFragment
                if newline:
                    result += '\n' + ' ' * (indent_level * spaces)

                newline = False
                if self._tokens[index+1] == 'on':
                    result += '... on '
                    index += 1
                    continue
                else:
                    result += '...'
                    continue
            # tokens that need to be surrounded by spaces
            elif token in ('=', '|'):
                result += ' ' + token + ' '
                newline = False
                continue
            # tokens that are used as is (no spaces)
            elif token in ('$', '!', '(', '[', ']'):
                result += token
                newline = False
                continue
            # ')' needs special handling - it doesn't need a space, but it could indicate the end of a line
            elif token == ')':
                newline = True
                result += token
                continue
            elif token[0] == '#':
                # newline at the end of the comment is a hack to signalize that it's a whole line comment
                if token[-1] == '\n':
                    if newline:
                        if len(result) and result[-1] != '\n':
                            # whole line comment, add a newline before
                            result += '\n' + ' ' * (indent_level * spaces) + token[:-1]
                        else:
                            # whole line comment, but there is a newline already
                            result += ' ' * (indent_level * spaces) + token[:-1]
                    else:
                        # whole line comment, but the newline has been handled already
                        result += token[:-1]
                else:
                    # inline comment, no newline but add a space before
                    result += ' ' + token
                newline = True
                continue
            else:
                print("token: |" + token + "|")
                if newline:
                    result += '\n' + ' ' * (indent_level * spaces) + token
                else:
                    result += token
                newline = True
                continue

        return result.strip()
