import datetime
import os

import pkg_resources

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

__version__ = pkg_resources.get_distribution('statements-manager').version
__year__ = datetime.date.today().year

project = "statements-manager"
copyright = f"{__year__}, tsutaj"
author = "tsutaj"
license = "Apache-2.0"
release = f"v{__version__}"

rtd_version = os.environ.get('READTHEDOCS_VERSION')
if rtd_version == 'latest':
    tag = 'master'
else:
    tag = 'v{}'.format(__version__)

extlinks = {
    'github': ('https://github.com/%s', '%s'),
    'blob': (f'https://github.com/tsutaj/statements-manager/blob/{tag}/%s', '%s'),
    'tree': (f'https://github.com/tsutaj/statements-manager/tree/{tag}/%s', '%s'),
}

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.extlinks",
    "sphinx_rtd_theme",
    "sphinx_copybutton",
    "sphinxcontrib.images"
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "ja"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]


def setup(app):
    app.add_object_type(
        'problemtoml', 'problemtoml',
        objname='problem config key',
        indextemplate='pair: %s; problem config key'
    )
    app.add_object_type(
        'problemsettoml', 'problemsettoml',
        objname='problemset config key',
        indextemplate='pair: %s; problemset config key'
    )
    app.add_object_type(
        'statementvar', 'statementvar',
        objname='variable in statement',
        indextemplate='pair: %s; variable in statement'
    )
