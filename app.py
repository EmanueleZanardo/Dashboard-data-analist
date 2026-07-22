import streamlit as st
import pandas as pd
import numpy as np
import time # Simula il ritardo del database reale

# Configurazione della pagina
st.set_page_config(page_title="Energy Trading Dashboard", layout="wide")
st.title("⚡ Energy Trading & Operations Dashboard")

# Creiamo due finestre separate: Simulatore e Dati Reali
tab_simulatore, tab_reale = st.tabs(["🎛️ Simulatore Strategico", "🌍 Dati Reali (Impianti Svizzeri)"])

# ==========================================
# FINESTRA 1: SIMULATORE
# ==========================================
with tab_simulatore:
    # Nota professionale
    st.info("📌 **Nota Operativa:** Il margine calcolato (Spread) rappresenta esclusivamente il margine di contribuzione operativo lordo. Tale valore **non** include i costi fissi aziendali quali: manutenzione ordinaria e straordinaria dell'impianto, stipendi dei tecnici e del personale, ammortamenti dei macchinari e rate dei prestiti bancari.")

    # Finestra di selezione centrale
    tipo_centrale = st.selectbox(
        "Seleziona la tipologia di centrale:", 
        ["Gas Naturale (CSS)", "Carbone (CDS)", "Idroelettrica", "Solare Fotovoltaico"]
    )

    st.sidebar.header("Parametri di Mercato")
    p_elec = st.sidebar.slider("Prezzo Energia Elettrica (€/MWh)", 0.0, 300.0, 100.0)

    # Variabili dinamiche
    margine = 0
    titolo_margine = ""

    # Logica condizionale in base alla centrale scelta
    if tipo_centrale == "Gas Naturale (CSS)":
        p_gas = st.sidebar.slider("Prezzo Gas Naturale (€/MWh)", 0.0, 150.0, 40.0)
        p_co2 = st.sidebar.slider("Prezzo CO2 (€/tCO2)", 0.0, 150.0, 80.0)
        efficienza = st.sidebar.slider("Efficienza Centrale (η)", 0.30, 0.65, 0.50)
        ef = 0.2
        
        costo_gas = p_gas / efficienza
        costo_co2 = (p_co2 * ef) / efficienza
        margine = p_elec - costo_gas - costo_co2
        titolo_margine = "Clean Spark Spread (CSS)"

        st.subheader("Modello Matematico")
        st.latex(r"CSS = P_{elec} - \frac{P_{gas}}{\eta} - \frac{P_{CO_2} \cdot E_f}{\eta}")
        st.caption("**Legenda:** $P_{elec}$ = Prezzo Elettricità | $P_{gas}$ = Prezzo Gas | $P_{CO_2}$ = Prezzo CO2 | $\eta$ = Efficienza termica | $E_f$ = Fattore emissione gas (0.2)")
        
        prezzi_range = np.linspace(50, 250, 50)
        margine_range = prezzi_range - costo_gas - costo_co2

    elif tipo_centrale == "Carbone (CDS)":
        p_carbone = st.sidebar.slider("Prezzo Carbone (€/MWh termico)", 0.0, 100.0, 20.0)
        p_co2 = st.sidebar.slider("Prezzo CO2 (€/tCO2)", 0.0, 150.0, 80.0)
        efficienza = st.sidebar.slider("Efficienza Centrale (η)", 0.30, 0.50, 0.40)
        ef = 0.34 # Il carbone emette più CO2 del gas
        
        costo_carb = p_carbone / efficienza
        costo_co2 = (p_co2 * ef) / efficienza
        margine = p_elec - costo_carb - costo_co2
        titolo_margine = "Clean Dark Spread (CDS)"

        st.subheader("Modello Matematico")
        st.latex(r"CDS = P_{elec} - \frac{P_{coal}}{\eta} - \frac{P_{CO_2} \cdot E_f}{\eta}")
        st.caption("**Legenda:** $P_{elec}$ = Prezzo Elettricità | $P_{coal}$ = Prezzo Carbone | $P_{CO_2}$ = Prezzo CO2 | $\eta$ = Efficienza termica | $E_f$ = Fattore emissione carbone (0.34)")
        
        prezzi_range = np.linspace(50, 250, 50)
        margine_range = prezzi_range - costo_carb - costo_co2

    elif tipo_centrale in ["Idroelettrica", "Solare Fotovoltaico"]:
        st.sidebar.markdown(f"Le centrali di tipo {tipo_centrale} non sostengono costi per il combustibile o per i permessi di emissione CO2. I costi variabili sono marginali.")
        margine = p_elec
        titolo_margine = "Margine Operativo (Rinnovabili)"

        st.subheader("Modello Matematico")
        st.latex(r"Margine = P_{elec} - O\&M_{var}")
        st.caption("**Legenda:** $P_{elec}$ = Prezzo Elettricità | $O\&M_{var}$ = Costi variabili di esercizio (Assunti $\\approx 0$)")
        
        prezzi_range = np.linspace(50, 250, 50)
        margine_range = prezzi_range # Correlazione diretta 1:1

    # Riduzione grafica (1/3 di larghezza)
    col_vuota_1, col_grafico, col_vuota_2 = st.columns([1, 1, 1]) 
    with col_grafico:
        df_grafico = pd.DataFrame({'Prezzo Elettricità': prezzi_range, 'Margine': margine_range}).set_index('Prezzo Elettricità')
        st.line_chart(df_grafico, height=250)
    
    st.markdown("---")

    # Azioni Consigliate
    st.subheader(f"📊 Strategia Operativa: {titolo_margine} a € {margine:.2f}")
    
    if margine > 0:
        st.success("Stato: IN THE MONEY (Profitto)")
        st.markdown("""
        **Azioni Consigliate:**
        * **Impianto Fisico:** **ACCENDI** la centrale (dispatching).
        * **Mercati (se in ottica Future/Hedging):**
          * **VENDI** contratti future per l'energia elettrica (per bloccare il ricavo alto).
        """ + ("" if tipo_centrale in ["Idroelettrica", "Solare Fotovoltaico"] else """
          * **COMPRA** contratti future per il gas naturale/carbone (per bloccare il costo del combustibile).
          * **COMPRA** certificati di CO2 (per coprire le emissioni).
        """))
    else:
        st.error("Stato: OUT OF THE MONEY (Perdita)")
        st.markdown("""
        **Azioni Consigliate:**
        * **Impianto Fisico:** **SPEGNI** la centrale (conviene acquistare energia sul mercato piuttosto che produrla).
        * **Mercati (se in ottica Future/Hedging):**
          * **COMPRA** contratti future per l'energia elettrica per soddisfare i tuoi clienti.
        """ + ("" if tipo_centrale in ["Idroelettrica", "Solare Fotovoltaico"] else """
          * **VENDI** contratti future per il gas/carbone (liquida le posizioni se non brucerai combustibile).
          * **VENDI** certificati di CO2.
        """))

# ==========================================
# FINESTRA 2: DATI REALI IMPIANTI SVIZZERI
# ==========================================
with tab_reale:
    st.header("Monitoraggio Impianti Svizzeri (Dati Proxy Reali)")
    st.markdown("Questa dashboard interroga i prezzi Spot dell'elettricità (Mercato Svizzero - Swissix) ed elabora le metriche finanziarie per tre asset strategici specifici.")
    
    if st.button("🔄 Aggiorna Dati da API ENTSO-E (Simulazione)"):
        with st.spinner("Connessione al database in corso... fetch prezzi Spot Svizzera..."):
            time.sleep(1.5) # Simula l'attesa di una vera API
            
            # Qui andrebbe inserita la libreria 'requests' per chiamare ENTSO-E. 
            # Generiamo prezzi plausibili proxy per il mercato attuale:
            prezzo_spot_ch = np.random.uniform(60.0, 110.0)
            prezzo_gas_eu = np.random.uniform(30.0, 45.0)
            prezzo_co2_eu = np.random.uniform(60.0, 75.0)
            
            # 1. Termovalorizzatore IRCD Giubiasco (Ciclo Termico)
            # Nota: I termovalorizzatori percepiscono anche la "gate fee" per i rifiuti, ma qui analizziamo il lato power.
            eff_ircd = 0.25 # Efficienza elettrica tipica termovalorizzatori
            margine_ircd = prezzo_spot_ch - (prezzo_gas_eu / eff_ircd) - (prezzo_co2_eu * 0.2 / eff_ircd) # Usando proxy gas
            
            # 2. Idroelettrica: Centrale di Biasca
            # Costi O&M stimati a ~5 CHF/MWh per usura Pelton.
            margine_biasca = prezzo_spot_ch - 5.0
            
            # 3. Solare: Diga del Muttsee (AlpinSolar)
            # Essendo a 2500m, produce molto in inverno con costi variabili quasi nulli.
            margine_muttsee = prezzo_spot_ch
            
            col1, col2, col3 = st.columns(3)
            
            col1.metric(
                label="🏭 IRCD Giubiasco (Termovalorizzatore)", 
                value=f"€ {margine_ircd:.2f} / MWh", 
                delta="Proxy Margin (Power)", delta_color="off"
            )
            col2.metric(
                label="💧 Centrale di Biasca (Idro)", 
                value=f"€ {margine_biasca:.2f} / MWh", 
                delta="Margine Netto O&M", delta_color="normal"
            )
            col3.metric(
                label="☀️ Diga del Muttsee (Fotovoltaico)", 
                value=f"€ {margine_muttsee:.2f} / MWh", 
                delta="Margine Lordo", delta_color="normal"
            )
            
            st.caption(f"Dati di mercato di riferimento utilizzati: Spot CH €{prezzo_spot_ch:.2f} | Gas proxy €{prezzo_gas_eu:.2f} | CO2 €{prezzo_co2_eu:.2f}")
    else:
        st.info("Clicca il pulsante in alto per scaricare i dati di mercato aggiornati.")
