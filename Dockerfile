FROM python:3.13-rc-slim

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install Poetry
RUN pip install --upgrade pip && pip install poetry bcrypt python-multipart

# Copy pyproject.toml early to cache dependencies
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry
ENV POETRY_VIRTUALENVS_CREATE=false
RUN poetry install --no-interaction --only main --no-root

# Copy source code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run init_db before starting the app
CMD ["sh", "-c", "python init_db.py && uvicorn src.app.main:app --host 0.0.0.0 --port 8000"]