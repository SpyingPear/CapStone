# News Portal — Setup

## 1. Requirements
- Python 3.10–3.12
- MariaDB/MySQL (or use SQLite for quick local runs)
- `pip install -r requirements.txt`

## 2. Environment
Create a `.env` next to `manage.py`:

**MariaDB (default):**
```env
DEBUG=1
SECRET_KEY=change-me
USE_SQLITE=0

DB_NAME=news_portal
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
```

**SQLite (quick local):**
```env
DEBUG=1
SECRET_KEY=dev-only
USE_SQLITE=1
```

## 3. First run
```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Visit http://127.0.0.1:8000/

## 4. Tips
- After each major edit, do a quick `python manage.py check` or `runserver` to catch syntax early.
- If you add/modify models, re-run `makemigrations` and `migrate`.
