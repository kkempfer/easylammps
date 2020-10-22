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
    "member": True,
    "member-order": "bysource",
    "special-members": None,
    "undoc-members": None,
    "exclude-members": "__weakref__",
}

templates_path = ["_templates"]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"

# html_logo = "_static/logo.png"

#html_theme_options = {
#    "canonical_url": "https://github.com/kkempfer/easylammps/docs",
#    "logo_only": False,
#    "display_version": True,
#    "prev_next_buttons_location": "bottom",
#    "style_external_links": True,
#    #"style_nav_header_background": "white",
#    # Toc options
#    "collapse_navigation": True,
#    "sticky_navigation": True,
#    "navigation_depth": 4,
#    "includehidden": True,
#    "titles_only": False
#}

#html_context = {
#    source_url_prefix:"https://github.com/kkempfer/easylammps/docs",
#}

#html_theme = "pydata_sphinx_theme"
#html_theme_options = {
#    "github_url": "https://github.com/kkempfer/easylammps",
#    "external_links": [{"url": "https://lammps.sandia.gov", "name": "LAMMPS"}],
#    "use_edit_page_button": True,
#    "search_bar_position": "sidebar",  # navbar
#    "navigation_with_keys": True,
#    "show_toc_level": 2,
#}
#html_context = {
#    "github_url": "https://github.com",
#    "github_user": "kkempfer",
#    "github_repo": "easylammps",
#    "github_version": "main",
#    "doc_path": "docs/source",
#}

html_static_path = ["_static"]
