# Project5 — Activities / Routes repository

## Overview

Project5 is a small Django web application for importing, parsing, and visualizing GPS activity/route files (TCX). The application stores uploaded `.TCX` files in the `rutas/` folder and parses them to extract the data required to display activity charts and a route map to users. The app logic lives in the `mapas` Django app and the project configuration is in the `project5` package.

## Features

- Import and parse TCX files into Django models
- Data validation and basic cleaning to remove spikes and handle missing values
- Activity charts using Chart.js (line, bar, bubble)
- Route maps using Leaflet (Folium is used for optional static map generation utilities)

## Distinctiveness and Complexity

This project goes beyond a simple example by combining file parsing, time-series data cleaning, and geospatial visualization into a cohesive Django application. Key points that make the project distinctive and non-trivial:

- TCX parsing and data modeling: The app reads TCX XML files, extracts hierarchical time-series and GPS data, and stores them in normalized Django models while preserving relationships (activities → laps → trackpoints).
- Data validation and smoothing: The project implements checks for missing or inconsistent timestamps, errant GPS jumps, and implausible sensor readings, and applies smoothing/cleaning where appropriate to produce reliable charts and maps.
- Time-series calculations: It computes derived metrics (distance, pace, cadence, heart-rate zones, elevation gain/loss) across time and distance windows, which requires careful handling of cumulative and sampled data.
- Geospatial rendering and integration: Coordinates are rendered interactively with Leaflet and optionally pre-rendered with Folium; syncing map position with charted data points adds UI complexity.
- Front-end visualization: Interactive charts with Chart.js (multiple series, different chart types, hover-linked map/chart interactions) require coordinated client-side code and data shaping APIs from Django views.
- Robust import workflow: The project handles bulk or single-file imports, preserves original files in `rutas/`, and provides admin tooling for re-processing or deleting imports.

Together these elements create a multi-layered project that demonstrates backend parsing and modeling, algorithmic data processing, and integrated front-end visualization — fulfilling distinctiveness and complexity expectations.

## Key files

- [manage.py](manage.py) — Django CLI entrypoint
- [project5/settings.py](project5/settings.py) — Django settings
- [project5/urls.py](project5/urls.py) — URL router
- [mapas/models.py](mapas/models.py) — Django models for activities and related data
- [mapas/views.py](mapas/views.py) — HTTP views and page handlers
- [mapas/tcx_parse_calc.py](mapas/tcx_parse_calc.py) — TCX parsing and calculation utilities 
- [mapas/static/mapas/] — JavaScript/CSS for map rendering and charting
- [rutas/] — Folder that stores imported `.TCX` files
- [requirements.txt](requirements.txt) — Python dependencies

## What's contained in each file I created

- `README_en.md`: This English project overview, run instructions, and reviewer notes.
- `mapas/tcx_parse_calc.py`: Core TCX parsing, using smoothing and data-cleaning helpers to obtain lap data, activity's global data and each point`s data.
- `mapas/utils.py`: Miscellaneous helper utilities used across the app (convert seconds to 'hh:mm:ss' form, fill missing data, smooth data).
- `rutas/` (directory): Storage for original `.TCX` files used for import; these files are preserved for re-processing or auditing.
- `mapas/static/capturas/`: Some screenshots in png format to show in de index.html page.
- `mapas/static/icons/`: Icons used in the application.
- `mapas/static/images_activities/`: Stores routes maps in png format (created with Folium and html2Image) to be shown in the dashboard page like a miniature.
- `mapas/static/mapas/grafico.js`: Front-end logic to create the graphics used in the application (bars, lines, bubbles).
- `mapas/static/mapas/mapa.js`: Front-end logic to create the activity´s route map from the obtained coordinates.
- `mapas/templates/mapas/activities_mes.html`: File to show a calendar with the activities registered in the selected month. It shows a sport icon and distance in the activity`s date place and a week resume (number of activities, total time and total distance).

![alt text](<Captura de pantalla 2025-12-26 214013.png>)
- `mapas/templates/mapas/activities_semana.html`: File to show the activities registered in the selected week. It shows a list with this week´s activities and a bubble graphic with the bubble´s size proportional to the activity distance. It also shows a bar graphic of the activities distance.

![alt text](<Captura de pantalla 2025-12-27 233016.png>)
- `mapas/templates/mapas/activities_year.html`: File to show the activities registered in the selected year. It has a bar graphic with each month's activities distance.Also shows the year`s number of activities and the total distance and time. Below this is shown a grid with each month and its data( number of activities and total time).

![alt text](<Captura de pantalla 2025-12-27 232739-1.png>)
- `mapas/templates/mapas/activities.html`: File to show a list of all the activities / my activities.
- `mapas/templates/mapas/activity_view.html`: File to show the selected activity. It shows:
    · the route map

    ![alt text](<Captura de pantalla 2025-12-27 233219.png>)

    · a line graphic representing bpm, altitude, pace, cadence

    ![alt text](<Captura de pantalla 2025-12-27 233232.png>)
    · a table with each lap (kilometer) data

    ![alt text](<Captura de pantalla 2025-12-27 233245.png>)

- `mapas/templates/mapas/agregar.html`: File with the form to add an activity.
- `mapas/templates/mapas/dashboard.html`: File to show:
    · total number of activities, time and distance.
    · last activity`s name and date
    · last week`s calendar with the activity´s sport icon in its date place.
    . a link to the list of activities.
    · a line graphic to represent actual week´s activities divided by sport.

    ![alt text](<Captura de pantalla 2025-12-27 232005.png>)
- `mapas/templates/mapas/delete_activity.html`: File to show a form to confirm or cancel to delete of an activity.
- `mapas/templates/mapas/index.html`: File to show the application index page, with some screenshots of the application and a short description of its properties.
- `mapas/templates/mapas/layout.html`: Base file to all the html files. It implements a header with different elements depending the user is authenticated or not.
- `mapas/templates/mapas/login.html`: File to show the login form.
- `mapas/templates/mapas/profile_fisico.html`: File to show the user's physic data.
- `mapas/templates/mapas/profile.html`: File to show the user's personal data.
- `mapas/templates/mapas/register.html`: File to show the register form.
- `mapas/forms.py`: Django forms to login / register users and add / delete activities.

## How to run (local development)

1. Create and activate a Python virtual environment (Windows example):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Apply migrations and (optionally) create a superuser:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

4. Run the development server:

```powershell
python manage.py runserver
```

5. Open `http://127.0.0.1:8000/` in your browser and navigate to the `mapas` app pages.





