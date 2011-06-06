`ikazuchi <https://bitbucket.org/t2y/ikazuchi>`_
helps to translate document using web translate APIs efficiently.
`ikazuchi` is intended to work with other tools since it's a CUI tool.

See the project `documentation <http://t2y.bitbucket.org/ikazuchi/build/html/index.html>`_ for more detail.


Features
========

* Translate reST document file keeping with the format
* Translate any string passed from command line argument
* Translate any string in Vim using ":pyfile" command
* Detect language of any string passed from command line argument
* Extend ``Handler`` with plug-in to your needs


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
   $ python bootstrap.py -d
   $ bin/buildout


Usage
=====

Execute ikazuchi command::

    $ ikazuchi -s "i can translate"
    sentence:                i can translate
    translated(Google):      [Actually, translated sentence]

    $ ikazuchi -d -s "hello"
    sentence:                hello
    detect(Google):          [{u'isReliable': False, u'confidence': 0.01737435, u'language': u'en'}]

Show which plugins are available::

    $ ikazuchi -h
    usage: ikazuchi [-h] {rstfile,normal} ...

    positional arguments:
      {rstfile,normal}  available plugins. 'normal' means ikazuchi's standard
                        feature so it can be abbreviated

    optional arguments:
      -h, --help        show this help message and exit

Show normal feature help::

    $ ikazuchi normal -h
    usage: ikazuchi normal [-h] [-a API] [-e ENCODING] [-f LANG] [-q] [-t LANG]
                           [-d] [-l] [-s SENTENCE [SENTENCE ...]] [--version]

    optional arguments:
      -h, --help            show this help message and exit
      -a API, --api API     APIs are ['google', 'microsoft']
      -e ENCODING, --encoding ENCODING
                            input/output encoding
      -f LANG, --from LANG  original language
      -q, --quiet           not to show original sentence to stdout
      -t LANG, --to LANG    target language to translate
      -d, --detect          detect language for target sentence
      -l, --languages       show supported languages
      -s SENTENCE [SENTENCE ...], --sentences SENTENCE [SENTENCE ...]
                            target sentences
      --version             show program's version number and exit

Show rstfile plugin help::

    $ ikazuchi rstfile -h
    usage: ikazuchi rstfile [-h] [-a API] [-e ENCODING] [-f LANG] [-q] [-t LANG]
                            [-o OUTPUT]
                            rst_file

    positional arguments:
      rst_file              target rst file

    optional arguments:
      -h, --help            show this help message and exit
      -a API, --api API     APIs are ['google', 'microsoft']
      -e ENCODING, --encoding ENCODING
                            input/output encoding
      -f LANG, --from LANG  original language
      -q, --quiet           not to show original sentence to stdout
      -t LANG, --to LANG    target language to translate
      -o OUTPUT, --output OUTPUT
                            translated output file name, default is 'output.rst'

.. note::

    Notice the difference of command line option between
    normal(standard feature) and rstfile.


Requirements
============

* Python 2.6 or later
* setuptools or distriubte


License
=======

Apache License 2.0


History
=======

0.5.1 (2011-06-06)
------------------
* add subparser for plug-in
* remove -p(plug-in) option
  (plug-in feature is provided with subparsers)

0.5.0 (2011-06-03)
------------------
* add plug-in feature
* add -p(plug-in) option
* remove -p(po file) and -r(rst file) option
  (po/rst file is handled with plug-in option)

0.4.2 (2011-06-01)
------------------
* change to call enrai/raimei scripts with portability
* fix some minor bugs for enrai/raimei

0.4.1 (2011-05-31)
------------------
* upgrade enrai/raimei scripts with updated Translate API
* add setting apikey feature for Translator with configuration file
* add LICENSE file for distribution
* fix some minor bugs

0.4.0 (2011-05-23)
------------------
* add -l(languages) option
* add -r(rst file) option
* upgrade v1 to v2 for Google Translator
* Change license to Apache License 2.0

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

