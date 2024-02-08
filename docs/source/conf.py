# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

# Project information
project = "PSyACC"
copyright = "Crown Copyright, Met Office"
author = "Joseph Wallwork"

# General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
]
templates_path = ["_templates"]
exclude_patterns = []

# Options for HTML output
html_theme = "alabaster"
html_static_path = ["_static"]

# Configure Intersphinx
intersphinx_mapping = {
    "psyclone": ("https://psyclone.readthedocs.io/en/stable", None),
    "python": ("https://docs.python.org/3", None),
}
