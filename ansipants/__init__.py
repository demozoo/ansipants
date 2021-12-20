from collections import namedtuple
from html import escape


COLORS = {
    False: ['000', 'a00', '0a0', 'a50', '00a', 'a0a', '0aa', 'aaa'],
    True: ['555', 'f55', '5f5', 'ff5', '55f', 'f5f', '5ff', 'fff'],
}

# Low ASCII codes that correspond to printable characters in CP437.
# Python apparently doesn't remap these to the relevant Unicode points
# when decoding cp437, so we have to do it ourselves...
REMAPPED_CHARS = {
    '\x00': ' ',
    '\x01': '\u263a',
    '\x02': '\u263b',
    '\x03': '\u2665',
    '\x04': '\u2666',
    '\x05': '\u2663',
    '\x06': '\u2660',
    '\x10': '\u25ba',
    '\x11': '\u25c4',
    '\x1d': '\u2194',
    '\x1e': '\u25b2',
    '\x1f': '\u25bc',
}

DEFAULT_FG = 7
DEFAULT_BG = 0

BaseAttribute = namedtuple('Attribute', ['fg', 'bg', 'bright', 'underline'])


class Attribute(BaseAttribute):
    @property
    def css_style(self):
        fg = COLORS[self.bright][self.fg]
        styles = ['color: #%s;' % fg]
        if self.bg != DEFAULT_BG:
            bg = COLORS[False][self.bg]
            styles.append('background-color: #%s;' % bg)
        if self.underline:
            styles.append('text-decoration: underline;')
        return ' '.join(styles)


DEFAULT_ATTR = Attribute(fg=DEFAULT_FG, bg=DEFAULT_BG, bright=False, underline=False)


class ANSIDecodeError(ValueError):
    pass


class ANSIDecoder:
    def __init__(self, stream=None, width=80, strict=False):
        self.current_line = []
        self.buffer = [self.current_line]
        self.x = 0
        self.y = 0
        self.saved_x = 0
        self.saved_y = 0
        self.current_attr = DEFAULT_ATTR
        self.width = width
        self.strict = strict

        if stream:
            self.play(stream)

    def write_char(self, char):
        # Handle an ordinary character
        try:
            self.current_line[self.x] = (self.current_attr, char)
        except IndexError:
            # X position is out of range; append to current line
            while len(self.current_line) < self.x:
                self.current_line.append((DEFAULT_ATTR, ' '))
            self.current_line.append((self.current_attr, char))

        self.x += 1
        if self.x >= self.width:
            self.write_newline()

    def set_cursor(self, x=None, y=None):
        if x is not None:
            self.x = max(x, 0)
        if y is not None:
            self.y = max(y, 0)

        try:
            self.current_line = self.buffer[self.y]
        except IndexError:
            while len(self.buffer) <= self.y:
                self.current_line = []
                self.buffer.append(self.current_line)

    def write_newline(self):
        # Handle a line break
        self.set_cursor(x=0, y=(self.y + 1))

    def set_attr(self, fg=None, bg=None, bright=None, underline=None):
        if fg is None:
            fg = self.current_attr.fg
        if bg is None:
            bg = self.current_attr.bg
        if bright is None:
            bright = self.current_attr.bright
        if underline is None:
            underline = self.current_attr.underline

        self.current_attr = Attribute(fg=fg, bg=bg, bright=bright, underline=underline)

    def write_escape(self, code, params):
        if code == 'm':
            for param in params:
                if param == 0:
                    self.current_attr = DEFAULT_ATTR
                elif param == 1:
                    self.set_attr(bright=True)
                elif param == 2 or param == 22:
                    self.set_attr(bright=False)
                elif param == 4:
                    self.set_attr(underline=True)
                elif param == 24:
                    self.set_attr(underline=False)
                elif 30 <= param <= 37:
                    self.set_attr(fg=(param - 30))
                elif 40 <= param <= 47:
                    self.set_attr(bg=(param - 40))
                else:
                    if self.strict:
                        raise ANSIDecodeError("Unsupported parameter to 'm' escape sequence: %r" % param)
        elif code == 'J':
            if params == [] or params == [0]:
                # erase from cursor to end of screen
                del self.current_line[self.x:]
                del self.buffer[(self.y + 1):]
            elif params == [1]:
                # erase up to cursor
                for i in range(0, self.y):
                    del self.buffer[i][:]
                try:
                    for i in range(0, self.x + 1):
                        self.current_line[i] = (DEFAULT_ATTR, ' ')
                except IndexError:
                    del self.current_line[:]
            elif params == [2]:
                # erase entire screen
                for i in range(0, self.y):
                    del self.buffer[i][:]
                del self.buffer[(self.y + 1):]
            else:
                if self.strict:
                    raise ANSIDecodeError("Unrecognised parameters to 'J' escape sequence: %r" % params)
        elif code == 'K':
            if params == [] or params == [0]:
                # erase from cursor to end of line
                del self.current_line[self.x:]
            elif params == [1]:
                # erase up to cursor
                try:
                    for i in range(0, self.x + 1):
                        self.current_line[i] = (DEFAULT_ATTR, ' ')
                except IndexError:
                    del self.current_line[:]
            elif params == [2]:
                # erase entire line
                del self.current_line[:]
            else:
                if self.strict:
                    raise ANSIDecodeError("Unrecognised parameters to 'K' escape sequence: %r" % params)

        elif code == 'A':
            # move cursor up N lines
            if not params:
                self.set_cursor(y=(self.y - 1))
            elif len(params) == 1:
                self.set_cursor(y=(self.y - params[0]))
            elif self.strict:
                raise ANSIDecodeError("Expected 0 or 1 param to 'A' escape sequence, got %d" % len(params))

        elif code == 'B':
            # move cursor down N lines
            if not params:
                self.set_cursor(y=(self.y + 1))
            elif len(params) == 1:
                self.set_cursor(y=(self.y + params[0]))
            elif self.strict:
                raise ANSIDecodeError("Expected 0 or 1 param to 'B' escape sequence, got %d" % len(params))

        elif code == 'C':
            # move cursor right N cols
            if not params:
                self.set_cursor(x=(self.x + 1))
            elif len(params) == 1:
                self.set_cursor(x=(self.x + params[0]))
            elif self.strict:
                raise ANSIDecodeError("Expected 0 or 1 param to 'C' escape sequence, got %d" % len(params))

        elif code == 'D':
            # move cursor left N cols
            if not params:
                self.set_cursor(x=(self.x - 1))
            elif len(params) == 1:
                self.set_cursor(x=(self.x - params[0]))
            elif self.strict:
                raise ANSIDecodeError("Expected 0 or 1 param to 'D' escape sequence, got %d" % len(params))

        elif code == 'E':
            # move cursor to beginning of next line, N lines down
            if not params:
                self.set_cursor(x=0, y=(self.y + 1))
            elif len(params) == 1:
                self.set_cursor(x=0, y=(self.y + params[0]))
            elif self.strict:
                raise ANSIDecodeError("Expected 0 or 1 param to 'E' escape sequence, got %d" % len(params))

        elif code == 'F':
            # move cursor to beginning of previous line, N lines up
            if not params:
                self.set_cursor(x=0, y=(self.y - 1))
            elif len(params) == 1:
                self.set_cursor(x=0, y=(self.y - params[0]))
            elif self.strict:
                raise ANSIDecodeError("Expected 0 or 1 param to 'F' escape sequence, got %d" % len(params))

        elif code == 'G':
            # move cursor to column N
            if len(params) == 1:
                self.set_cursor(x=params[0])
            elif self.strict:
                raise ANSIDecodeError("Expected 1 param to 'G' escape sequence, got %d" % len(params))

        elif code == 'H' or code == 'f':
            # move cursor to (line, col)
            if not params:
                self.set_cursor(x=0, y=0)
            elif len(params) == 2:
                self.set_cursor(x=params[1] - 1, y=params[0] - 1)
            elif self.strict:
                raise ANSIDecodeError("Expected 0 or 2 param to '%s' escape sequence, got %d" % (code, len(params)))

        elif code == 'h':
            if params == [7]:
                # enable line wrapping
                pass
            elif self.strict:
                raise ANSIDecodeError("Unrecognised params to 'h' - got %r" % params)

        elif code == 's':
            # save cursor position
            if params and self.strict:
                raise ANSIDecodeError("Unrecognised params to 's' - got %r" % params)
            self.saved_x = self.x
            self.saved_y = self.y

        elif code == 'u':
            # restore cursor position
            if params and self.strict:
                raise ANSIDecodeError("Unrecognised params to 'u' - got %r" % params)
            self.set_cursor(x=self.saved_x, y=self.saved_y)

        else:
            if self.strict:
                raise ANSIDecodeError("Unrecognised escape code: %r" % code)

    def play(self, f):
        while True:
            # Read file a character at a time
            char = f.read(1)
            if not char:
                # End of file
                break

            elif char >= ' ':
                self.write_char(char)

            elif char == '\x0a':  # LF
                self.write_newline()

            elif char == '\x0d':  # CR
                continue

            elif char in REMAPPED_CHARS:
                self.write_char(REMAPPED_CHARS[char])

            elif char == '\x1a':
                # EOF when using SAUCE records
                break

            elif char == '\x1b':
                # Handle an escape sequence
                char = f.read(1)
                # Next character is expected to be '['
                if char != '[':
                    if self.strict:
                        raise ANSIDecodeError("Unrecognised character after ESC: %r" % char)
                    continue

                params = []
                param = None
                private = False
                while True:
                    char = f.read(1)
                    if '0' <= char <= '9':
                        if param is None:
                            param = int(char)
                        else:
                            param = param * 10 + int(char)
                    elif char == ';':
                        if param is None:
                            if self.strict:
                                raise ANSIDecodeError("Encountered ';' character without parameter")
                        else:
                            params.append(param)
                            param = None
                    elif char == ' ':
                        pass
                    elif char == '?':
                        private = True
                    else:
                        if param is not None:
                            params.append(param)

                        if not private:
                            self.write_escape(char, params)
                        break

            elif self.strict:
                raise ANSIDecodeError("Unrecognised character: %r" % char)

    def as_html_lines(self):
        for line in self.buffer:
            last_attr = None
            spans = []
            current_span_chars = []
            for (attr, char) in line:
                if attr != last_attr:
                    # close the last span, if any
                    if current_span_chars:
                        spans.append((last_attr, ''.join(current_span_chars)))
                    # start a new span
                    last_attr = attr
                    current_span_chars = []
                current_span_chars.append(char)

            # close the last span, if any
            if current_span_chars:
                spans.append((last_attr, ''.join(current_span_chars)))

            output_line = ''
            for (attr, text) in spans:
                output_line += (
                    '<span style="%s">%s</span>' % (escape(attr.css_style), escape(text, quote=False))
                )
            yield output_line

    def as_html(self):
        output_lines = list(self.as_html_lines())
        return '\n'.join(output_lines)
