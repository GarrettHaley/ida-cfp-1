"""
Defines `distuitls` installation.

Provides a simplistic way for a new user to install all six of the
main IDA-CFP modules. Largely adapted from Pyglet's setup.py
"""

from setuptools import setup

VERSION = '1.0.0'

LONG_DESCRIPTION = """IDA-CFP is a two part project designed to process
C99-standard files and partially automate aspects of reverse engineering.
Several similar projects have been created in years past for the IDA Pro
platform utilizing IDAPython's available API. This project serves both
as an exercise in learning what Python 3.7 has to offer as well as
exploring the available interface of IDA Free. It is by no means a final
work and will continue to be improved upon as time allows."""


SETUP_INFO = dict(
    name="IDA-CFP",
    version=VERSION,
    author="rttmd",
    url="https://github.com/rttmd/ida_lib_parser",
    download_url="https://github.com/rttmd/ida_lib_parser/releases",
    description="Cross-platform C file parser for IDA Free",
    long_description=LONG_DESCRIPTION,
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    packages=["astparser",
              "core",
              "exception",
              "interface",
              "record",
              "verifier"],

    zip_safe=True
)

setup(**SETUP_INFO)
