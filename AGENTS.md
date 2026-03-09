# AGENTS.md

## Cursor Cloud specific instructions

### Overview
This is an Odoo 19 development environment. The Odoo source is cloned to `/workspace/odoo` (branch `19.0`). The repository root (`/workspace`) contains `main.py` (user code), `odoo.conf` (config), and this file.

### Services

| Service | How to start | Notes |
|---|---|---|
| **PostgreSQL 16** | `sudo pg_ctlcluster 16 main start` | Must start before Odoo. DB user `ubuntu` with superuser/createdb. |
| **Odoo 19** | `python3 /workspace/odoo/odoo-bin -c /workspace/odoo.conf -d odoo19_dev --dev=all` | Runs on port 8069. Admin login: `admin`/`admin`. |

### Key commands

- **Run Odoo (dev mode):** `python3 /workspace/odoo/odoo-bin -c /workspace/odoo.conf -d odoo19_dev --dev=all`
- **Run tests:** `python3 /workspace/odoo/odoo-bin -d odoo19_test --test-enable -i <module> --test-tags <tag> --stop-after-init --http-port=8070`
  - Use a different port (e.g. 8070) if main Odoo is running on 8069.
- **Lint (flake8):** `cd /workspace/odoo && flake8 --max-line-length=120 <file_or_dir>`
- **Config file:** `/workspace/odoo.conf`
- **Addons path:** `/workspace/odoo/addons`

### Gotchas
- PostgreSQL must be started manually after VM boot (`sudo pg_ctlcluster 16 main start`). It does not auto-start.
- Odoo's `--dev=all` flag enables auto-reload on Python file changes, but changes to XML views require a module upgrade (`-u <module>`).
- When running tests, use `--stop-after-init` and a separate `--http-port` to avoid conflicts with a running dev server.
- The `odoo.conf` `db_host`/`db_port`/`db_password` fields should be omitted (not set to `False`) for local socket connections in Odoo 19.
- System Python packages are installed with `--break-system-packages` since no venv is used.
- `~/.local/bin` must be on `PATH` for pip-installed CLI tools (already configured in `~/.bashrc`).
