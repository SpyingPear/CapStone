import os, sys
sys.path.insert(0, os.path.abspath('..'))

project = 'News Portal'
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon', 'sphinx.ext.viewcode']
templates_path = ['_templates']
exclude_patterns = ['_build']
html_theme = 'alabaster'
html_static_path = ['_static']
