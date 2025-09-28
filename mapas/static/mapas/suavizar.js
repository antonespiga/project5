function suavizar_ritmo(speeds, factor) {
            let res = []
            let suma = 0
            let start = 0
            let end = factor
            for ( let i = 0; i < speeds.length; i+=factor) {
                const parcial = speeds.slice(i, end)
                parcial.sort((a, b) => a - b)
                const mediana = parcial.length % 2 === 1 ?
                    parcial[Math.floor(parcial.length / 2) ] :
                    (parcial[parcial.length / 2] + parcial[parcial.length / 2 - 1]) / 2
                res.push(mediana)
                end = end + factor
            }
            

           /* for(i = 0; i < speeds.length; i++) {
                suma += speeds[i]
                if ( i === end) {
                res.push(suma / factor)    
                start = i;
                end > speeds.length ? end = speeds.length : end = i + factor
                suma = 0 
                    }
            } */
            //console.log(res) 
            return (res)    

        }

        speeds = [2.5,3.8,3.1,3.02,2.15,2.14,3.2,2.01,4.2,5.3,10.3,1.02,2,3.6,2.5,1.5,6.2,1.2,3.2,3.6,2.9,1.2]
        console.log(suavizar_ritmo(speeds, 4))
