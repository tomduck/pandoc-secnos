
**New in 2.1.0:** Warnings are now given for duplicate reference targets.

[more...](#whats-new)


pandoc-secnos 2.1.0
===================

*pandoc-secnos* is a [pandoc] filter for numbering section references when converting markdown to other formats.  It is part of the [pandoc-xnos] filter suite.  LaTeX/pdf, html, and epub output have native support.  Native support for docx output is a work in progress.

Demonstration: Processing [demo3.md] with pandoc + pandoc-secos gives numbered section references in [pdf][pdf3], [tex][tex3], [html][html3], [epub][epub3], [docx][docx3] and other formats.

This version of pandoc-secnos was tested using pandoc 1.15.2 - 2.7.3,<sup>[1](#footnote1)</sup> and may be used with linux, macOS, and Windows. Bug reports and feature requests may be posted on the project's [Issues tracker].  If you find pandoc-secnos useful, then please kindly give it a star [on GitHub].

See also: [pandoc-fignos], [pandoc-eqnos], [pandoc-tablenos] \
Other filters: [pandoc-comments], [pandoc-latex-extensions]

[pandoc]: http://pandoc.org/
[pandoc-xnos]: https://github.com/tomduck/pandoc-xnos
[Issues tracker]: https://github.com/tomduck/pandoc-secnos/issues
[on GitHub]:  https://github.com/tomduck/pandoc-secnos
[pandoc-fignos]: https://github.com/tomduck/pandoc-fignos
[pandoc-eqnos]: https://github.com/tomduck/pandoc-eqnos
[pandoc-tablenos]: https://github.com/tomduck/pandoc-tablenos
[pandoc-comments]: https://github.com/tomduck/pandoc-comments
[pandoc-latex-extensions]: https://github.com/tomduck/pandoc-latex-extensions


Contents
--------

 1. [Installation](#installation)
 2. [Usage](#usage)
 3. [Markdown Syntax](#markdown-syntax)
 4. [Customization](#customization)
 5. [Technical Details](#technical-details)
 6. [Getting Help](#getting-help)
 7. [Development](#development)
 8. [What's New](#whats-new)


Installation
------------

Pandoc-secnos requires [python], a programming language that comes pre-installed on macOS and linux.  It is easily installed on Windows -- see [here](https://realpython.com/installing-python/).  Either python 2.7 or 3.x will do.

Pandoc-secnos may be installed using the shell command

    pip install pandoc-secnos --user

and upgrade by appending `--upgrade` to the above command.  Pip is a program that downloads and installs software from the Python Package Index, [PyPI].  It normally comes installed with a python distribution.<sup>[2](#footnote2)</sup>

Instructions for installing from source are given in [DEVELOPERS.md].

[python]: https://www.python.org/
[PyPI]: https://pypi.python.org/pypi
[DEVELOPERS.md]: DEVELOPERS.md


Usage
-----

Pandoc-secnos is activated by using the

    --filter pandoc-secnos

option with pandoc.  Alternatively, use

    --filter pandoc-xnos

to activate all of the filters in the [pandoc-xnos] suite (if installed).

Any use of `--filter pandoc-citeproc` or `--bibliography=FILE` should come *after* the `pandoc-secnos` or `pandoc-xnos` filter calls.


Markdown Syntax
---------------

The cross-referencing syntax used by pandoc-secnos was developed in [pandoc Issue #813] -- see [this post] by [@scaramouche1].

For LaTeX/pdf, html, and epub output, sections are numbered using     pandoc's `--number-sections` [option](https://pandoc.org/MANUAL.html#option--number-sections).

To reference a section, use

    @sec:id

or

    {@sec:id}

The prefix `@sec:` is required. `id` should be replaced with a unique identifier for the section, composed of letters, numbers, dashes and underscores.  Curly braces protect a reference and are stripped from the output.

Pandoc automatically assigns an identifier to each section title in a document.  For example, the identifier for

    Section One
    ===========

is `section-one`; a reference to it would be `@sec:section-one`.  An identifier may be explicitly assigned to the section title using attributes as follows:

    Section Two {#sec:2}
    ===========

A reference to this would be `@sec:2`.

Demonstration: Processing [demo.md] with pandoc + pandoc-secnos gives numbered section references in [pdf], [tex], [html], [epub], [docx] and other formats.

[pandoc Issue #813]: https://github.com/jgm/pandoc/issues/813
[this post]: https://github.com/jgm/pandoc/issues/813#issuecomment-70423503
[@scaramouche1]: https://github.com/scaramouche1
[reference link]: http://pandoc.org/MANUAL.html#reference-links
[demo.md]: https://raw.githubusercontent.com/tomduck/pandoc-secnos/master/demos/demo.md
[pdf]: https://raw.githack.com/tomduck/pandoc-secnos/demos/demo.pdf
[tex]: https://raw.githack.com/tomduck/pandoc-secnos/demos/demo.tex
[html]: https://raw.githack.com/tomduck/pandoc-secnos/demos/demo.html
[epub]: https://raw.githack.com/tomduck/pandoc-secnos/demos/demo.epub
[docx]: https://raw.githack.com/tomduck/pandoc-secnos/demos/demo.docx


### Clever References ###

Writing markdown like

    See sec. @sec:id.

seems a bit redundant.  Pandoc-secnos supports "clever references" via single-character modifiers in front of a reference.  Users may write

     See +@sec:id.

to have the reference name (i.e., "section") automatically generated.  The above form is used mid-sentence; at the beginning of a sentence, use

     *@sec:id

instead.  If clever references are enabled by default (see [Customization](#customization), below), then users may disable it for a given reference using<sup>[3](#footnote3)</sup>

    !@sec:id

Demonstration: Processing [demo2.md] with pandoc + pandoc-secnos gives numbered section references in [pdf][pdf2], [tex][tex2], [html][html2], [epub][epub2], [docx][docx2] and other formats.

Note: When using `*sec:id` and emphasis (e.g., `*italics*`) in the same sentence, the `*` in the clever reference must be backslash-escaped; i.e., `\*sec:id`.

[demo2.md]: https://raw.githubusercontent.com/tomduck/pandoc-secnos/master/demos/demo2.md
[pdf2]: https://raw.githack.com/tomduck/pandoc-secnos/demos/demo2.pdf
[tex2]: https://raw.githack.com/tomduck/pandoc-secnos/demos/demo2.tex
[html2]: https://raw.githack.com/tomduck/pandoc-secnos/demos/demo2.html
[epub2]: https://raw.githack.com/tomduck/pandoc-secnos/demos/demo2.epub
[docx2]: https://raw.githack.com/tomduck/pandoc-secnos/demos/demo2.docx


### Disabling Links ###

To disable a link on a reference, set `nolink=True` in the reference's attributes:

    @sec:id{nolink=True}


Customization
-------------

Pandoc-secnos may be customized by setting variables in the [metadata block] or on the command line (using `-M KEY=VAL`).  The following variables are supported:

  * `secnos-warning-level` or `xnos-warning-level` - Set to `0` for
    no warnings, `1` for critical warnings, or `2` (default) for
    all warnings.  Warning level 2 should be used when
    troubleshooting.

  * `secnos-cleveref` or `xnos-cleveref` - Set to `True` to assume "+"
    clever references by default;

  * `xnos-capitalise` - Capitalises the names of "+" clever
    references (e.g., change from "section" to "Section");

  * `secnos-plus-name` - Sets the name of a "+" clever reference
    (e.g., change it from "section" to "sec.").  Settings here take
    precedence over `xnos-capitalise`;

  * `secnos-star-name` - Sets the name of a "*" clever reference
    (e.g., change it from "Section" to "Sec.");

  * `xnos-number-offset` - Set to an integer to offset the section
    numbers in references.  For html and epub output, this feature
    should be used together with pandoc's
    `--number-offset`
    [option](https://pandoc.org/MANUAL.html#option--number-sections)
    set to the same integer value.  For LaTeX/PDF, this option
    offsets the actual section numbers as required.


Note that variables beginning with `secnos-` apply to only pandoc-secnos, whereas variables beginning with `xnos-` apply to all all of the pandoc-fignos/eqnos/tablenos/secnos filters.

Demonstration: Processing [demo3.md] with pandoc + pandoc-secnos gives numbered section references in [pdf][pdf3], [tex][tex3], [html][html3], [epub][epub3], [docx][docx3] and other formats.

[metadata block]: http://pandoc.org/README.html#extension-yaml_metadata_block
[demo3.md]: https://raw.githubusercontent.com/tomduck/pandoc-secnos/master/demos/demo3.md
[pdf3]: https://raw.githack.com/tomduck/pandoc-secnos/demos/demo3.pdf
[tex3]: https://raw.githack.com/tomduck/pandoc-secnos/demos/demo3.tex
[html3]: https://raw.githack.com/tomduck/pandoc-secnos/demos/demo3.html
[epub3]: https://raw.githack.com/tomduck/pandoc-secnos/demos/demo3.epub
[docx3]: https://raw.githack.com/tomduck/pandoc-secnos/demos/demo3.docx


Technical Details
-----------------

### TeX/pdf Output ###

During processing, pandoc-secnos inserts packages and supporting TeX into the `header-includes` metadata field.  To see what is inserted, set the `secnos-warning-level` meta variable to `2`.  Note that any use of pandoc's `--include-in-header` option [overrides](https://github.com/jgm/pandoc/issues/3139) all `header-includes`.

An example reference in TeX looks like

~~~latex
See \cref{sec:1}.
~~~

Other details:

  * The `cleveref` and `caption` packages are used for clever
    references and caption control, respectively; 
  * The `\label` and `\ref` macros are used for section labels and
    references, respectively (`\Cref` and `\cref` are used for
    clever references);
  * Clever reference names are set with `\Crefname` and `\crefname`;


### Html/Epub Output ###

An example reference in html looks like

~~~html
See section <a href="#sec:1">1</a>.
~~~


### Docx Output ###

Docx OOXML output is under development and subject to change.  Native capabilities will be used wherever possible.


Getting Help
------------

If you have any difficulties with pandoc-secnos, or would like to see a new feature, then please submit a report to our [Issues tracker].


Development
-----------

Pandoc-secnos will continue to support pandoc 1.15-onward and python 2 & 3 for the foreseeable future.  The reasons for this are that a) some users cannot upgrade pandoc and/or python; and b) supporting all versions tends to make pandoc-secnos more robust.

Developer notes are maintained in [DEVELOPERS.md].


What's New
----------

**New in 2.1.0:** Warnings are now given for duplicate reference targets.

**New in 2.0.0:**  Pandoc-secnos is a new filter.  It has been makred with version number 2.0.0 in keeping with the major version number of the underlying pandoc-xnos library.


----

**Footnotes**

<a name="footnote1">1</a>: Pandoc 2.4 [broke](https://github.com/jgm/pandoc/issues/5099) how references are parsed, and so is not supported.

<a name="footnote2">2</a>: Anaconda users may be tempted to use `conda` instead.  This is not advised.  The packages distributed on the Anaconda cloud are unofficial, are not posted by me, and in some cases are ancient.  Some tips on using `pip` in a `conda` environment may be found [here](https://www.anaconda.com/using-pip-in-a-conda-environment/).

<a name="footnote3">3</a>: The disabling modifier "!" is used instead of "-" because [pandoc unnecessarily drops minus signs] in front of references.

[pandoc unnecessarily drops minus signs]: https://github.com/jgm/pandoc/issues/2901
