# News Portal — Setup & Run

This project can be run **either** in a Python virtual environment or via **Docker**.

## Option A — Virtual Environment

1. Create & activate a venv
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. Install dependencies
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Apply migrations & run
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
   Visit http://127.0.0.1:8000

## Option B — Docker

1. Build the image
   ```bash
   docker build -t news-portal .
   ```

2. Run the container
   ```bash
   docker run --env DJANGO_SETTINGS_MODULE=config.settings -p 8000:8000 news-portal
   ```

## Documentation (Sphinx)

Auto-generated API docs live under `docs/`. To (re)generate:

```bash
# from project root
sphinx-apidoc -o docs/ .
make -C docs html
```

Ensure `docs/_build/` **is NOT** in `.gitignore` so reviewers can see the generated HTML.

## Notes

- If you use MySQL, set env vars in Docker run (or `.env`) accordingly:
  ```bash
  -e DB_NAME=... -e DB_USER=... -e DB_PASSWORD=... -e DB_HOST=... -e DB_PORT=3306
  ```
- The container entrypoint runs `migrate` and `collectstatic` automatically before starting the server.
