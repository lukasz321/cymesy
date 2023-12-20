#!/usr/bin/env python

import os
from setuptools import setup, find_packages

NAME = "cymesy"

about = {}
with open(os.path.join(here, os.path.abspath(os.path.dirname(__file__)), "__version__.py")) as f:
    exec(f.read(), about)

setup(
    name=NAME,
    version=about["__version__"],
    author=""
    author_email=""
    url="",
    license="",
    include_package_data=True,
    install_requires=[
        ],
    entry_points={
        "console_scripts": [
            "mfg-records=mfg.print_records:main",
        ],
    },
    packages=find_packages(),
)
