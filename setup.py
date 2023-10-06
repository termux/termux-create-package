#!/usr/bin/env python
"""
termux-create-package setup script
https://packaging.python.org/en/latest/tutorials/packaging-projects
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as file:
    LONG_DESCRIPTION = file.read()


setuptools.setup(
    name="termux-create-package",
    version="0.12.0",
    author="Agnostic Apollo, Fredrik Fornwall",
    author_email="agnosticapollo@gmail.com, fredrik@fornwall.net",
    description="Utility to create binary deb packages",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    url="https://github.com/termux/termux-create-package",
    project_urls={
        "Bug Tracker": "https://github.com/termux/termux-create-package/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools"
    ],
    scripts=["src/termux-create-package"],
)
