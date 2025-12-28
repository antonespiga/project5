Project5 — Activities/routes repository

Overview

Project5 is a small Django web application for importing, parsing and visualizing GPS route/activity files (TCX). La aplicacion almacena los archivos .TCX en una carpeta y los parsea para extraer los datos necesarios para ser visualizados por el usuario en forma de gráfico de la actividad y con un mapa de la ruta de la actividad. The app is implemented under the `mapas` Django app and a lightweight project configuration in `project5`.

Distinctiveness and Complexity

This project meets distinctiveness and complexity requirements because:
- It implements a full-stack web application (Django backend + HTML/JS front-end) rather than a trivial script or single-file exercise.
- Existe similitud con el proyect 'Network' en el sentido de que en 'Network' se publican posts y en 'mapas' rutas, sin embargo, el tratamiento previo de los datos necesario para que estos puedan ser guardados y luego publicados creo que aporta una sustantiva diferencia.
- Se realizan tareas no triviales como: 
    · parsear los archivos TCX para obtener los datos y guardarlos en las estructuras de datos        apropiadas.
    · analizar los datos obtenidos para verificar que sean consistentes y que no haya vacios en ellos y si así fuera aplicar las correcciones necesarias.
    · tratar datos para corregir posibles lecturas erroneas y poder crear gráficas suavizadas, sin picos exagerados.
- Se utiliza Leaflet y Folium para generar los mapas a partir de las coordenadas obtenidas.
- Se emplea Charjs para crear los distintos tipos de gráficos (linea, barras, burbujas).

What I created (file list and contents)

- README.md: This file — project overview, distinctiveness statement, file list, run instructions, and notes for reviewers.
- requirements.txt: Pinning the Python packages needed to run the site locally.

Key repository files (high level)

- [manage.py](manage.py): Django CLI entrypoint to runserver, migrate, etc.
- [project5/settings.py](project5/settings.py): Django settings for the project.
- [project5/urls.py](project5/urls.py): URL router.
- [mapas/models.py](mapas/models.py): Django models describing activities and users.
- [mapas/views.py](mapas/views.py): Request handlers and page views.
- [mapas/tcx_parse_calc.py]: TCX parsing and calculation utilities used to import and process route files.
- [mapas/static/mapas/*]: JavaScript/CSS for map rendering and smoothing/plotting utilities.
- [rutas/]: Folder to save imported TCX files.

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
