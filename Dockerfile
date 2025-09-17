FROM python:3.12

# Set workdir
WORKDIR /app

# System deps (safer for mysqlclient)
RUN apt-get update && apt-get install -y --no-install-recommends \        default-libmysqlclient-dev build-essential pkg-config \        && rm -rf /var/lib/apt/lists/*

# Copy project metadata first for better caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy rest of the project
COPY . /app

# Django collects static files (optional; won't fail if static not configured)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Entrypoint applies migrations then starts server
RUN chmod +x /app/entrypoint.sh
EXPOSE 8000
CMD ["/bin/sh", "/app/entrypoint.sh"]
