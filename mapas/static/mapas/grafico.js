    
    function getElement(id) {
        const elemento = document.getElementById(id)
        if(!elemento) return null
        try {
            return JSON.parse(elemento.textContent)
        }   
        catch(error) {
            console.error(error)
    }}
    
        function suavizar(data, window) {
        const res = [...data]
        // Eliminar ceros o nulls al inicio
        let i = 0
        const mitad = Math.floor(window / 2)
        while(data[i] === 0 || data[i] === null) {
            //Indice del primer dato no nulo o distinto de 0
            i++;
            }

        for( let j = 0; j < i; j++) {
            res[j] = data[i]
        }
        
        for( let k = i; k < data.length; k++) {
            const start = k - Math.max(0, k - mitad);
            const end = Math.min(data.length, k + mitad + 1) 
            const parcial = data.slice(start, end)  
            parcial.sort((a, b) => a - b);
            const mediana = parcial.length % 2 === 1 ?
                parcial[Math.floor(parcial.length / 2)] :
                (parcial[parcial.length / 2 - 1] + parcial[parcial.length / 2]) / 2
        }
        return res
        }
        
        
        function kernel_gaussiano(size, sigma) {
            const kernel = [];
            const mean = size/2;
            let sum =0;
            for (let i = 0; i < size; i++) {
                const x = i - mean
                const value = Math.exp(-(x*x) / (2* sigma * sigma))
                kernel.push(value)
                sum += value
            }
            
            return kernel.map(v => v / sum)
        }

        function suavizar_gaussian(data, size, sigma) {
            if(!Array.isArray(data) || data.length === 0) return []

            const kernel = kernel_gaussiano(size, sigma)
            const med = Math.floor(size/2)
            const res = [];

            for(let i = 0; i < data.length; i++) {
                let sum =0;
                let weight_sum = 0;

                for(let j =0; j < size; j++) {
                    const ind = i - med + j;
                    if(ind >= 0 && ind < data.length) {
                        sum += data[ind] * kernel[j]
                        weight_sum += kernel[j]
                    }
                }
            res.push(sum / weight_sum)

             }
             return res;
        }

        function fillMissing(data) {
            let last = null;
            return data.map(val => {
                if(val == null || isNaN(val)) {
                    return last;
                }
                last = val;
                return val;
            })
        }
        
        function seconds_to_hms(seconds) {
            let h = Math.floor(seconds/3600).toString()
            let m =Math.floor( (seconds%3600)/60).toString()
            let s =Math.floor( seconds%60).toString()
            return `${h.padStart(2,0)}:${m.padStart(2,0)}:${s.padStart(2,0)}`
        }

        function hms_to_seconds(hms) {
            let h = 0;
            let m = 0;
            let s = 0;
            let data = hms.split(':')
            if (data.length === 3){
                h = parseInt(data[0])
                m = parseInt(data[1])
                s = parseInt(data[2])
                return ( s + m*60 + h*360)
            }
            else {
                m = parseInt(data[0])
                s = parseInt(data[1])
                return ( s + m*60)
            } 

        }

        function tominkmNumber(speed) {
            return 1000/ speed / 60
        }

        
        function suavizar_ritmo(speeds, factor) {
            let res = []
            let suma = 0
            let start = 0
            let end = factor
            /*for ( let i = 0; i < speeds.length; i+=factor) {
                let parcial = speeds.slice(i, end)
                parcial.sort((a, b) => a - b)
                let mediana = parcial.length % 2 === 1 ?
                    parcial[Math.floor(parcial.length / 2 )] :
                    (parcial[parcial.length / 2] + parcial[parcial.length / 2 + 1]) / 2
                res.push(mediana)
                end = end + factor
            }*/
            

            for(i = 0; i < speeds.length; i++) {
                suma += speeds[i]
                if ( i === end) {
                const valor = suma / factor
                const valorFiltrado = (valor < 1 ? 1 : valor > 10 ? 10 : valor)
                res.push(valorFiltrado)    
                start = i;
                end > speeds.length ? end = speeds.length : end = i + factor
                suma = 0 
                    }
            } 
            return (res)    
        }

       
        

    function createGraf() {    
        const grf = document.getElementById('graf')
        const gpuntos = getElement('puntos-data')

        if(!grf || ! gpuntos) return null

        const bpm = gpuntos.map(p => p.heart_rate);
        const altitudes = gpuntos.map(p => p.altitud);
        const distancias = gpuntos.map(p => p.distancia);
        const tiempos = gpuntos.map(p => p.time);
        const cadencias =gpuntos.map(c => c.cadencia);
        const speeds = gpuntos.map(c => c.speed);
        const pendientes = gpuntos.map(c => c.pendiente);
        const tiempos_calc = tiempos.map((c, i) => 
            Math.floor((Date.parse(c) - Date.parse(tiempos[0]))/1000)
        )
        const cadenciasFilled = fillMissing(cadencias)
        const altitudesFilled = fillMissing(altitudes)
        //const speedsFilled = suavizar_gaussian(speeds, 5, 1.0)
        //const speedsFilled = suavizar_ritmo(speeds, 10)
        const speedsFilled =suavizar_gaussian(suavizar_ritmo(speeds, 5), 5, 1.0)
        const ejex = Math.ceil(tiempos_calc.length / speedsFilled.length)
        const speedsExpanded = [];
        for (let i = 0; i < tiempos_calc.length; i++) {
            // Encuentra el índice correspondiente en speedsFilled
            const idx = Math.floor(i / ejex);
            speedsExpanded.push(speedsFilled[idx] !== undefined ? speedsFilled[idx] : null);
        }
        new Chart(grf, {
            type: 'line',
            data: {
                labels: tiempos_calc, distancias,
                datasets: [{
                    label: 'bpm',
                    data: bpm,
                    borderColor: 'rgba(245, 23, 25, 1)',
                    pointHoverColor: 'rgba(225, 22, 25, 1)',
                    },
                    {
                    label: 'Altitud',
                    data: suavizar_gaussian(altitudesFilled, 5, 1.0).map((c, i) => Math.floor(c)),
                    borderColor: 'rgba(12, 20, 250, 1)',
                    pointHoverColor: 'rgba(225, 225, 225, 1)',
                    fill: true,
                    backgroundColor: 'rgba(200, 200, 200, 0.5)'
                    } ,
                    {
                    label: 'Cadencia',
                    data: cadencias,
                    },
                    {
                    label: 'Ritmo',
                    data: speedsExpanded.map((c, i) => ({ 
                        x: tiempos_calc[i ], 
                        y: tominkmNumber(c)
                    })),
                    borderColor: 'rgba(145, 223, 25, 1)',
                    pointHoverColor: 'rgba(225, 225, 225, 1)',
                    cubicInterpolationMode: 'monotone',
                    yAxisID: 'y1',
                    tension : 0.1
                    } 
                    
                ]                 
                    ,
                    }
                ,
            options: {
                plugins: {
                    tooltip: {
                        backgroundColor: 'rgba(35,85,136,0.6)',
                        bodyColor: '#fff',
                        displayColors: 'true',
                        borderColor: '#fff',
                        callbacks: {
                            title: function(context) {
                                const xvalue = context[0].parsed.x;
                                const ind = context[0].dataIndex
                                const d = Math.floor(distancias[ind])
                                const t = seconds_to_hms(xvalue);
                                return `Distancia: ${d} m`
                            },
                            label: function(context) {
                                let label = context.dataset.label  || '';
                                let value = context.parsed.y;
                                let yvalue = context.parsed.y1
                                let xvalue = context.parsed.x
                                let ind = context.dataIndex
                                let lines = []
                                if (label === 'bpm' && value != null) {
                                    lines.push(`${label}: ${value} bpm`);}
                                if(label === 'Ritmo' && value != null) {
                                    const m = Math.floor(value)
                                    const s = Math.round((value - m) * 60)
                                    lines.push(`${label}: ${m}:${s.toString().padStart(2, 0)} min/km`);
                                    }
                                if(label === 'Cadencia' && value != null) {
                                    lines.push(`${label}: ${value}`)
                                }
                                if (label === 'Altitud' && value != null) {
                                    lines.push(`${label}: ${value} m`);}
                                return lines;
                            },
                            afterBody: function(context) {
                                let p = [];
                                let ind = context[0].dataIndex
                                if( pendientes && pendientes[ind] != null) {
                                    p.push(`Pendiente: ${pendientes[ind].toFixed(2)} %`)
                                }
                                return p;
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'index', 
                    intersect: false
                },
                    onHover: (event, activeElements) => {
                        if (activeElements.length > 0) {
                            const ind = activeElements[0].index;
                            if(ind < coords.length || coords[ind] !== undefined) {
                                const ptoX = coords[ind][0];
                                const ptoY = coords[ind][1];
                                updateMarker(ptoX, ptoY);
                            }
                        
                        }
                    },
                responsive: true,
                stacked: true,
                maintainAspectRatio: false,   
                fill: false,
                tension: 0.4,
                pointStyle: 'circle',
                pointRadius: 0,
                pointHoverBorderWidth: 3,
                backgroundColor: 'rgba(255, 255, 255, 1)',
                scales: {
                    y: {
                        beginAtZero: false, 
                        type: 'linear',
                        position: 'left',
                        tension: 1,
                    },
                    y1: {
                        type:'logarithmic',
                        position: 'right',
                        reverse: true,
                        suggestedMin: 0,
                        suggestedMax: 10,
                        tension: 1,
                        ticks: {
                            source: "auto"
                        }
                    },
                   
                     x: {
                        type: 'linear',
                        title: {
                            display: true,
                            text: 'Tiempo '},
                        display: true,
                        min: 0,
                        max: tiempos_calc[tiempos_calc.length - 1],
                        ticks: {
                            source: 'auto',
                            callback: function(value, index, values) {
                                const h = Math.floor(value / 3600);
                                const m = Math.floor((value % 3600) / 60);
                                const s = Math.floor(value % 60)
                            return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}` 
                            },
                           
                            }},
                    
            }
        }});
    }

    function createBars(){
    const bars = document.getElementById('bars')
    const dias = JSON.parse(document.getElementById('semana-data').textContent)
    if(!bars || !dias) return null

    const dia = dias.map(p => p.dia)
    const acum_distancias = dias.map(p => p.actividad ? p.actividad.acums.acum_distancia : null)
    const acum_tiempo = dias.map(p => p.actividad ? hms_to_seconds(p.actividad.acums.acum_tiempo) : null)
    
    window.barChart = new Chart(bars, {
        type: 'bar',
        data: {
            labels: dia,
            datasets: [{
                label: false,
                data: acum_tiempo,
                barThickness: 6,
                borderSkipped: true,
                }],
                    },
                options: {
                    plugins: {
                        legend: {
                        display: false
                    },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    let label = context.dataset.label || 'Tiempo'
                                    let value = seconds_to_hms(context.parsed.y)
                                    return `${value}`
                                }
                                }
                            },
                    },
                    scales: {
                        x: {
                            grid: {
                                display: false
                            },
                        },
                        y: {
                            display: false,
                            grid: {
                                display: false
                            }
                        }
                    }
                }
    })
            }

document.addEventListener('DOMContentLoaded', () => {
    createGraf()
    createBars()
})