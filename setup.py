#!/usr/bin/env python3
import os

from setuptools import find_packages, setup


def read(rel_path: str) -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with open(os.path.join(here, rel_path)) as fp:
        return fp.read()


def get_version(rel_path: str) -> str:
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setup(
    name="statements-manager",
    version=get_version("statements_manager/__init__.py"),
    author="Yuya Sugie",
    author_email="y.sugie.15739d@gmail.com",
    url="https://github.com/tsutaj/statements-manager",
    license="Apache-2.0",
    description="",
    python_requires=">=3.9.12",
    install_requires=[
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "markdown>=3.3.1",
        "jinja2",
        "toml",
        "colorlog",
        "pdfkit>=1.0.0",
        "pymdown-extensions",
        "pyquery>=1.2.4",
        "rich",
    ],
    packages=find_packages(exclude=("sample", "config")),
    entry_points={
        "console_scripts": [
            "ss-manager = statements_manager.main:main",
        ],
    },
)
