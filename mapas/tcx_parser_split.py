import os
import xml.etree.ElementTree as ET
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

# --- Haversine: calcula distancia entre dos coords (m) ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # radio de la Tierra en metros
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1-a))

# --- Parsear TCX ---
def parse_tcx(file_path):
    ns = {"tcx": "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"}
    tree = ET.parse(file_path)
    root = tree.getroot()

    trackpoints = []
    for tp in root.findall(".//tcx:Trackpoint", ns):
        time_elem = tp.find("tcx:Time", ns)
        pos_elem = tp.find("tcx:Position", ns)
        hr_elem = tp.find(".//tcx:HeartRateBpm/tcx:Value", ns)

        if time_elem is None or pos_elem is None:
            print('vacio')
            continue

        time = datetime.fromisoformat(time_elem.text.replace("Z", "+00:00"))
        lat = float(pos_elem.find("tcx:LatitudeDegrees", ns).text)
        lon = float(pos_elem.find("tcx:LongitudeDegrees", ns).text)
        hr = int(hr_elem.text) if hr_elem is not None else None

        trackpoints.append((time, lat, lon, hr))
    return trackpoints

# --- Cálculo de métricas ---
def calcular_metricas(trackpoints):
    total_dist = 0
    total_time = 0
    hr_sum = 0
    hr_time = 0

    dist_acum = 0
    km_splits = []
    split_dist = 0
    split_time = 0
    split_hr_sum = 0
    split_hr_time = 0

    for i in range(1, len(trackpoints)):
        t1, lat1, lon1, hr1 = trackpoints[i-1]
        t2, lat2, lon2, hr2 = trackpoints[i]

        dt = (t2 - t1).total_seconds()
        d = haversine(lat1, lon1, lat2, lon2)

        total_dist += d
        total_time += dt

        # HR ponderado por tiempo
        if hr1 and hr2:
            hr_avg_segment = (hr1 + hr2) / 2
            hr_sum += hr_avg_segment * dt
            hr_time += dt

        # Split por km
        split_dist += d
        split_time += dt
        if hr1 and hr2:
            split_hr_sum += hr_avg_segment * dt
            split_hr_time += dt

        if split_dist >= 1000:  # cerramos split de 1 km
            km_splits.append({
                "dist": split_dist,
                "time": split_time,
                "pace": split_time / (split_dist/1000),  # seg/km
                "hr": split_hr_sum / split_hr_time if split_hr_time > 0 else None
            })
            split_dist = 0
            split_time = 0
            split_hr_sum = 0
            split_hr_time = 0

    # Métricas globales
    pace = total_time / (total_dist/1000) if total_dist > 0 else None
    hr_avg = hr_sum / hr_time if hr_time > 0 else None

    return {
        "dist_total_km": total_dist/1000,
        "tiempo_total_s": total_time,
        "ritmo_medio": pace,  # seg/km
        "bpm_medio": hr_avg,
        "splits": km_splits
    }

# --- Ejemplo de uso ---
if __name__ == "__main__":
    file_path = os.path.join( os.path.dirname( os.getcwd()) , "rutas", "anton_espiga_2025-08-03_13-01-11.TCX")
    print(file_path)
    trackpoints = parse_tcx(file_path)
    metrics = calcular_metricas(trackpoints)

    print(f"Distancia total: {metrics['dist_total_km']:.2f} km")
    print(f"Tiempo total: {metrics['tiempo_total_s']/60:.1f} min")
    print(f"Ritmo medio: {metrics['ritmo_medio']/60:.2f} min/km")
    print(f"BPM medio: {metrics['bpm_medio']:.1f} bpm")
    print("\nSplits por km:")
    for i, split in enumerate(metrics["splits"], 1):
        print(f"Km {i}: ritmo {split['pace']/60:.2f} min/km, HR {split['hr']:.0f}")
