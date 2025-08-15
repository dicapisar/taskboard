# TaskBoard

TaskBoard is a web application built with **FastAPI**, **PostgreSQL**, and **Redis**. It provides a REST API and simple web UI for task management with user authentication and role support.

---

## Features

- User authentication (login/logout) with **bcrypt** password hashing.
- Task CRUD using async **SQLAlchemy 2.x** and **asyncpg**.
- Roles: **admin** and **student**.
- Profile image upload via multipart/form-data.
- Jinja2 templates + static assets.
- Redis-backed session cache.
- One-time DB seeding on first start.

---

## Requirements

- Docker
- Docker Compose

> This project uses **Poetry** for dependency management only (no package build).

---

## Quick Start (Docker)

1) Create a `.env` file (example below).  
2) Build and run:

```bash
docker-compose up --build
```

App will be available at: http://localhost:8000

### .env example

```env
# Database
POSTGRES_DB=taskboard
POSTGRES_USER=taskboard
POSTGRES_PASSWORD=secret
DATABASE_URL=postgresql+asyncpg://taskboard:secret@db:5432/taskboard

# Redis
REDIS_URL=redis://redis:6379

# App
ENVIRONMENT=dev
PROJECT_NAME=TaskBoard

# Default admin (seeded only when there are no roles)
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
```

---

## Database Seeding

On container start, `init_db.py` runs and:
- Creates tables via `Base.metadata.create_all` (all models are imported first).
- Seeds roles: `admin` (id=1) and `student` (id=2) **only if no roles exist**.
- Creates the default admin user (credentials from `.env`).

### Run the seeder manually

**Inside Docker:**

```bash
docker-compose exec web python init_db.py
```

**Locally (outside Docker):** update `DATABASE_URL` to use `localhost` as host, for example:
```
postgresql+asyncpg://taskboard:secret@localhost:5432/taskboard
```
then run:
```bash
python init_db.py
```

---

## Project Structure

```
src/
├─ app/
│  ├─ api/v1/         # REST endpoints
│  ├─ web/            # Jinja2 routes
│  ├─ core/           # settings, DB, cache
│  ├─ services/       # business logic
│  ├─ repositories/   # DB adapters
│  ├─ models/         # SQLAlchemy models
│  ├─ schemas/        # Pydantic models
│  ├─ templates/      # HTML templates
│  └─ static/         # CSS / JS / images
├─ init_db.py         # one-time DB seeder
```

---

## Development Notes

- Install dependencies locally (without packaging the project):
  ```bash
  poetry install --no-root
  ```

- Run tests:
  ```bash
  poetry run pytest
  ```

---

## Troubleshooting

- **Form data requires python-multipart**  
  If you see: `RuntimeError: Form data requires "python-multipart" to be installed.`  
  Install it locally:
  ```bash
  poetry add python-multipart
  ```
  (The Docker image already includes this dependency.)

- **SQLAlchemy relationship resolution (Task not found)**  
  Ensure `init_db.py` imports all models *before* creating tables or querying:
  ```python
  import src.app.models.role
  import src.app.models.user
  import src.app.models.task
  from src.app.core.database import Base
  # Base.metadata.create_all(...)
  ```

- **Template path case-sensitivity**  
  Linux/Docker filesystems are case-sensitive. Make sure the template path in `TemplateResponse(...)` matches directory/file casing exactly (e.g., `mainBoard/mainBoard.html`).

- **DATABASE_URL host**  
  Inside Docker use `db` as host; outside Docker use `localhost` (or your host IP).

- **Poetry tries to install the project**  
  This repo uses Poetry for deps only. The Docker build uses:
  ```
  poetry install --no-interaction --only main --no-root
  ```

---

## Security

- Passwords are hashed using **bcrypt** on seeding.
- Login validates with `bcrypt.checkpw(...)`. Example in the `LoginService`:
  ```python
  import bcrypt

  if user and isinstance(user.password, str) and bcrypt.checkpw(
      password.encode(),
      user.password.encode()
  ):
      return user
  ```

---

## License

MIT © 2025 — dicapisar
