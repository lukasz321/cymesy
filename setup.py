#!/usr/bin/env python
import os
from setuptools import setup, find_packages

NAME = "compute"

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, NAME, "__version__.py")) as f:
    exec(f.read(), about)

setup(
    name=NAME,
    version=about["__version__"],
    author="Density Factory",
    author_email="factory@density.io",
    install_requires=[],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'mfg-compute=compute.__main__:main',
            'mfg-go=compute.__main__:main',
            ],
    },
    packages=find_packages(
        exclude=(
            "tests",
            "docs",
            "vendor",
        )
    ),
)
