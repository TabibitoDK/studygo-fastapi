# StudyGo API (FastAPI + SQLModel + Postgres)

No Node/npm required. Pure Python backend with JWT auth, file uploads, and the same resources:
**users, posts, progress**.

## Features
- FastAPI + SQLModel (SQLAlchemy) + Postgres
- JWT auth (python-jose), bcrypt hashing (passlib)
- Users: register/login/me/update
- Posts: list/create/delete (owner only)
- Progress: per-module upsert
- File uploads served from `/files/*`
- Docker Compose for Postgres
- `.env` config

## Quick start (Ubuntu)

### 0) Install Python and tools
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip docker.io docker-compose-plugin
python3 --version && pip3 --version
```

### 1) Start Postgres
```bash
docker compose up -d
```

### 2) Create venv & install deps
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
- `DATABASE_URL=postgresql+psycopg2://studygo:supersecret@localhost:5432/studygo`
- `JWT_SECRET=` set a long random string
- `CORS_ORIGIN=` your webapp URL (e.g., `http://localhost:5173` or your domain)
- `BASE_URL=` public base URL for this API (e.g., `http://localhost:8000`)

### 3) Create tables & run server
Tables auto-create on first run:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open:
- API root: `http://<server-ip>:8000/`
- Docs: `http://<server-ip>:8000/docs`

### 4) Seed (optional)
Use the `/register`, `/login`, and POST endpoints from docs UI.

## Production notes
- Use a reverse proxy (Nginx/Caddy) with HTTPS
- Create a systemd service for uvicorn/gunicorn
- Schedule `pg_dump` backups
- Consider Alembic if you later need DB migrations
