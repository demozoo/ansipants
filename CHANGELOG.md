Changelog
=========

0.1.2 (2021-12-20)
------------------

* Implement escape sequence for underline
* Ignore spaces in escape sequence arguments


0.1.1 (2021-12-06)
------------------

* Add support for printable characters with codepoints < 0x20
* Implement escape sequences for save/restore cursor
* Fix: Use correct colour palette as per http://answers.google.com/answers/threadview/id/126097.html
* Fix: Bright flag should not apply to background colour
* Fix: Fix 'move cursor' escape sequence to be 1-based rather than 0-based


0.1 (2021-12-06)
----------------

* Initial release
