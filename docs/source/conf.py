# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "/")

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'andi-py'
copyright = '2026, F. Kolbl - Y. Bornat - L. Regnacq - T. Couppey'
author = 'F. Kolbl - Y. Bornat - L. Regnacq - T. Couppey'
release = '1.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


templates_path = ['_templates']
exclude_patterns = []
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

html_theme = "furo"
html_title = "ANDI"
html_static_path = ['_static']
html_logo = "logo/andi_logo.svg"
add_module_names = False  # shorten fully-qualified names in headings

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True

autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_mock_imports = [
    "numpy",
    "scipy",
    "matplotlib",
    # add whatever the error mentions
]



