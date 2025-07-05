import os
import sys

sys.path.insert(0, os.path.abspath("../.."))  # Adjust path as needed
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "PythonProjectGrader"
copyright = "2025, Lyuboslav Karev"
author = "Lyuboslav Karev"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # Automatically document from docstrings
    "sphinx.ext.napoleon",  # Support for Google-style or NumPy-style docstrings
    "sphinx.ext.viewcode",  # Add links to source code in documentation]
    "sphinx_rtd_theme_ext_color_contrast",
]
templates_path = ["_templates"]
exclude_patterns = []  # type: ignore


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
