import datetime
import os
import xml.etree.ElementTree as ET
import numpy as np
from math import floor
from geopy.distance import geodesic


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
            lap_h_inicio = -1;
            lap_h_actual = 0;
            h_max = 0;
            h_min = 50000; 
            hr_max = 0;
            h_ant = -5555;
            pend = 0;
            fecha = activity.find("tcx:Id", ns)
            
            
            for lap in activity.findall("./tcx:Lap", ns):
                lap_subida = 0;
                lap_bajada = 0;
                lap_time_b = lap.find("tcx:TotalTimeSeconds", ns)
                lap_distance = lap.find("tcx:DistanceMeters", ns)
                lap_avg_hr = lap.find("tcx:AverageHeartRateBpm/tcx:Value", ns)
                lap_max_hr = lap.find("tcx:MaximumHeartRateBpm/tcx:Value", ns)
                lap_max_speed_b = lap.find("tcx:MaximumSpeed", ns)
                lap_cadence = lap.find("tcx:Cadence", ns)
                for lap_altitude in lap.findall("./tcx:Track/tcx:Trackpoint", ns):
                    altitude = lap_altitude.find("tcx:AltitudeMeters", ns)
                
                    if(altitude is not None):
                        if(lap_h_inicio == -1):
                            lap_h_inicio = altitude.text
                            lap_h_actual = altitude.text
                        else:
                            lap_gap = float(altitude.text) - float(lap_h_actual)
                            if(lap_gap > 0):
                                lap_subida += lap_gap
                                acum_subida += lap_gap;
                                lap_h_actual = altitude.text
                            else:
                                lap_bajada += lap_gap
                                acum_bajada += lap_gap;
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
                "lap_distance": lap_distance.text,
                "lap_avg_hr": lap_avg_hr.text,
                "lap_max_hr": lap_max_hr.text,
                "lap_max_speed": lap_max_speed,
                "lap_avg_speed": lap_avg_speed,
                "lap_cadence": lap_cadence.text,
                "lap_pace": lap_pace,
                "acum_distancia": acum_distancia,
                "lap_subida": f"{float(lap_subida):.0f}",
                "lap_bajada": f"{float(lap_bajada):.0f}"
                    })
            
                for track in lap.findall("./tcx:Track", ns):
                    inicio = True
                    coord_ant = None
                    avg_speed = 0;
                    lap_h_inicio = -1;
                    lap_h_actual = 0;
                    for trackpoint in track.findall("./tcx:Trackpoint", ns):
                        time = trackpoint.find("tcx:Time",ns)
                        distance = trackpoint.find("tcx:DistanceMeters", ns)
                        hr = trackpoint.find("tcx:HeartRateBpm/tcx:Value", ns)
                        altitude = trackpoint.find("tcx:AltitudeMeters", ns)
                        longitude = trackpoint.find("tcx:Position/tcx:LongitudeDegrees", ns)
                        latitude = trackpoint.find("tcx:Position/tcx:LatitudeDegrees", ns)
                        cadence = trackpoint.find("tcx:Cadence", ns)

                        if time is not None:
                            acum_tiempo += 1;
                            times.append(time.text)
                            if distance is not None:
                                speed = to_minkm(float(distance.text) / float(acum_tiempo))
                                avg_speed = speed
                            else:
                                speed = 0;
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
                            if float(altitude.text) > (h_max):
                                h_max = floor(float(altitude.text))
                            elif float(altitude.text) < (h_min):
                                h_min = floor(float(altitude.text))
                            altitudes.append(altitude.text)
                        else: 
                            None
                        if longitude is not None:
                            if inicio:
                                coord_ant =  [float(latitude.text), float(longitude.text)]
                                if float(h_ant) < -5000:
                                    if altitude is not None:
                                        h_ant = float(altitude.text)
                                inicio = False
                            else:
                                coord = [float(latitude.text), float(longitude.text)]
                                coords.append(coord)
                                geo_distance = g_distance(coord, coord_ant)
                                if altitude is not None:
                                    if geo_distance > 0:
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
                            "coordenadas": coord,
                            "cadencia": cadence.text if cadence is not None else None,
                            "heart_rate": hr.text if hr is not None else None,
                            "altitud": altitude.text if altitude is not None else None,
                            "distancia": distance.text if distance is not None else None,
                            "geo_distance": geo_distance,
                            "t_distance": t_distance,
                            "time": time.text,
                            "pendiente": pend
                        }
                       
                        puntos.append(punto)
      
    return {
        "puntos": puntos,
        "lap_data":lap_data,
        "fecha": fecha.text,
        "sport": sport,
        "times": times,
        "distancias": distances,
        "hrs": hrs,
        "altitudes":altitudes,
        "coordenadas":coords,
        "cadencias":cadences,
        "speeds": (speeds),
        "paces": paces,
        "acums": {
            "acum_tiempo": seconds_to_hms(acum_tiempo),
            "acum_distancia":  f"{acum_dist:.2f}",
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

if __name__ == "__main__":
    file_path = os.path.join( os.path.dirname( os.getcwd()) , "rutas", "anton_espiga_2025-08-03_13-01-11.TCX")
    parse_calc_tcx(file_path)
