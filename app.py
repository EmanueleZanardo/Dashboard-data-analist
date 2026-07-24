import streamlit as st
import pandas as pd
import numpy as np

# Configurazione della pagina
st.set_page_config(page_title="Energy Trading Dashboard", layout="wide")
st.title("⚡ Energy Trading & Operations Dashboard")

# Creiamo due finestre separate: Simulatore e Dati Reali
tab_simulatore, tab_reale = st.tabs(["🎛️ Simulatore Strategico", "🌍 Dati Reali (Impianti Svizzeri)"])

# ==========================================
# FINESTRA 1: SIMULATORE
# ==========================================
with tab_simulatore:
    # Nota professionale (Costi Fissi vs Variabili)
    st.info("📌 **Nota Operativa:** Il margine calcolato (Spread) rappresenta esclusivamente il margine di contribuzione operativo lordo. Tale valore **non** include i costi fissi aziendali quali:\n"
            "* Manutenzione ordinaria e straordinaria dell'impianto.\n"
            "* Stipendi dei tecnici e del personale.\n"
            "* Ammortamenti dei macchinari e rate dei prestiti bancari.")

    # Finestra di selezione centrale
    tipo_centrale = st.selectbox(
        "Seleziona la tipologia di centrale:", 
        ["Gas Naturale (CSS)", "Carbone (CDS)", "Idroelettrica (Biasca)", "Solare Fotovoltaico (Muttsee)"]
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
        ef = 0.34
        
        costo_carb = p_carbone / efficienza
        costo_co2 = (p_co2 * ef) / efficienza
        margine = p_elec - costo_carb - costo_co2
        titolo_margine = "Clean Dark Spread (CDS)"

        st.subheader("Modello Matematico")
        st.latex(r"CDS = P_{elec} - \frac{P_{coal}}{\eta} - \frac{P_{CO_2} \cdot E_f}{\eta}")
        st.caption("**Legenda:** $P_{elec}$ = Prezzo Elettricità | $P_{coal}$ = Prezzo Carbone | $P_{CO_2}$ = Prezzo CO2 | $\eta$ = Efficienza termica | $E_f$ = Fattore emissione carbone (0.34)")
        
        prezzi_range = np.linspace(50, 250, 50)
        margine_range = prezzi_range - costo_carb - costo_co2

    elif tipo_centrale == "Idroelettrica (Biasca)":
        costo_om = st.sidebar.slider("Costi O&M Variabili (€/MWh)", 0.0, 20.0, 5.0)
        margine = p_elec - costo_om
        titolo_margine = "Margine Operativo Idroelettrico"

        st.subheader("Modello Matematico")
        st.latex(r"Margine = P_{elec} - O\&M_{var}")
        st.caption("**Legenda:** $P_{elec}$ = Prezzo Elettricità | $O\&M_{var}$ = Costi operativi e di manutenzione variabili legati all'usura (es. turbine Pelton)")
        
        prezzi_range = np.linspace(50, 250, 50)
        margine_range = prezzi_range - costo_om

    elif tipo_centrale == "Solare Fotovoltaico (Muttsee)":
        st.sidebar.markdown("Le centrali solari non sostengono costi per il combustibile o permessi CO2. I costi variabili sono assunti pari a zero.")
        margine = p_elec
        titolo_margine = "Margine Lordo Fotovoltaico"

        st.subheader("Modello Matematico")
        st.latex(r"Margine = P_{elec}")
        st.caption("**Legenda:** $P_{elec}$ = Prezzo Elettricità (Correlazione 1:1)")
        
        prezzi_range = np.linspace(50, 250, 50)
        margine_range = prezzi_range 

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
        st.markdown("**Azioni Consigliate:**")
        st.markdown("* **Impianto Fisico:** **ACCENDI** la centrale (dispatching).")
        st.markdown("* **Mercati Future/Hedging (se applicabile):**")
        st.markdown("  * **VENDI** contratti future per l'energia elettrica (blocchi il ricavo).")
        if tipo_centrale in ["Gas Naturale (CSS)", "Carbone (CDS)"]:
            st.markdown(f"  * **COMPRA** contratti future per il {'gas naturale' if tipo_centrale == 'Gas Naturale (CSS)' else 'carbone'} (blocchi il costo del combustibile).")
            st.markdown("  * **COMPRA** certificati di CO2 (copri le emissioni).")
    else:
        st.error("Stato: OUT OF THE MONEY (Perdita)")
        st.markdown("**Azioni Consigliate:**")
        st.markdown("* **Impianto Fisico:** **SPEGNI** la centrale (conviene acquistare energia sul mercato piuttosto che produrla in perdita).")
        st.markdown("* **Mercati Future/Hedging (se applicabile):**")
        st.markdown("  * **COMPRA** contratti future per l'energia elettrica per soddisfare i tuoi clienti.")
        if tipo_centrale in ["Gas Naturale (CSS)", "Carbone (CDS)"]:
            st.markdown(f"  * **VENDI** contratti future per il {'gas' if tipo_centrale == 'Gas Naturale (CSS)' else 'carbone'} (liquida le posizioni se non brucerai combustibile).")
            st.markdown("  * **VENDI** certificati di CO2.")

# ==========================================
# FINESTRA 2: DATI REALI IMPIANTI SVIZZERI (API ENTSO-E)
# ==========================================
with tab_reale:
    st.header("Monitoraggio Impianti Svizzeri (Dati Reali ENTSO-E)")
    st.markdown("Questa dashboard interroga l'API ufficiale ENTSO-E per il mercato Day-Ahead Svizzero (Swissix) in tempo reale.")
    
    if st.button("🔄 Scarica Prezzi Reali Mercato CH"):
        try:
            with st.spinner("Connessione a ENTSO-E Transparency Platform in corso..."):
                from entsoe import EntsoePandasClient
                
                # CHIAVE API INSERITA QUI
                api_key = "69b86d28-17c2-4e13-a587-1598048a6675"
                client = EntsoePandasClient(api_key=api_key)
                
                # Imposta l'intervallo temporale (ultime 24 ore)
                inizio = pd.Timestamp.now(tz='Europe/Zurich').floor('h') - pd.Timedelta(hours=24)
                fine = pd.Timestamp.now(tz='Europe/Zurich').floor('h')
                
                # Interroga i prezzi Day-Ahead per la Svizzera ('CH')
                prezzi_ch = client.query_day_ahead_prices('CH', start=inizio, end=fine)
                
                # Estrae l'ultimo prezzo disponibile
                prezzo_spot_ch = prezzi_ch.iloc[-1]
                
                # Mostra un grafico dell'andamento reale
                st.subheader("Andamento Prezzo Spot Svizzera (Ultime 24h)")
                st.line_chart(prezzi_ch, height=200)
                
                # --- CALCOLO DEI MARGINI ---
                prezzo_gas_eu = 38.5  # Proxy realistico attuale €/MWh
                prezzo_co2_eu = 68.0  # Proxy realistico attuale €/tCO2
                
                # 1. Termovalorizzatore IRCD Giubiasco 
                eff_ircd = 0.25 
                margine_ircd = prezzo_spot_ch - (prezzo_gas_eu / eff_ircd) - (prezzo_co2_eu * 0.2 / eff_ircd) 
                
                # 2. Idroelettrica: Centrale di Biasca
                margine_biasca = prezzo_spot_ch - 5.0 # Costo O&M stimato
                
                # 3. Solare: Diga del Muttsee 
                margine_muttsee = prezzo_spot_ch
                
                st.markdown("---")
                st.subheader("Margini Operativi Istantanei (su Prezzo Reale)")
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
                
                st.caption(f"Ultimo prezzo Spot CH rilevato da ENTSO-E: **€ {prezzo_spot_ch:.2f} / MWh** | Proxy Gas: €{prezzo_gas_eu} | Proxy CO2: €{prezzo_co2_eu}")

        except Exception as e:
            st.error(f"Si è verificato un errore durante il recupero dei dati da ENTSO-E: {e}")
