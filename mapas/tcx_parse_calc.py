import datetime
import os
import xml.etree.ElementTree as ET
import numpy as np
import calendar
from math import floor
from geopy.distance import geodesic
from datetime import datetime
#from .utils import getUbicacion
import logging, requests

logger = logging.getLogger(__name__)



def revisar_puntos(puntos):
    # Extraer datos por categorias
    long = len(puntos)
    altitudes = [punto.get("altitud") for punto in puntos]
    speeds = [punto.get("speed") for punto in puntos]
    coords = [punto.get("coordenadas") for punto in puntos]
    

    # Filtrar los datos
    if(not isNone(speeds)):
        speedsFiltered = suavizar_ritmo(speeds, 5)
    

    # Rellenar datos faltantes
    speedsFilled = fill_speeds(speedsFiltered, long)
   
    altitudesFilled = fillData(altitudes, long) if altitudes is not None else None
    
    #print(altitudesFilled)
    
    coordenadasFilled = fillData(coords, long) if coords is not None else None
    altitudesFilledFiltered = filtrar_altitud(altitudesFilled) if not isNone(altitudesFilled) else None
    

    for i, p in enumerate(puntos):
        p["speed"] = speedsFilled[i]
        p["altitud"] = altitudesFilledFiltered[i] if altitudesFilledFiltered is not None else None
        p["coordenadas"] = coordenadasFilled[i] if coordenadasFilled is not None else None
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
        if(not isNone(data[p])):
            res.append(0 if float(data[p]) < -10 else data[p])
    return res

def fillData(data, long):
    res = []
    last = None if len(data) == 1 else [None, None]
    first = 0
    while isNone(data[first]) and first < len(data) - 1:
        first += 1
    if(first == len(data) -1):
        print('No hay datos')
        return None
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


def isNone(data):
    return None in data if type(data).__name__ == 'list' else  type(data).__name__ == 'NoneType'


def parse_calc_tcx(file):
    tree = ET.parse(file)
    root = tree.getroot()
    ns = {"tcx": "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"}

    lap_data = [];
    times = [];
    distances = []; hrs = []; altitudes = []; coords = []; cadences = []; paces = []; speeds = [];
    puntos = []

    for activities in root.findall("tcx:Activities", ns):
        act = activities.find("tcx:Activity", ns)
        sport = act.get("Sport")
        for activity in activities.findall(".//tcx:Activity", ns):
            t_distance = 0;
            geo_distance = 0;
            acum_distancia_b = 0;
            acum_tiempo = 0;
            ant_dist = 0;
            acum_dist = 0;
            acum_hr = 0;
            acum_subida = 0;
            acum_bajada = 0;
            h_max = 0;
            h_min = 50000; 
            hr_max = 0;
            h_ant = -5555;
            pend = 0;
            fecha = activity.find("tcx:Id", ns)
           
            for lap in activity.findall("./tcx:Lap", ns):
                lap_time_b = lap.find("tcx:TotalTimeSeconds", ns)
                lap_distance = lap.find("tcx:DistanceMeters", ns)
                lap_avg_hr = lap.find("tcx:AverageHeartRateBpm/tcx:Value", ns) 
                lap_max_hr = lap.find("tcx:MaximumHeartRateBpm/tcx:Value", ns)
                lap_max_speed_b = lap.find("tcx:MaximumSpeed", ns)
                lap_cadence = lap.find("tcx:Cadence", ns)
                lap_subida = 0;
                lap_bajada = 0;
                lap_h_inicio = -1000;
                lap_h_actual = 0;
                
                
                for lap_altitude in lap.findall("./tcx:Track/tcx:Trackpoint", ns):
                    altitude = lap_altitude.find("tcx:AltitudeMeters", ns) if (lap_altitude is not None) else None
                
                    if(altitude is not None):
                        if(lap_h_inicio == -1000):
                            lap_h_inicio = altitude.text
                            lap_h_actual = altitude.text
                        else:
                            lap_gap = float(altitude.text) - float(lap_h_actual)

                            if(lap_gap > 0):
                                lap_subida += lap_gap
                                lap_h_actual = altitude.text
                            else:
                                lap_bajada += lap_gap
                                lap_h_actual = altitude.text
                if lap_max_hr is not None:
                    if (float(lap_max_hr.text) > float(hr_max)):
                        hr_max = lap_max_hr.text

                acum_distancia_b += float(lap_distance.text) / 1000
                acum_distancia = f"{round(acum_distancia_b, 2):.2f}".rstrip('0').rstrip('.')
                lap_time = seconds_to_hms(float(lap_time_b.text))
                lap_pace = to_minkm(float(lap_distance.text) / float(lap_time_b.text))
                lap_max_speed = to_minkm(float(lap_max_speed_b.text))
                lap_avg_speed = to_minkm(float(lap_distance.text) / float(lap_time_b.text))
                lap_data.append({
                "lap_time": lap_time,
                "lap_distance": lap_distance.text if lap_distance is not None else None,
                "lap_avg_hr": lap_avg_hr.text if lap_avg_hr is not None else None,
                "lap_max_hr": lap_max_hr.text if lap_max_hr is not None else None,
                "lap_max_speed": lap_max_speed,
                "lap_avg_speed": lap_avg_speed,
                "lap_cadence": lap_cadence.text if lap_cadence is not None else None,
                "lap_pace": lap_pace,
                "acum_distancia": acum_distancia,
                "lap_subida": f"{float(lap_subida):.0f}",
                "lap_bajada": f"{float(lap_bajada):.0f}"
                    })
                
                for track in lap.findall("./tcx:Track", ns):
                    inicio = True
                    coord_ant = None
                    speed = 0
                    avg_speed=0;
                    act_speed = 0;
                    h_inicio = -1000;
                   
                    h_actual = 0;
                    for trackpoint in track.findall("./tcx:Trackpoint", ns):
                        time = trackpoint.find("tcx:Time",ns)
                        distance = trackpoint.find("tcx:DistanceMeters", ns)
                        hr = trackpoint.find("tcx:HeartRateBpm/tcx:Value", ns)
                        altitude = trackpoint.find("tcx:AltitudeMeters", ns)
                        latitude = trackpoint.find("tcx:Position/tcx:LatitudeDegrees", ns)
                        longitude = trackpoint.find("tcx:Position/tcx:LongitudeDegrees", ns)
                        
                        cadence = trackpoint.find("tcx:Cadence", ns)

                        if time is not None:
                            acum_tiempo += 1;
                            times.append(time.text)
                            if distance is not None:
                                speed = to_minkm(float(distance.text) / float(acum_tiempo))
                            avg_speed = speed
                        if distance is not None:
                            gap = float(distance.text) - acum_dist;
                            act_speed = (float(gap))
                            speeds.append(act_speed)
                            acum_dist = float(distance.text)
                            distances.append(distance.text)
                        if hr is not None:
                            acum_hr += float(hr.text)
                            hrs.append(hr.text)
                        if altitude is not None :
                            if(h_inicio == -1000):
                                h_inicio = altitude.text
                                h_actual = altitude.text
                            else:
                                gap = float(altitude.text) - float(h_actual)
                                if(gap > 0):
                                    acum_subida += gap;
                                    h_actual = altitude.text
                                else:
                                    acum_bajada += gap;
                                    h_actual = altitude.text
                            if float(altitude.text) > (h_max):
                                h_max = floor(float(altitude.text))
                            elif float(altitude.text) < (h_min):
                                h_min = floor(float(altitude.text))
                            altitudes.append(altitude.text)
                        else: 
                            None
                        if longitude is not None and latitude is not None :
                            coord = [float(latitude.text), float(longitude.text)]
                            if inicio:
                                coord_ant =  coord
                                if float(h_ant) < -5000 and altitude is not None:
                                    h_ant = float(altitude.text)
                                geo_distance = 0.0    
                                inicio = False
                            else:
                                coords.append(coord)
                                geo_distance = g_distance(coord, coord_ant)
                                if altitude is not None and geo_distance > 0:
                                        pend = ((float(altitude.text) - float(h_ant)) / float(geo_distance)) * 100
                                        h_ant = float(altitude.text)
                                t_distance += geo_distance
                                coord_ant = coord
                                if distance is not None:
                                    gap = float(distance.text) - ant_dist;
                                    ant_dist = float(distance.text)
                        else:
                            coord = [None, None]
                        if cadence is not None:
                            cadences.append(cadence.text)
                        if lap_pace is not None:
                            paces.append(lap_pace)
                        
                        punto = {
                            "coordenadas": coord if coord is not None else [None, None],
                            "cadencia": cadence.text if cadence is not None else None,
                            "heart_rate": hr.text if hr is not None else None,
                            "altitud": altitude.text if altitude is not None else None,
                            "distancia": distance.text if distance is not None else None,
                            "geo_distance": geo_distance if geo_distance is not None else None,
                            "t_distance": t_distance if geo_distance is not None else None,
                            "time": time.text if time.text is not None else None,
                            "pendiente": pend if pend is not None else None,
                            "speed": act_speed if act_speed is not None else None
                        }
                        puntos.append(punto)
                
    puntos_revisados = revisar_puntos(puntos)
    #print(puntos_revisados)
    #print((datetime.fromisoformat(fecha.text)).strftime("%A, %d de %B de %Y"))
    
    ubicacion = getUbicacion(puntos_revisados[0].get("coordenadas"))
    return {
        "puntos": puntos_revisados,
        "lap_data":lap_data,
        "fecha": fecha.text,
        "ubicacion": ubicacion,
        "sport": sport,
        "tiempo": acum_tiempo,
        "distancia":  f"{acum_dist / 1000:.2f}",
        "subida": f"{acum_subida:.0f}",
        "fc_med": f"{acum_hr / acum_tiempo:.0f}"  ,
        "ritmo": avg_speed,
        "acums": {
            "acum_tiempo": seconds_to_hms(acum_tiempo),
            "acum_distancia":  f"{acum_dist / 1000:.2f}",
            "acum_hr": f"{acum_hr / acum_tiempo:.0f}"  ,
            "acum_subida": f"{acum_subida:.0f}",
            "acum_bajada": f"{acum_bajada:.0f}",
            "altura_max": f"{float(h_max):.0f}",
            "hr_max": hr_max,
            "h_max": h_max,
            "h_min": h_min,
            "avg_speed": avg_speed,
            "max_speed": to_minkm(max(speeds))
            }
        }
  

def g_distance(a, b):
    return geodesic(a, b).m

def seconds_to_hms(sec):
    seconds = int(sec)
    h = int((seconds) / 3600);
    m = int(((seconds%3600)  / 60));
    s = int((seconds) % 60)

    if h < 1 :
        return f"{m:02}:{s:02}"
    else:    
        return f"{h:02}:{m:02}:{s:02}"

def to_minkm(speed):
    if speed > 0:
        return seconds_to_hms(1000/speed) 

def speed_filter(data, window_size=5):
    filtered = np.convolve(data, np.ones(window_size) / window_size, mode='same')      
    filtered_formatted = []
    for x in filtered:
        filtered_formatted.append(to_minkm(x))
    return filtered_formatted

def getUbicacion(coord):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}
    try:
        res = requests.get(f'https://photon.komoot.io/reverse?lon={coord[1]}&lat={coord[0]}', headers=headers)
        print(res)
        location = res.json().get('features')[0].get('properties')
        
        print('location')
    except Exception as e:
        print(e)
        location = None
    print(f"location: {location}")
    return location

if __name__ == "__main__":
    file_path = os.path.join( os.path.dirname( os.getcwd()) , "rutas", "anton_espiga_2025-10-18_13-23-40.TCX")
    parse_calc_tcx(file_path)
    
