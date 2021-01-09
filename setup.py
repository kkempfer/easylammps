#!/usr/bin/env python
"""EasyLAMMPS Package configuration."""

from setuptools import setup, find_packages

AUTHOR = "Kevin Kempfer"
EMAIL = "kevin.kempfer@hotmail.fr"
DESCRIPTION = "Python tools for LAMMPS"
LONG_DESCRIPTION = """
A user-friendly Python package to manipulate input and output files of LAMMPS
molecular dynamics code. One Python class per LAMMPS file type. Include
conversion into pandas DataFrame for quick and easy access to LAMMPS
information within Python.
"""
URL = "https://github.com/kkempfer/easylammps"
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GNU Affero General Public License v3",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Chemistry",
]

setup(
    name="easylammps",
    version="0.1",
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url=URL,
    classifiers=CLASSIFIERS,
    packages=find_packages(include=["easylammps", "easylammps.*"]),
    install_requires=["networkx", "numpy", "pandas"],
    extras_require={"test": ["pytest"]},
)
