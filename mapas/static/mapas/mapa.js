const coords = JSON.parse(document.getElementById('coords-data').textContent);
const map = L.map('map').setView(coords[0], 13);

        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        const polyline = L.polyline(coords, { color: 'blue' }).addTo(map);

        map.fitBounds(polyline.getBounds());

        const mark = L.circleMarker(coords[0], {
            radius: 6,
            fillColor:'green',
            color: 'green',
            weight: 1,
            fillOpacity: 0.6,
        }).addTo(map)

        map.invalidateSize();

        function updateMarker(lat, lon) {
            mark.setLatLng([lat, lon])
        }