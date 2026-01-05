function getElement(id) {
    const elemento = document.getElementById(id)
    if(!elemento) return null
    try {
          return JSON.parse(elemento.textContent)
        }   
        catch(error) {
            console.error(error)    
}
}

let mark;

function activity_map() {
    const puntos = getElement('puntos-data');
    if(!puntos) return null;
    const coords = puntos.map(p => p.coordenadas) 
    const map = L.map('map').setView(coords[0], 13);

        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        const polyline = L.polyline(coords, { color: 'blue' }).addTo(map);

        map.fitBounds(polyline.getBounds());
        mark = L.circleMarker(coords[0], {
            radius: 6,
            fillColor:'green',
            color: 'green',
            weight: 1,
            fillOpacity: 0.6,
        })
        mark.addTo(map)
        map.invalidateSize();
}

function updateMarker(lat, lng) {
            mark.setLatLng([lat, lng])
        }

function all_map() {
    let coords = [];
    const acts = getElement('acts');

    if(!acts) return null;
    acts.forEach(act => {
        if(act.ubicacion && act.ubicacion.extent) {
            const lon = act.ubicacion.extent[0];
            const lat = act.ubicacion.extent[1];
            coords.push([lat, lon]);
        }
    });
    if(coords.length === 0) return null;

    const map = L.map('all_map').setView(coords[0], 11);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    const markersGroup = L.markerClusterGroup();
    coords.forEach(mark => {
        markersGroup.addLayer(L.marker(mark));
        })

    map.addLayer(markersGroup);
    
    try {
        map.fitBounds(markersGroup.getBounds());
    } catch (e) {
        // si hay un solo marcador, getBounds puede fallar; ignorar
    }
}

document.addEventListener('onHoverGrafico', e => {
    const ind = Math.floor(e.detail.dist / 1000)
    console.log(ind)
    const {lat, lng } = e.detail;
    const marker = L.marker(e.detail.splits[e.detail.dist])
    map.addLayer(marker)
    mark.setLatLng([lat, lng]);
    
})

document.addEventListener('DOMContentLoaded', () => {
activity_map()
all_map()
 })

