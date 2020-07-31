#! /usr/bin/env python

"""pandoc-secnos: a pandoc filter that inserts section references."""


__version__ = '2.2.2'


# Copyright 2015-2020 Thomas J. Duck.
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# OVERVIEW
#
# The basic idea is to scan the document twice in order to:
#
#   1. Obtain the labels for each section.
#
#   2. Replace each reference with a section number.  For LaTeX,
#      replace with \ref{...} instead.
#
# This is followed by injecting header code as needed for certain output
# formats.

# pylint: disable=invalid-name, global-statement

import re
import functools
import argparse
import json
import copy
import textwrap

from pandocfilters import walk, Span

import pandocxnos
from pandocxnos import STRTYPES, STDIN, STDOUT, STDERR
from pandocxnos import check_bool, get_meta
from pandocxnos import repair_refs, process_refs_factory, replace_refs_factory
from pandocxnos import attach_attrs_factory

# Read the command-line arguments
parser = argparse.ArgumentParser(description='Pandoc section numbers filter.')
parser.add_argument('--version', action='version',
                    version='%(prog)s {version}'.format(version=__version__))
parser.add_argument('fmt')
parser.add_argument('--pandocversion', help='The pandoc version.')
args = parser.parse_args()

# Patterns for matching labels and references
LABEL_PATTERN = re.compile(r'(sec:[\w/-]*)')

# Meta variables; may be reset elsewhere
cleveref = False    # Flags that clever references should be used
capitalise = False  # Flags that plusname should be capitalised
# Sets names for mid-sentence references
plusname = {'section': ['section', 'sections'],
            'chapter': ['chapter', 'chapters']}
# Sets names for refs at sentence start
starname = {'section': ['Section', 'Sections'],
            'chapter': ['Chapter', 'Chapters']}
secoffset = 0           # Section number offset
warninglevel = 2        # 0 - no warnings; 1 - some warnings; 2 - all warnings

# Processing state variables
sec = []      # Section number tracker
targets = {}  # Global targets tracker

# Processing flags
# Flags that the plus name changed
plusname_changed = {'section': False, 'chapter': False}
# Flags that the star name changed
starname_changed = {'section': False, 'chapter': False}

PANDOCVERSION = None


# Actions --------------------------------------------------------------------

def process_sections(key, value, fmt, meta):  # pylint: disable=unused-argument
    """Processes sections."""

    global sec

    if key == 'Header':
        if 'unnumbered' in value[1][1]:
            return

        # Update the section number
        level = value[0]
        assert level
        if not sec:
            sec = [secoffset]
        while len(sec) < level:
            sec.append(0)
        if len(sec) > level:
            sec = sec[:level]
        assert len(sec) == level
        sec[level-1] += 1

        # Add new item to the targets tracker
        targets[value[1][0]] = \
          pandocxnos.Target('.'.join(str(i) for i in sec), None,
                            value[1][0] in targets)


# TeX blocks -----------------------------------------------------------------

# Section number offset
SECOFFSET_TEX = r"""
%% pandoc-secnos: section number offset
\setcounter{section}{%s}
"""


# Main program ---------------------------------------------------------------

def set_name(nametype, division, value):
    """Sets the name on a given division."""

    global plusname_changed  # Flags that the plus name changed
    global starname_changed  # Flags that the star name changed

    isplusname = nametype == 'plus'

    old_name = copy.deepcopy(plusname if isplusname else starname)
    name = plusname if isplusname else starname
    name_changed = plusname_changed if isplusname else starname_changed

    if isinstance(value, list):  # Singular and plural forms given
        name[division] = value
    else:  # Only the singular form was given
        name[division][0] = value
    name_changed[division] = name[division] != old_name[division]
    assert len(name[division]) == 2
    for x in name[division]:
        assert isinstance(x, STRTYPES)
    if isplusname and name_changed[division]:
        starname[division] = \
          [x.title() for x in name[division]]

# pylint: disable=too-many-statements, too-many-branches
def process(meta):
    """Saves metadata fields in global variables and returns a few
    computed fields."""

    # pylint: disable=global-statement
    global cleveref      # Flags that clever references should be used
    global capitalise    # Flags that plusname should be capitalised
    global plusname      # Sets names for mid-sentence references
    global starname      # Sets names for references at sentence start
    global secoffset     # Section number offset
    global warninglevel  # 0 - no warnings; 1 - some; 2 - all

    # Read in the metadata fields and do some checking

    for name in ['secnos-warning-level', 'xnos-warning-level']:
        if name in meta:
            warninglevel = int(get_meta(meta, name))
            pandocxnos.set_warning_level(warninglevel)
            break

    metanames = ['secnos-warning-level', 'xnos-warning-level',
                 'secnos-cleveref', 'xnos-cleveref',
                 'xnos-capitalise', 'xnos-capitalize',
                 'xnos-caption-separator', # Used by pandoc-fignos/tablenos
                 'secnos-plus-name', 'secnos-star-name',
                 'xnos-number-by-section', 'xnos-number-offset']

    if warninglevel:
        for name in meta:
            if (name.startswith('secnos') or name.startswith('xnos')) and \
              name not in metanames:
                msg = textwrap.dedent("""
                          pandoc-secnos: unknown meta variable "%s"\n
                      """ % name)
                STDERR.write(msg)

    for name in ['secnos-cleveref', 'xnos-cleveref']:
        # 'xnos-cleveref' enables cleveref in all four of
        # fignos/eqnos/tablenos/secnos
        if name in meta:
            cleveref = check_bool(get_meta(meta, name))
            break

    for name in ['xnos-capitalise', 'xnos-capitalize']:
        # 'xnos-capitalise' enables capitalise in all four of
        # fignos/eqnos/tablenos/secnos.  Since this uses an option in the
        # caption package, it is not possible to select between the three (use
        # 'secnos-plus-name' instead.  'xnos-capitalize' is an alternative
        # spelling
        if name in meta:
            capitalise = check_bool(get_meta(meta, name))
            break

    if 'secnos-plus-name' in meta:

        value = get_meta(meta, 'secnos-plus-name')

        if isinstance(value, str):
            try:
                value_ = \
                  dict(itemstr.split(':') for itemstr in value.split(','))
                for division in value_:
                    set_name('plus', division, value_[division])
            except ValueError:
                set_name('plus', 'section', value)
        else:  # Dict expected
            for division in value:
                set_name('plus', division, value[division])

    if 'secnos-star-name' in meta:

        value = get_meta(meta, 'secnos-star-name')

        if isinstance(value, str):
            try:
                value_ = \
                  dict(itemstr.split(':') for itemstr in value.split(','))
                for division in value_:
                    set_name('star', division, value_[division])
            except ValueError:
                set_name('star', 'section', value)
        else:  # Dict expected
            for division in value:
                set_name('star', division, value[division])

    if 'xnos-number-offset' in meta:
        secoffset = int(get_meta(meta, 'xnos-number-offset'))


def add_tex(meta):
    """Adds tex to the meta data."""

    warnings = warninglevel == 2 and targets and \
      (pandocxnos.cleveref_required() or
       any(plusname_changed.values()) or any(starname_changed.values()) or \
       secoffset)
    if warnings:
        msg = textwrap.dedent("""\
                  pandoc-secnos: Wrote the following blocks to
                  header-includes.  If you use pandoc's
                  --include-in-header option then you will need to
                  manually include these yourself.
              """)
        STDERR.write('\n')
        STDERR.write(textwrap.fill(msg))
        STDERR.write('\n')

    # Update the header-includes metadata.  Pandoc's
    # --include-in-header option will override anything we do here.  This
    # is a known issue and is owing to a design decision in pandoc.
    # See https://github.com/jgm/pandoc/issues/3139.

    if pandocxnos.cleveref_required() and targets:
        tex = """
            %%%% pandoc-secnos: required package
            \\usepackage%s{cleveref}
        """ % ('[capitalise]' if capitalise else '')
        pandocxnos.add_to_header_includes(
            meta, 'tex', tex,
            regex=r'\\usepackage(\[[\w\s,]*\])?\{cleveref\}')

    if plusname_changed['section'] and targets:
        tex = """
            %%%% pandoc-secnos: change cref names
            \\crefname{section}{%s}{%s}
        """ % (plusname['section'][0], plusname['section'][1])
        pandocxnos.add_to_header_includes(meta, 'tex', tex)

    if plusname_changed['chapter'] and targets:
        tex = """
            %%%% pandoc-secnos: change cref names
            \\crefname{chapter}{%s}{%s}
        """ % (plusname['chapter'][0], plusname['chapter'][1])
        pandocxnos.add_to_header_includes(meta, 'tex', tex)

    if starname_changed['section'] and targets:
        tex = """
            %%%% pandoc-secnos: change Cref names
            \\Crefname{section}{%s}{%s}
        """ % (starname['section'][0], starname['section'][1])
        pandocxnos.add_to_header_includes(meta, 'tex', tex)

    if starname_changed['chapter'] and targets:
        tex = """
            %%%% pandoc-secnos: change Cref names
            \\Crefname{chapter}{%s}{%s}
        """ % (starname['chapter'][0], starname['chapter'][1])
        pandocxnos.add_to_header_includes(meta, 'tex', tex)

    if secoffset and targets:
        pandocxnos.add_to_header_includes(
            meta, 'tex', SECOFFSET_TEX % secoffset,
            regex=r'\\setcounter\{section\}')

    if warnings:
        STDERR.write('\n')

# pylint: disable=too-many-locals, unused-argument
def main(stdin=STDIN, stdout=STDOUT, stderr=STDERR):
    """Filters the document AST."""

    # pylint: disable=global-statement
    global PANDOCVERSION

    # Get the output format and document
    fmt = args.fmt
    doc = json.loads(stdin.read())

    # Initialize pandocxnos
    PANDOCVERSION = pandocxnos.init(args.pandocversion, doc)

    # Chop up the doc
    meta = doc['meta'] if PANDOCVERSION >= '1.18' else doc[0]['unMeta']
    blocks = doc['blocks'] if PANDOCVERSION >= '1.18' else doc[1:]

    # Process the metadata variables
    process(meta)

    # First pass
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [process_sections], blocks)

    # Second pass
    process_refs = process_refs_factory(LABEL_PATTERN, targets.keys())
    replace_refs = \
      replace_refs_factory(targets, cleveref, False,
                           plusname['section'] if not capitalise or \
                           plusname_changed['section'] else \
                           [name.title() for name in plusname['section']],
                           starname['section'], allow_implicit_refs=True)
    attach_attrs_span = attach_attrs_factory(Span, replace=True)
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [repair_refs, process_refs, replace_refs,
                                attach_attrs_span],
                               altered)

    if fmt in ['latex', 'beamer']:
        add_tex(meta)

    # Update the doc
    if PANDOCVERSION >= '1.18':
        doc['blocks'] = altered
    else:
        doc = doc[:1] + altered

    # Dump the results
    json.dump(doc, stdout)

    # Flush stdout
    stdout.flush()

if __name__ == '__main__':
    main()
