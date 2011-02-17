`ikazuchi <https://bitbucket.org/t2y/ikazuchi>`_
helps to translate document using web translate APIs efficiently.
`ikazuchi` is intended to work with other tools since it's a CUI tool.

See the project `documentation <http://t2y.bitbucket.org/ikazuchi/build/html/index.html>`_ for more detail.


Features
========

* Translate GNU gettext catalog named PO file with good reference from web API
* Translate any string passed from command line argument
* Translate any string in Vim using ":pyfile" command
* Detect language of any string passed from command line argument


Setup
=====

by easy_install
----------------

Make environment::

   $ easy_install ikazuchi

by buildout
-----------

Make environment::

   $ hg clone https://t2y@bitbucket.org/t2y/ikazuchi
   $ cd ikazuchi
   $ python bootstrap.py
   $ bin/buildout


Usage
=====

Execute ikazuchi command::

    $ ikazuchi -s "i can translate"
    sentence:                i can translate
    translated(Google):      [Actually, translated sentence]

    $ ikazuchi -d -s "hello"
    sentence:                hello
    detect(Google):          en

All command option are::

    $ ikazuchi -h
    Usage: ikazuchi [options]

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -a API, --api=API     APIs are ['all', 'google', 'microsoft', 'yahoo'],
                            cannot use with '-p po_file'option
      -d, --detect          detect language for target sentence
      -f LANG, --from=LANG  original language
      -t LANG, --to=LANG    target language to translate
      -p POFILE, --pofile=POFILE
                            target po file
      -s SENTENCE, --sentence=SENTENCE
                            target sentence
      -e ENCODING, --encoding=ENCODING
                            input/output encoding
      -q, --quiet           not to show original sentence to stdout
      -v, --verbose         show debug messages to stdout


Requirements
============

* Python 2.6 or later
* polib 0.5.5 or later
* setuptools or distriubte.


License
=======
Python Software Foundation License.


History
=======

0.3.0 (2011-02-17)
------------------
* add -d(detect) option
* add more api for Microsoft Translator
* refactor translator architecture

0.2.0 (2011-02-07)
------------------
* add -q(quiet) and -e(encoding) option

0.1.0 (2011-01-22)
------------------
* first release

