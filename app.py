import streamlit as st
import streamlit.components.v1 as components

# 1. Configurazione base della pagina Streamlit
st.set_page_config(
    page_title="Singularity Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Tutto il nostro codice HTML, CSS e JavaScript racchiuso in una stringa Python
# NOTA: Qui dentro possiamo usare liberamente regole CSS come "height: 100vh;" 
# senza che Python si arrabbi, perché per lui è solo testo.
codice_dashboard = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Singularity</title>
    <!-- Importa Plotly.js -->
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        :root {
            --bg-dark: #16181d;
            --bg-panel: #1e2129;
            --text-light: #e0e0e0;
            --accent-blue: #3b82f6;
        }
        
        body {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-light);
            display: flex;
            height: 100vh; /* Ora non darà più errore in Streamlit */
            overflow: hidden; /* Nasconde le scrollbar se non necessarie */
        }

        /* --- SIDEBAR & EDU MODE FIX --- */
        .sidebar {
            width: 250px;
            background-color: var(--bg-panel);
            padding: 20px;
            box-sizing: border-box;
            border-right: 1px solid #2d313a;
        }

        .brand {
            font-size: 1.2rem;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 40px;
        }

        .controls-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 15px;
        }

        .lang-selector select {
            background-color: var(--bg-dark);
            color: white;
            border: 1px solid #333;
            padding: 8px;
            border-radius: 4px;
            width: 80px;
        }

        .edu-mode-container {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* IL FIX PER EDU MODE (non va a capo) */
        .edu-mode-label {
            white-space: nowrap; 
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .toggle-switch {
            width: 34px;
            height: 18px;
            background-color: #ff4757;
            border-radius: 10px;
            position: relative;
        }
        .toggle-switch::after {
            content: '';
            position: absolute;
            width: 14px;
            height: 14px;
            background-color: white;
            border-radius: 50%;
            top: 2px;
            right: 2px;
        }

        /* --- AREA GRAFICI --- */
        .main-content {
            flex-grow: 1;
            padding: 20px;
            display: flex;
            gap: 20px;
            box-sizing: border-box;
        }

        .chart-container {
            flex: 1;
            background-color: var(--bg-panel);
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
        }

        .chart-title {
            font-size: 1.1rem;
            color: #60a5fa;
            margin-bottom: 10px;
            border-bottom: 1px dashed #60a5fa;
            padding-bottom: 5px;
            display: inline-block;
        }

        .plot-area {
            flex-grow: 1;
            width: 100%;
        }
    </style>
</head>
<body>

    <!-- SIDEBAR -->
    <div class="sidebar">
        <div class="brand">
            <span style="color: #60a5fa;">❖</span> SINGULARITY
        </div>
        <div style="margin-bottom: 10px; font-size: 0.9rem;">🌐 Lang</div>
        <div class="controls-row">
            <div class="lang-selector">
                <select><option>IT</option></select>
            </div>
            
            <!-- EDU MODE CONTAINER CON FIX -->
            <div class="edu-mode-container">
                <div class="toggle-switch"></div>
                <div class="edu-mode-label">
                    🎓 Edu Mode <span>❓</span>
                </div>
            </div>
        </div>
    </div>

    <!-- MAIN DASHBOARD -->
    <div class="main-content">
        <!-- Grafico Eolico -->
        <div class="chart-container">
            <div class="chart-title">Wind Power Curve</div>
            <div id="windPlot" class="plot-area"></div>
        </div>
        
        <!-- Grafico Bacino Idrico -->
        <div class="chart-container">
            <div class="chart-title">Hydro Reservoir Topography</div>
            <div id="hydroPlot" class="plot-area"></div>
        </div>
    </div>

    <script>
        // Tema scuro comune per Plotly
        const layoutConfig = {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#e0e0e0' },
            margin: { t: 20, r: 20, b: 50, l: 60 }
        };

        /* ==========================================
           1. FIX GRAFICO EOLICO
           ========================================== */
        let windSpeeds = [];
        let powerOutput = [];
        const cutInSpeed = 3;
        const ratedSpeed = 12;
        const cutOutSpeed = 25;
        const ratedPower = 3000;

        for (let v = 0; v <= 30; v += 0.5) {
            windSpeeds.push(v);
            if (v < cutInSpeed) {
                powerOutput.push(0);
            } else if (v < ratedSpeed) {
                let power = ratedPower * Math.pow((v - cutInSpeed) / (ratedSpeed - cutInSpeed), 3);
                powerOutput.push(power);
            } else if (v <= cutOutSpeed) {
                powerOutput.push(ratedPower);
            } else {
                powerOutput.push(0);
            }
        }

        const windData = [{
            x: windSpeeds,
            y: powerOutput,
            type: 'scatter',
            mode: 'lines',
            line: { color: '#60a5fa', width: 2 },
            fill: 'tozeroy',
            fillcolor: 'rgba(96, 165, 250, 0.1)'
        }];

        const windLayout = {
            ...layoutConfig,
            xaxis: { title: 'Velocità Vento (m/s)', gridcolor: '#333' },
            yaxis: { title: 'Potenza Generata (MW)', gridcolor: '#333', range: [0, 4000] }
        };

        Plotly.newPlot('windPlot', windData, windLayout, {responsive: true});


        /* ==========================================
           2. FIX GRAFICO BACINO
           ========================================== */
        let zData = [];
        const gridSize = 30;
        const center = gridSize / 2;

        for (let y = 0; y < gridSize; y++) {
            let zRow = [];
            for (let x = 0; x < gridSize; x++) {
                let distanceX = Math.pow(x - center, 2);
                let distanceY = Math.pow(y - center, 2);
                
                let elevation = 400 + (0.8 * distanceX) + (1.2 * distanceY);
                
                if (elevation > 600) elevation = 600; 
                if (elevation < 420) elevation = 420; 
                
                zRow.push(elevation);
            }
            zData.push(zRow);
        }

        const hydroData = [{
            z: zData,
            type: 'surface',
            colorscale: 'Blues',
            reversescale: true,
            contours: {
                z: { show: true, usecolormap: true, highlightcolor: "#fff", project: { z: true } }
            }
        }];

        const hydroLayout = {
            ...layoutConfig,
            scene: {
                xaxis: { title: 'Latitudine (X)', gridcolor: '#444' },
                yaxis: { title: 'Longitudine (Y)', gridcolor: '#444' },
                zaxis: { title: 'Livello Acqua (m)', gridcolor: '#444', range: [400, 600] },
                camera: { eye: { x: 1.5, y: -1.5, z: 1.2 } }
            },
            margin: { t: 0, r: 0, b: 0, l: 0 }
        };

        Plotly.newPlot('hydroPlot', hydroData, hydroLayout, {responsive: true});
    </script>
</body>
</html>
"""

# 3. Carichiamo la stringa come componente web all'interno di Streamlit
# Un'altezza di 800-900px solitamente è perfetta per coprire la pagina.
components.html(codice_dashboard, height=850, scrolling=True)
