# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from os.path import join as pathjoin
import sys

VERSION = '0.1'
LONG_DESCRIPTION = "".join([
    open(pathjoin("src","README.txt")).read(),
    open(pathjoin("src","TODO.txt")).read()])

CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Environment :: Web Environment",
    "Intended Audience :: End User/Desktop",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Python Software Foundation License",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Programming Language :: Python",
    "Topic :: Software Development",
    "Topic :: Software Development :: Internationalization",
]

setup(
     name="ikazuchi",
     version=VERSION,
     description="ikazuchi helps to translate po file efficiently",
     long_description=LONG_DESCRIPTION,
     classifiers=CLASSIFIERS,
     keywords=["po-file", "translate", "i18n", "internationalization"],
     author="Tetsuya Morimoto",
     author_email="tetsuya dot morimoto at gmail dot com",
     url="http://t2y.bitbucket.org/ikazuchi/build/html/index.html",
     license="PSL",
     #py_modules=["ikazuchi_thinking_of_later"],
     packages=find_packages("src"),
     package_dir={"": "src"},
     package_data = {"": ["buildout.cfg"]},
     include_package_data=True,
     install_requires=[
        "setuptools",
        "polib",
         # -*- Extra requirements: -*-
     ],
     extras_require=dict(
         test=[
             "pikzie",
             "minimock",
             "pep8",
         ],
     ),
     #test_suite="nose.collector",
     tests_require=["pikzie","minimock","pep8"],
     entry_points="""
        [console_scripts]
        ikazuchi = ikazuchi:main
     """,
)
