# ansipants

A Python module and command-line utility for converting .ANS format ANSI art to HTML.

## Installation

    pip install ansipants

## Command-line usage

    python -m ansipants input.ans > output.html

For additional options, run `python -m ansipants --help`.

The output is a fragment of HTML, in UTF-8 encoding, intended to be inserted into a preformatted text element such as `<pre style="background-color: #000;">...</pre>`. Further styling is up to you - for the proper MS-DOS experience, [The Ultimate Oldschool PC Font Pack by VileR](https://int10h.org/oldschool-pc-fonts/) is recommended.

## Python API

Example code:

```python
from ansipants import ANSIDecoder

with open('input.ans', 'rt', encoding='cp437') as f:
    decoder = ANSIDecoder(f)

print(decoder.as_html())
```

class **ansipants.ANSIDecoder**_(stream=None, width=80, strict=False)_

Parameters:

* `stream` - the ANSI input data as a file-like object. This should be opened for reading in text mode, which means you'll need to specify the appropriate encoding - for ANSI art created for DOS this will most likely be `cp437`.
* `width` - the number of columns the text should wrap at
* `strict` - If True, the decoder will raise an `ansipants.ANSIDecodeError` exception on any unrecognised or malformed escape codes; if False, it will skip past them.

**ANSIDecoder.as_html**_()_

Returns the HTML output as a string.

**ANSIDecoder.as_html_lines**_()_

Returns the HTML output as an iterator, yielding one line at a time.


## Author

Matt Westcott matt@west.co.tt
