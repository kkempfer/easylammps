#!/usr/bin/env python

import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

with open("LICENSE", "r") as f:
    license = f.read()

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f]

setuptools.setup(
    name="easylammps",
    version="0.1",
    author="Kevin Kempfer",
    author_email="kevin.kempfer@hotmail.fr",
    description="A user-friendly Python package to manipulate input and output files of LAMMPS molecular dynamics code. One Python class per LAMMPS file type. Includes conversion into pandas DataFrame.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=license,
    url="https://github.com/kkempfer/easylammps",
    packages=setuptools.find_packages(),
    package_dir={"": "easylammps"},
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: AGPL-3.0",
        "Operating System :: OS Independent",
    ],
)
