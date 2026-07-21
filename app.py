import streamlit as st
import pandas as pd
import numpy as np

# Configurazione della pagina
st.set_page_config(page_title="Energy Trading Dashboard", layout="wide")

st.title("⚡ Simulatore Clean Spark Spread (CSS)")
st.markdown("Questa dashboard calcola il margine di profitto teorico di una centrale a gas.")

# Sidebar per gli input interattivi
st.sidebar.header("Parametri di Mercato")
p_elec = st.sidebar.slider("Prezzo Energia Elettrica (€/MWh)", 0.0, 300.0, 100.0)
p_gas = st.sidebar.slider("Prezzo Gas Naturale (€/MWh)", 0.0, 150.0, 40.0)
p_co2 = st.sidebar.slider("Prezzo CO2 (€/tCO2)", 0.0, 150.0, 80.0)

st.sidebar.header("Parametri Centrale")
efficienza = st.sidebar.slider("Efficienza Centrale (η)", 0.30, 0.65, 0.50)
fattore_emissione = 0.2  # tCO2/MWh termico costante per il gas

# Calcolo del Clean Spark Spread
costo_gas = p_gas / efficienza
costo_co2 = (p_co2 * fattore_emissione) / efficienza
css = p_elec - costo_gas - costo_co2

# Visualizzazione dei risultati
st.subheader("Risultati in Tempo Reale")

col1, col2, col3 = st.columns(3)
col1.metric("Costo Generazione (Gas)", f"€ {costo_gas:.2f}")
col2.metric("Costo Emissioni (CO2)", f"€ {costo_co2:.2f}")

# Colora il CSS di verde se in profitto, rosso se in perdita
if css > 0:
    col3.metric("Clean Spark Spread (Margine)", f"€ {css:.2f}")
    st.success("✅ La centrale sta generando un profitto (In the money).")
else:
    col3.metric("Clean Spark Spread (Margine)", f"€ {css:.2f}")
    st.error("❌ La centrale è in perdita (Out of the money).")

# Simulazione su un range di prezzi dell'energia (Grafico)
st.subheader("Analisi di Sensibilità")
prezzi_energia_range = np.linspace(50, 200, 100)
css_range = prezzi_energia_range - costo_gas - costo_co2

df_grafico = pd.DataFrame({
    'Prezzo Energia (€/MWh)': prezzi_energia_range,
    'CSS (€/MWh)': css_range
})

st.line_chart(df_grafico.set_index('Prezzo Energia (€/MWh)'))
