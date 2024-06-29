import tomllib
import datetime

with open("../pyproject.toml", "rb") as f:
    toml = tomllib.load(f)

_pyproject = toml["project"]

project = _pyproject["name"].capitalize()
version = _pyproject["version"]
release = _pyproject["version"]

author = "Alex Lambson"
project_copyright = f"{datetime.date.today().year}, Alex Lambson"
extensions = [
    "myst_parser",
    "autoapi.extension",
    "sphinx.ext.autodoc",
    "sphinx_rtd_theme",
]

autoapi_dirs = ["../src"]
autoapi_python_class_content = "both"
autoapi_options = [
    "members",
    "undoc-members",
    "private-members",
    "show-inheritance",
    "special-members",
    "imported-members",
]
autodoc_typehints = "description"
autodoc_typehints_format = "short"

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    # 'analytics_id': 'G-XXXXXXXXXX',  #  Provided by Google in your dashboard
    # 'analytics_anonymize_ip': False,
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": True,
    "vcs_pageview_mode": "",
    "style_nav_header_background": "#2980B9",
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 2,
    "includehidden": True,
    "titles_only": True,
}
