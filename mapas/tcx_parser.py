import xml.etree.ElementTree as ET

def parse_tcx(file):
    times, coords, alts, dists, bpms, cads = [], [], [], [], [], []
    tree = ET.parse(file)
    root = tree.getroot()
    ns = {"tcx": "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"}

    for trackpoint in root.findall('.//tcx:Trackpoint', ns):
        time = trackpoint.find("tcx:Time", ns)
        lat = trackpoint.find("tcx:Position/tcx:LatitudeDegrees", ns)
        lon = trackpoint.find("tcx:Position/tcx:LongitudeDegrees", ns)
        alt = trackpoint.find("tcx:AltitudeMeters", ns)
        dist = trackpoint.find("tcx:DistanceMeters", ns)
        bpm = trackpoint.find("tcx:HeartRateBpm/tcx:Value", ns)
        cad = trackpoint.find("tcx:Cadence", ns)

        if time is not None:
            times.append(time.text)
        if lat is not None:
            coords.append([float(lat.text), float(lon.text)])
        if alt is not None:
            alts.append(alt.text)
        if dist is not None:
            dists.append(dist.text)
        if bpm is not None:
            bpms.append(bpm.text)
        if cad is not None:
            cads.append(cad.text)
    return {"times": times, "coordenadas": coords, "altitudes": alts, "distancias": dists, "bpms": bpms, "cadencias": cads }       

