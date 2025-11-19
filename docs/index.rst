News Portal — Project Documentation
===================================

Overview
--------

This project is a simple news portal built with Django and Django REST Framework.

It supports:

- Readers who can view articles and subscribe to publishers / journalists.
- Editors who can review and approve articles.
- Journalists who can create and manage their own articles.
- Optional posting to X (Twitter) when an article is approved (if credentials are configured).

Quick start (local)
-------------------

1. Create and activate a virtual environment::

      python -m venv .venv
      source .venv/bin/activate   # On Windows: .venv\Scripts\activate

2. Install dependencies::

      pip install --upgrade pip
      pip install -r requirements.txt

3. Configure environment (SQLite default)::

      # For quick testing, ensure USE_SQLITE=1 is set in your environment
      # e.g. on Linux/macOS:
      export USE_SQLITE=1

4. Apply migrations and create a superuser::

      python manage.py migrate
      python manage.py createsuperuser

5. Run the development server::

      python manage.py runserver

Docker usage
------------

To build and run the Docker container::

      docker build -t news-portal .
      docker run --rm -p 8000:8000 news-portal

The container:

- Installs project dependencies.
- Applies migrations on startup.
- Starts the development server on port 8000.

Permissions & roles
-------------------

On ``migrate`` the project automatically creates three groups:

- **Reader** – can view articles and newsletters.
- **Editor** – can view, change, and delete articles and newsletters.
- **Journalist** – can add, view, change, and delete articles and newsletters.

These groups are intended to be assigned to users via the Django admin interface.

API
---

The REST API is implemented using Django REST Framework.

Key endpoints (relative to ``/``) include:

- ``/api/articles/`` – list and manage articles.
- ``/api/newsletters/`` – list and manage newsletters.
- ``/api/publishers/`` – manage publishers.

For full details, use the DRF browsable API or see the code in ``news/views.py``.

.. toctree::
   :maxdepth: 2
   :caption: Code Reference

   modules
