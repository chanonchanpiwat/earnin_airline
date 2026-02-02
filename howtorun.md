# 🚀 Project Run Guide

This project uses **Makefile commands** to standardize environment setup, container startup, database migration, development server run, and testing.

Follow the steps below in order for a clean setup.

---

# ✅ Prerequisites

Make sure the following tools are installed:

- Python
- uv package manager — https://github.com/astral-sh/uv
- Docker
- Docker Compose
- Make

Verify installation:

```bash
python --version
uv --version
docker --version
docker compose version
make --version
```

---

# 🧱 Step 1 — Install Dependencies

Run this first:

```bash
make init
```

---

# 🐳 Step 2 — Start Containers

Start required services (PostgreSQL, etc.) [is required for both testing and running service locally]:

```bash
make docker-up
```

---

# 🗄️ Step 3 — Run Database Migration

Apply the database schema after containers are running [not required for testing but require for running service locally]:

```bash
make migrate
```

Runs:

```bash
docker compose exec -it postgres bash -c "/home/scripts/exec_sql.sh schema.sql"
```

---

# 🧪 Step 4 — Run Tests

tests file is located under tests
Run the full test suite:

```bash
make test
```


Test report output:

```
report.html
```

Open this file in your browser to view results.

for github action we will find report once pr have failed on test

---

# 💻 Run Application Locally (Dev Mode)

To start the FastAPI app locally:

```bash
make dev
```

---

