#!/usr/bin/env python3
from setuptools import find_packages, setup

setup(
    name="statements-manager",
    version="1.4.4",
    author="Yuya Sugie",
    author_email="y.sugie.15739d@gmail.com",
    url="https://github.com/tsutaj/statements-manager",
    license="Apache License 2.0",
    description="",
    python_requires=">=3.7",
    install_requires=[
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "markdown>=3.3.1",
        "jinja2",
        "toml",
        "colorlog",
        "pdfkit",
        "pymdown-extensions",
    ],
    packages=find_packages(exclude=("sample", "config")),
    entry_points={
        "console_scripts": [
            "ss-manager = statements_manager.main:main",
        ],
    },
)
