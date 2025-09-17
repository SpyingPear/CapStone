import os, sys
sys.path.insert(0, os.path.abspath(".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "news_portal.settings")

# Mock heavy deps during doc builds (so Sphinx can run even without Django/DRF installed)
autodoc_mock_imports = ["django", "rest_framework"]

try:
    import django  # type: ignore
    django.setup()
except Exception:
    # Build docs without initializing Django if it's unavailable in the environment
    pass

project = "News Portal – Developer Docs"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]
html_theme = "alabaster"
