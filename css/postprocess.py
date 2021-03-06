#!/usr/bin/env python

#
#   This file is part of m.css.
#
#   Copyright © 2017 Vladimír Vondruš <mosra@centrum.cz>
#
#   Permission is hereby granted, free of charge, to any person obtaining a
#   copy of this software and associated documentation files (the "Software"),
#   to deal in the Software without restriction, including without limitation
#   the rights to use, copy, modify, merge, publish, distribute, sublicense,
#   and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included
#   in all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#   THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.
#

import argparse
import re
import os
import sys

import_rx = re.compile("^@import url\\('(?P<file>[^']+)'\\);$")
opening_brace_rx = re.compile("^\\s*:root\s*{\\s*$")
closing_brace_rx = re.compile("^\\s*}\\s*$")
comment_rx = re.compile("^\\s*(/\\*.*\\*/)?\\s*$")
comment_start_rx = re.compile("^\\s*(/\\*.*)\\s*$")
comment_end_rx = re.compile("^\\s*(.*\\*/)\\s*$")
variable_declaration_rx = re.compile("^\\s*(?P<key>--[a-z-]+)\\s*:\\s*(?P<value>[^;]+)\\s*;\\s*$")
variable_use_rx = re.compile("^(?P<before>.+)var\\((?P<key>--[a-z-]+)\\)(?P<after>.+)$")

def postprocess(files, process_imports, out_file):
    directory = os.path.dirname(files[0])

    if not out_file:
        basename, ext = os.path.splitext(files[0])
        out_file = basename + ".compiled" + ext

    with open(out_file, mode='w') as out:
        variables = {}
        imported_files = []

        not_just_variable_declarations = False

        # Put a helper comment and a license blob on top
        out.write("""/* Generated using `./postprocess.py {}`. Do not edit. */

/*
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
*/
""".format(' '.join(sys.argv[1:])))

        # Parse the top-level file
        with open(files[0]) as f:
            in_variable_declarations = False
            in_comment = False
            for line in f:
                # In comment and the comment is not ending yet, ignore
                if in_comment:
                    if comment_end_rx.match(line):
                        in_comment = False
                    continue

                # Import statement: add the file to additionally processed
                # files unless it's disabled
                match = import_rx.match(line)
                if match:
                    if process_imports:
                        imported_files += [match['file']]
                    continue

                # Opening brace of variable declaration block
                match = opening_brace_rx.match(line)
                if match:
                    in_variable_declarations = True
                    continue

                # Variable declaration
                match = variable_declaration_rx.match(line)
                if match and in_variable_declarations:
                    variables[match['key']] = match['value']
                    continue

                # Comment or empty line, ignore
                if comment_rx.match(line):
                    continue

                # Comment start line, ignore this and the next lines
                if comment_start_rx.match(line):
                    in_comment = True
                    continue

                # Closing brace of variable declaration block. If it was not
                # just variable declarations, put the closing brace to the
                # output as well.
                match = closing_brace_rx.match(line)
                if match and in_variable_declarations:
                    if not_just_variable_declarations: out.write("}\n")
                    in_variable_declarations = False
                    continue

                # Something else, copy verbatim to the output. If inside
                # variable declaration block, include also the opening brace
                # and remeber to put the closing brace there as well
                if in_variable_declarations:
                    out.write(":root {\n")
                    not_just_variable_declarations = True

                # Strip the trailing comment, if there, to save some bytes
                if line.rstrip().endswith('*/'):
                    out.write(line[:line.rindex('/*')])
                else:
                    out.write(line)

        # Now open the imported files and replace variables
        for file in imported_files + files[1:]:
            out.write('\n')

            with open(file) as f:
                in_comment = False
                for line in f:
                    # In comment and the comment is not ending yet, ignore
                    if in_comment:
                        if comment_end_rx.match(line):
                            in_comment = False
                        continue

                    # Variable use, replace with actual value
                    # TODO: more variables on the same line?
                    match = variable_use_rx.match(line)
                    if match and match['key'] in variables:
                        out.write(match['before'])
                        out.write(variables[match['key']])
                        out.write(match['after'])
                        out.write("\n")
                        continue

                    # Comment or empty line, ignore
                    if comment_rx.match(line):
                        continue

                    # Comment start line, ignore this and the next lines
                    if comment_start_rx.match(line):
                        in_comment = True
                        continue

                    # Something else, copy verbatim to the output. Strip the
                    # trailing comment, if there, to save some bytes
                    if line.rstrip().endswith('*/'):
                        out.write(line[:line.rindex('/*')].rstrip() + '\n')
                    else:
                        out.write(line)

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=r"""
Postprocessor for removing @import statements and variables from CSS files.

Combines all files into a new *.compiled.css file. The basename is taken
implicitly from the first argument. The -o option can override the output
filename.""")
    parser.add_argument('files', nargs='+', help="input CSS file(s)")
    parser.add_argument('--no-import', help="ignore @import statements", action='store_true')
    parser.add_argument('-o', '--output', help="output file", default='')
    args = parser.parse_args()

    exit(postprocess(args.files, not args.no_import, args.output))
