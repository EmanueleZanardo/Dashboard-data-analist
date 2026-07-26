import streamlit as st
import plotly.graph_objects as go
import math

# 1. Configurazione della pagina (layout largo per i grafici)
st.set_page_config(layout="wide", page_title="Singularity Dashboard")

# 2. Iniezione CSS minimo (solo per personalizzare i colori di base, senza intaccare i widget)
st.markdown("""
    <style>
        .css-1d391kg { background-color: #1e2129; } /* Colore sidebar */
        .stApp { background-color: #16181d; color: #e0e0e0; } /* Colore sfondo principale */
    </style>
""", unsafe_allow_html=True)

# 3. --- SIDEBAR (Costruita con elementi nativi di Streamlit) ---
with st.sidebar:
    st.markdown("### <span style='color: #60a5fa;'>❖</span> SINGULARITY", unsafe_allow_html=True)
    st.markdown("---")
    
    # Usiamo le colonne per allineare il selettore lingua e il toggle Edu Mode
    col_lang, col_edu = st.columns([1, 1.5])
    
    with col_lang:
        lang = st.selectbox("🌐 Lang", ["IT", "EN", "ES"])
        
    with col_edu:
        # Spaziatura per allineare verticalmente il toggle alla selectbox
        st.write("")
        st.write("")
        # Il toggle nativo non va a capo in modo anomalo
        edu_mode = st.toggle("🎓 Edu Mode ❓")

# 4. --- CALCOLO MATEMATICO DEI DATI (Tradotto da JS a Python) ---

# --- Dati Eolico ---
wind_speeds = [v * 0.5 for v in range(61)]  # Genera valori da 0.0 a 30.0 (step 0.5)
power_output = []
cut_in_speed = 3
rated_speed = 12
cut_out_speed = 25
rated_power = 3000

for v in wind_speeds:
    if v < cut_in_speed:
        power_output.append(0)
    elif v < rated_speed:
        power = rated_power * math.pow((v - cut_in_speed) / (rated_speed - cut_in_speed), 3)
        power_output.append(power)
    elif v <= cut_out_speed:
        power_output.append(rated_power)
    else:
        power_output.append(0)

# --- Dati Topografia Bacino Idrico ---
grid_size = 30
center = grid_size / 2
z_data = []

for y in range(grid_size):
    z_row = []
    for x in range(grid_size):
        distance_x = math.pow(x - center, 2)
        distance_y = math.pow(y - center, 2)
        elevation = 400 + (0.8 * distance_x) + (1.2 * distance_y)
        
        # Limiti di altezza/profondità
        if elevation > 600: elevation = 600
        if elevation < 420: elevation = 420
        
        z_row.append(elevation)
    z_data.append(z_row)


# 5. --- CREAZIONE GRAFICI CON PLOTLY GRAPH OBJECTS ---

layout_config = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e0e0e0'),
    margin=dict(t=40, r=20, b=40, l=40)
)

# Grafico Eolico (2D)
fig_wind = go.Figure()
fig_wind.add_trace(go.Scatter(
    x=wind_speeds, 
    y=power_output, 
    mode='lines',
    line=dict(color='#60a5fa', width=2),
    fill='tozeroy', 
    fillcolor='rgba(96, 165, 250, 0.1)'
))
fig_wind.update_layout(
    **layout_config,
    title=dict(text="Wind Power Curve", font=dict(color='#60a5fa', size=20)),
    xaxis=dict(title='Velocità Vento (m/s)', gridcolor='#333'),
    yaxis=dict(title='Potenza Generata (MW)', gridcolor='#333', range=[0, 4000])
)

# Grafico Topografico (3D)
fig_hydro = go.Figure(data=[go.Surface(
    z=z_data, 
    colorscale='Blues', 
    reversescale=True,
    contours=dict(z=dict(show=True, usecolormap=True, highlightcolor="#fff", project=dict(z=True)))
)])
fig_hydro.update_layout(
    **layout_config,
    title=dict(text="Hydro Reservoir Topography", font=dict(color='#60a5fa', size=20)),
    scene=dict(
        xaxis=dict(title='Latitudine (X)', gridcolor='#444'),
        yaxis=dict(title='Longitudine (Y)', gridcolor='#444'),
        zaxis=dict(title='Livello Acqua (m)', gridcolor='#444', range=[400, 600]),
        camera=dict(eye=dict(x=1.5, y=-1.5, z=1.2))
    )
)

# 6. --- RENDERIZZAZIONE SULLA DASHBOARD ---
# Creiamo due colonne principali per affiancare i grafici
col1, col2 = st.columns(2)

with col1:
    # use_container_width=True rende il grafico responsive e lo adatta alla colonna
    st.plotly_chart(fig_wind, use_container_width=True)

with col2:
    st.plotly_chart(fig_hydro, use_container_width=True)
    
# Qui sotto potrai continuare ad aggiungere altre funzioni Streamlit nativamente...
# st.dataframe(...)
# st.button(...)
