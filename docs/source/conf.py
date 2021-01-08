# Configuration file for the Sphinx documentation builder.

# -- Path setup --------------------------------------------------------------

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))


# -- Project information -----------------------------------------------------

project = "EasyLAMMPS"
copyright = "2020, Kévin Kempfer"
author = "Kévin Kempfer"
release = "0.1"


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "undoc-members": None,
    "exclude-members": "__weakref__",
}

templates_path = ["_templates"]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"

# html_logo = "_static/logo.png"

html_theme_options = {
    "canonical_url": "https://github.com/kkempfer/easylammps/docs",
    "logo_only": True,
    "display_version": True,
    "prev_next_buttons_location": "both",
    "style_external_links": False,
    "style_nav_header_background": None,
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

html_static_path = ["_static"]
