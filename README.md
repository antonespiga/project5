Project5 — Route/Activity Mapper

Overview

Project5 is a small Django web application for importing, parsing and visualizing GPS route/activity files (TCX). It provides model-backed storage of activities, simple map visualizations, per-activity images, and helper utilities to parse TCX files and compute metrics (distance, heart rate, pace, elevation). The app is implemented under the `mapas` Django app and a lightweight project configuration in `project5`.

Distinctiveness and Complexity

This project meets distinctiveness and complexity requirements because:
- It implements a full-stack web application (Django backend + HTML/JS front-end) rather than a trivial script or single-file exercise.
- It includes non-trivial data parsing and processing: custom TCX parsing logic, smoothing utilities, and metric computations (distance, pace, elevation gain, heart-rate summaries) which required careful handling of timestamps, missing data and coordinate interpolation.
- The UI integrates map rendering and activity plotting in the `static/mapas` assets, and the project contains reusable data-processing utilities (e.g., `tcx_parser.py`, `tcx_parse_calc.py`, `tcx_parser_split.py`).
- There is data modeling (Django models, migrations) and file handling for imported activity media (images and thumbnails), which adds complexity beyond simple CRUD apps.

What I created (file list and contents)

- README.md: This file — project overview, distinctiveness statement, file list, run instructions, and notes for reviewers.
- requirements.txt: Pinning the Python packages needed to run the site locally.

Key repository files (high level)

- [manage.py](manage.py): Django CLI entrypoint to runserver, migrate, etc.
- [project5/settings.py](project5/settings.py): Django settings for the project.
- [project5/urls.py](project5/urls.py): URL router.
- [mapas/models.py](mapas/models.py): Django models describing activities, routes, and related items.
- [mapas/views.py](mapas/views.py): Request handlers and page views.
- [mapas/tcx_parser.py, mapas/tcx_parse_calc.py, mapas/tcx_parser_split.py]: TCX parsing and calculation utilities used to import and process route files.
- [mapas/static/mapas/*]: JavaScript/CSS for map rendering and smoothing/plotting utilities.
- [rutas/]: Folder holding example TCX files used for testing and import.

What’s contained in each file I created

- [README.md](README.md): This explanatory document.
- [requirements.txt](requirements.txt): The Python dependency list.

How to run the application (local development)

1) Create and activate a Python virtual environment (Windows example):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies:

```powershell
pip install -r requirements.txt
```

3) Apply migrations and create a superuser (optional):

```powershell
python manage.py migrate
python manage.py createsuperuser
```

4) Run the development server:

```powershell
python manage.py runserver
```

5) Open http://127.0.0.1:8000/ in your browser and browse the app pages under the `mapas` app.

Notes and additional information for reviewers

- Database: The project uses SQLite by default (db.sqlite3). If you need a working database snapshot, ensure `db.sqlite3` exists in the project root. If it was removed from the repo (gitignored), you can create an empty DB with the migration commands above and optionally import TCX files from the `rutas/` folder using any import script or admin pages included.
- Static files: The repo includes static JS/CSS in `mapas/static/mapas/` for visualization. For production, collectstatic and a proper static server are recommended.
- Security: Secret keys and production settings are not included. This repository is configured for local development only.
- If you want me to re-add `db.sqlite3` to the repository history (or undo a commit that removed it), tell me which commit to target and whether you want it re-introduced as a tracked file or left locally; I can perform a git commit amend, interactive rebase, or a reset depending on your preference.

Contact

If you want any changes to the README content or to add a database snapshot, tell me and I will update or add the files as requested.