..
    This file is part of m.css.

    Copyright © 2017 Vladimír Vondruš <mosra@centrum.cz>

    Permission is hereby granted, free of charge, to any person obtaining a
    copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense,
    and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included
    in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.
..

Test
####

:save_as: pelican/theme/test/index.html
:breadcrumb: {filename}/pelican.rst Pelican
             {filename}/pelican/theme.rst Theme
:css: {filename}/static/dummy.css
      {filename}/static/dummy.css
:summary: um
:highlight: pelican/theme
:header:
    .. note-warning::

        This is a page header with an `internal link <{filename}/pelican.rst>`_.
        This shouldn't be wrapped in a ``<p>``.
:footer:
    .. note-danger::

        This is a page footer with an `internal link <{filename}/pelican.rst>`_.
        This shouldn't be wrapped in a ``<p>``.

This page should have a breadcrumb, summary in a meta tag, header and a footer
and also two additional links to ``/static/dummy.css``. It should also
highlight the Pelican Theme menu item in the top navbar.
