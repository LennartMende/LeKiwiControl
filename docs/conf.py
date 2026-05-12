# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'robot_control'
copyright = '2026, HTWK Leipzig'
author = 'HTWK Leipzig'
release = '26/05'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']


# docs/conf.py
import os
import sys

# 1. Root-Package von robot_control hinzufügen
sys.path.insert(0, os.path.abspath("../src"))

# 2. Optional: Pfad zu lerobot hinzufügen, wenn noch nicht installiert
# sys.path.insert(0, "/home/student/lerlekiwi/src/lerobot")

autodoc_member_order = "bysource"

# 3. Extensions
extensions = [
    'sphinx.ext.autodoc',   # Docstrings automatisch einbinden
    'sphinx.ext.napoleon',  # Google/NumPy Docstrings
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode'
]

autosummary_generate = True

# 4. Mock für Hardware/lerobot-Pakete (falls sie nicht importierbar sind)
autodoc_mock_imports = [
    "lerobot.robots.lekiwi",
    "lerobot.teleoperators.keyboard.teleop_keyboard",
    "lerobot.teleoperators.so100_leader",
    "lerobot.utils.robot_utils",
]
