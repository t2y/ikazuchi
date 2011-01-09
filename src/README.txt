`ikazuchi` helps to translate po file efficiently.

Features
========

* Translate GNU gettext catalog called PO file with good reference from Web API


Setup
=====

by easy_install
----------------
Make environment::

   $ easy_install ikazuchi

by buildout
------------
Make environment::

   $ hg clone https://t2y@bitbucket.org/t2y/ikazuchi
   $ cd ikazuchi
   $ python bootstrap.py
   $ bin/buildout


Usage
=====

Execute ikazuchi command::

   $ ikazuchi -t ja -p examples/short_test.po 
   msgid:           forest book
   for reference:   森林の本
   Input: もりのほん

   msgid:       Python Module Of The Week
   for reference:   今週のPythonモジュール
   Input:  
   updated msgstr:  

   msgid:       ikazuchi translation
   for reference:   雷の翻訳
   Input: y
   updated msgstr:  雷の翻訳

You can entered translation string for msgid after "Input: ".
Or just type "y" if you want to select reffrence string.

All command option are::

    $ python src/ikazuchi/ikazuchi.py -h
    Usage: ikazuchi.py [options]

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -a API, --api=API     translation api are ['google', 'yahoo']
      -f LANG, --from=LANG  original language(msgid)
      -t LANG, --to=LANG    target language(msgstr)
      -p POFILE, --pofile=POFILE
                            target po file
      -s SENTENCE, --sentence=SENTENCE
                            target sentence
      -v, --verbose         print debug messages to stdout


Requirements
============

* Python 2.6 or later (not tested 3.x)
* polib 0.5.5 or later
* setuptools or distriubte.


License
=======
Python Software Foundation License.


History
=======

0.1 (2011-01-10)
-----------------
* first version
* use Google Translate API as reference
