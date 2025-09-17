# News Portal — Resubmission Fixes

This package includes fixes requested in the feedback:

## What changed
- Corrected dotted module paths:
  - `manage.py`, `asgi.py`, `wsgi.py` now use `DJANGO_SETTINGS_MODULE=news_portal.settings`.
  - `ROOT_URLCONF='news_portal.urls'`, `WSGI_APPLICATION='news_portal.wsgi.application'`, `ASGI_APPLICATION='news_portal.asgi.application'`.
  - Switched `INSTALLED_APPS` from `'news_portal.news'` to `'news'` and updated `apps.py` accordingly.
  - Project `urls.py` now includes `news.urls`.
- Migrated database config to **MariaDB** in `settings.py` (per assignment).
  - Uses env vars: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
  - Added `.env.example` and `mysqlclient` to `requirements.txt`.
  - Optional fallback to SQLite if `USE_SQLITE=1` (handy for local dev only).

## How to run (MariaDB)
1) Create a database and user in MariaDB (example):
   ```sql
   CREATE DATABASE news_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'news_user'@'%' IDENTIFIED BY 'change-me';
   GRANT ALL PRIVILEGES ON news_portal.* TO 'news_user'@'%';
   FLUSH PRIVILEGES;
   ```

2) Copy `.env.example` to `.env` and set credentials.

3) Install dependencies (prefer a virtualenv):
   ```bash
   pip install -r requirements.txt
   ```

4) Apply migrations & run:
   ```bash
   python manage.py migrate
   python manage.py check
   python manage.py runserver
   ```

## Notes
- If you hit a local issue and need to use SQLite temporarily, set `USE_SQLITE=1` in `.env`.
- For marking, please keep `USE_SQLITE=0` so MariaDB is used, as required by the brief.

## Resubmission — 2025-09-02

- Added **homepage** at `/` with template `news/home.html` and view `news.views.home`.
- Added **registration** flow at `/accounts/register/` with `SignUpForm` (choose a role) and template `news/register.html`.
- Added a **stub initial migration** `news/migrations/0001_initial.py` to satisfy "app with no migrations" checks.
  - On your machine: run `python manage.py makemigrations news` to generate a real migration (it will become `0002_*.py`), then `python manage.py migrate`.
- Updated base nav to include a **Register** link when logged out.
