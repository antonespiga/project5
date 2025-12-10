import os
import folium
from html2image import Html2Image
from django.conf import settings
import json
from math import pow, floor
from .tcx_parse_calc import parse_calc_tcx
import logging, requests

logger = logging.getLogger(__name__)


def revisar_puntos(puntos):
    # Extraer datos por categorias
    long = len(puntos)
    altitudes = [punto.get("altitud") for punto in puntos]
    speeds = [punto.get("speed") for punto in puntos]
    coords = [punto.get("coordenadas") for punto in puntos]
    distancias = [punto.get("distancias") for punto in puntos]
    cadencias = [punto.get("cadencias") for punto in puntos]

    # Filtrar los datos
    speedsFiltered = suavizar_ritmo(speeds, 5)
    

    # Rellenar datos faltantes
    speedsFilled = fill_speeds(speedsFiltered, long)
    
    altitudesFilled = fillData(altitudes, long)
    
    #print(altitudesFilled)
    coordenadasFilled = fillData(coords, long)
    altitudesFilledFiltered = filtrar_altitud(altitudesFilled)
    distanciasFilled = fillData(distancias, long)
    cadenciasFilled = fillData(cadencias, long)

    for i,p in enumerate(puntos):
        p["speed"] = speedsFilled[i]
        p["altitud"] = altitudesFilledFiltered[i]
        p["coordenadas"] = coordenadasFilled[i]
        p["distancias"] = distanciasFilled[i]
        p["cadencias"] = cadenciasFilled[i]
    
    return puntos

def suavizar_ritmo(data, factor):
    sum = 0
    i = 0
    end = factor
    res = []
    for p in range(0, len(data)):
        sum+= data[p]
        i+=1
        if (i == factor):
            valor = float (sum / factor)
            valorFiltrado = 1 if valor < 1 else 10 if valor > 10 else valor
            res.append(valorFiltrado)
            end += factor
            sum = 0
            i = 0
    return res

def fill_speeds(speedsFiltered, long):
    res = []
    for i in range(0, long):
       idx = (i / (long / len(speedsFiltered))).__floor__()
       res.append(speedsFiltered[idx]) 
    return res

def filtrar_altitud(data):
    res = []
    for p in range(0, len(data)):
        res.append(0 if float(data[p]) < -10 else data[p])
    return res

def fillData(data, long):
    res = []
    last = None if len(data) == 1 else [None, None]
    first = 0
    while isNone(data[first]):
        first += 1
    for i in range(0, first):
        res.append(data[first])
    last = data[first]
    for i in range(first, long):
        if(isNone(data[i])):
            res.append(last)
        else:
            res.append(data[i])
            last = data[i]
    return res

def normalize_data(data):
    if isinstance(data, dict):
        return data
    if isinstance(data, str):
        try:
            parsed = json.loads(data)
        except Exception:
            return {}
        if isinstance(parsed, dict):
            return parsed
        if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
            return parsed[0]
        return {}
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return data[0]
    return {}

def isNone(data):
    return None in data if type(data).__name__ == 'list' else  type(data).__name__ == 'NoneType'

def crear_img(coords, id):
    m = folium.Map(location = coords[0], zoom_start=13)
    folium.PolyLine(coords).add_to(m)
    folium.Marker(coords[0], tooltip="Inicio", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(coords[-1], tooltip="Final", icon=folium.Icon(color="red")).add_to(m)
    
    html_path=os.path.join(settings.BASE_DIR, "rutas","rutas_html",f"{id}.html")
    m.save(html_path)
    png_path = os.path.join(settings.BASE_DIR,'mapas', 'static' ,"images_activities")
    hti = Html2Image(output_path=png_path, size=(600, 600))
    hti.screenshot(html_file=html_path, save_as= f"img_{id}.png")
    if(os.path.exists(html_path)):
        print(f"Eliminando archivo temporal {id}.html")
        os.remove(html_path)

def handle_data(activity):
    file = activity.archivo_tcx
    try:
        data = parse_calc_tcx(file)
    except Exception as e:
        logger.exception("Error al parsear datos id=%s: %s", activity.id, e)
        activity.puntos = []
        activity.bpm = []
        activity.coordenadas = []
        activity.altitudes = []
        activity.distancias = []
        activity.tiempos = []
        activity.cadencias = []
        activity.acums = {}
        activity.lap_data = {}
        activity.fecha = activity.fecha or None
        activity.sport = activity.sport or None
        activity.ubicacion = activity.ubicacion or None
        activity.imagen = None
        activity.save()
        return activity
    
    puntos = data.get("puntos", []) or []

    if not isinstance(activity.bpm, list): activity.bpm = []
    if not isinstance(activity.coordenadas, list): activity.coordenadas = []
    if not isinstance(activity.altitudes, list): activity.altitudes = []
    if not isinstance(activity.distancias, list): activity.distancias = []
    if not isinstance(activity.tiempos, list): activity.tiempos = []
    if not isinstance(activity.cadencias, list): activity.cadencias = []

    for punto in puntos:
        activity.bpm.append(punto["heart_rate"]) if punto["heart_rate"] is not None else None
        activity.coordenadas.append(punto["coordenadas"]) if punto["coordenadas"] is not None else [0,0]
        activity.altitudes.append(punto["altitud"])
        activity.distancias.append(punto["distancia"])
        activity.tiempos.append(punto["time"])
        activity.cadencias.append(punto["cadencia"])
    activity.lap_data = data["lap_data"]
    activity.acums = data["acums"]
    activity.fecha = data["fecha"]
    activity.sport = data["sport"]
    activity.ubicacion = data["ubicacion"]
    activity.imagen = f"img_{activity.id}.png"
    activity.puntos = puntos
   
    activity.save()
    if(activity.coordenadas):
        crear_img(activity.coordenadas, activity.id)
    return activity

def string_to_seconds(time):
    todo = time.split(":")
    l = len(todo)
    seconds = 0
    for i in range(l ):
        seconds += (int(pow(60, int(l-i-1))) * float(todo[i]))
    return seconds     

def seconds_to_string(seconds):
    int_seconds = int(seconds)
    h = floor(int_seconds / 3600)
    m = floor( (int_seconds % 3600) / 60)
    s = (int_seconds) % 60
    return(f"{h:2}h{m:02}m{s:02}s")


       