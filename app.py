import streamlit as st
import pandas as pd
import numpy as np
import datetime

# --- FUNZIONE DI DOWNLOAD CON CACHE ---
# Questa funzione scarica i dati e li salva in memoria per 1 ora (3600 sec)
# Così se scarichi 6 mesi di dati, non devi aspettare ogni volta che clicchi un bottone.
@st.cache_data(ttl=3600, show_spinner=False)
def scarica_dati_entsoe(api_key, start_date, end_date):
    from entsoe import EntsoePandasClient
    client = EntsoePandasClient(api_key=api_key)
    
    # Adattiamo le date selezionate dalla console al formato richiesto dall'API
    inizio_tz = pd.Timestamp(start_date, tz='Europe/Zurich')
    # Impostiamo la fine all'ultima ora del giorno selezionato
    fine_tz = pd.Timestamp(end_date, tz='Europe/Zurich') + pd.Timedelta(days=1) - pd.Timedelta(hours=1)
    
    prezzi = client.query_day_ahead_prices('CH', start=inizio_tz, end=fine_tz)
    
    # ECCO LA CORREZIONE DELLO "0": Diamo un nome alla colonna e all'asse del tempo
    prezzi.name = "Prezzo Spot (€/MWh)"
    prezzi.index.name = "Data e Ora"
    
    return prezzi

# Configurazione della pagina
st.set_page_config(page_title="Energy Trading Dashboard", layout="wide")
st.title("⚡ Energy Trading & Operations Dashboard")

# Creiamo due finestre separate: Simulatore e Dati Reali
tab_simulatore, tab_reale = st.tabs(["🎛️ Simulatore Strategico", "🌍 Dati Reali (Impianti Svizzeri)"])

# ==========================================
# FINESTRA 1: SIMULATORE
# ==========================================
with tab_simulatore:
    st.info("📌 **Nota Operativa:** Il margine calcolato (Spread) rappresenta esclusivamente il margine di contribuzione operativo lordo. Tale valore **non** include i costi fissi aziendali quali:\n"
            "* Manutenzione ordinaria e straordinaria dell'impianto.\n"
            "* Stipendi dei tecnici e del personale.\n"
            "* Ammortamenti dei macchinari e rate dei prestiti bancari.")

    tipo_centrale = st.selectbox(
        "Seleziona la tipologia di centrale:", 
        ["Gas Naturale (CSS)", "Carbone (CDS)", "Idroelettrica (Biasca)", "Solare Fotovoltaico (Muttsee)"]
    )

    st.sidebar.header("Parametri di Mercato")
    p_elec = st.sidebar.slider("Prezzo Energia Elettrica (€/MWh)", 0.0, 300.0, 100.0)

    margine = 0
    titolo_margine = ""

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
        st.caption("**Legenda:** $P_{elec}$ = Prezzo Elettricità | $O\&M_{var}$ = Costi operativi e manutenzione (es. usura turbine)")
        
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

    col_vuota_1, col_grafico, col_vuota_2 = st.columns([1, 1, 1]) 
    with col_grafico:
        df_grafico = pd.DataFrame({'Prezzo Elettricità': prezzi_range, 'Margine': margine_range}).set_index('Prezzo Elettricità')
        st.line_chart(df_grafico, height=250)
    
    st.markdown("---")

    st.subheader(f"📊 Strategia Operativa: {titolo_margine} a € {margine:.2f}")
    
    if margine > 0:
        st.success("Stato: IN THE MONEY (Profitto)")
        st.markdown("**Azioni Consigliate:**\n"
                    "* **Impianto Fisico:** **ACCENDI** la centrale (dispatching).\n"
                    "* **Mercati Future/Hedging:**\n"
                    "  * **VENDI** contratti future per l'energia elettrica (blocchi il ricavo).")
        if tipo_centrale in ["Gas Naturale (CSS)", "Carbone (CDS)"]:
            st.markdown(f"  * **COMPRA** contratti future per il {'gas naturale' if tipo_centrale == 'Gas Naturale (CSS)' else 'carbone'}.")
            st.markdown("  * **COMPRA** certificati di CO2.")
    else:
        st.error("Stato: OUT OF THE MONEY (Perdita)")
        st.markdown("**Azioni Consigliate:**\n"
                    "* **Impianto Fisico:** **SPEGNI** la centrale (conviene acquistare energia sul mercato piuttosto che produrla in perdita).\n"
                    "* **Mercati Future/Hedging:**\n"
                    "  * **COMPRA** contratti future per l'energia elettrica per soddisfare i tuoi clienti.")
        if tipo_centrale in ["Gas Naturale (CSS)", "Carbone (CDS)"]:
            st.markdown(f"  * **VENDI** contratti future per il {'gas' if tipo_centrale == 'Gas Naturale (CSS)' else 'carbone'}.")
            st.markdown("  * **VENDI** certificati di CO2.")


# ==========================================
# FINESTRA 2: DATI REALI IMPIANTI SVIZZERI (API ENTSO-E) CON CONSOLE
# ==========================================
with tab_reale:
    st.header("Monitoraggio Impianti Svizzeri (Dati Reali ENTSO-E)")
    st.markdown("Questa dashboard interroga l'API ufficiale ENTSO-E per il mercato Day-Ahead Svizzero (Swissix).")
    
    # --- CONSOLE TIMEFRAME ---
    st.subheader("⚙️ Console Timeframe")
    
    # Logica per il tasto Reset tramite st.session_state
    oggi = datetime.date.today()
    default_inizio = oggi - datetime.timedelta(days=7) # Default a 7 giorni

    if 'data_inizio' not in st.session_state:
        st.session_state.data_inizio = default_inizio
    if 'data_fine' not in st.session_state:
        st.session_state.data_fine = oggi

    def resetta_date():
        st.session_state.data_inizio = default_inizio
        st.session_state.data_fine = oggi

    # Creazione della barra degli strumenti in 3 colonne
    col_inizio, col_fine, col_btn = st.columns([2, 2, 1])
    with col_inizio:
        data_inizio_selezionata = st.date_input("Data Inizio", value=st.session_state.data_inizio, key='data_inizio')
    with col_fine:
        data_fine_selezionata = st.date_input("Data Fine", value=st.session_state.data_fine, key='data_fine')
    with col_btn:
        st.write("") # Spazio per allineare verticalmente il bottone ai calendari
        st.write("")
        st.button("🔄 Reset (Ultimi 7 gg)", on_click=resetta_date)

    st.markdown("---")
    
    # --- SCARICAMENTO DATI ---
    if st.button("🚀 Scarica/Aggiorna Dati Mercato CH"):
        try:
            with st.spinner("Connessione a ENTSO-E in corso (potrebbe richiedere qualche secondo per periodi lunghi)..."):
                
                # CHIAVE API INSERITA QUI
                api_key = "69b86d28-17c2-4e13-a587-1598048a6675"
                
                # Richiamo la funzione "veloce" con la Cache
                prezzi_ch = scarica_dati_entsoe(api_key, data_inizio_selezionata, data_fine_selezionata)
                
                # Estrae l'ultimo prezzo disponibile
                prezzo_spot_ch = prezzi_ch.iloc[-1]
                data_ultimo_prezzo = prezzi_ch.index[-1].strftime('%d/%m/%Y %H:%00')
                
                # Mostra un grafico dell'andamento reale
                st.subheader(f"Andamento Prezzo Spot Svizzera (Dal {data_inizio_selezionata.strftime('%d/%m/%Y')} al {data_fine_selezionata.strftime('%d/%m/%Y')})")
                st.line_chart(prezzi_ch, height=350)
                
                # --- CALCOLO DEI MARGINI ---
                prezzo_gas_eu = 38.5  # Proxy
                prezzo_co2_eu = 68.0  # Proxy
                
                # 1. Termovalorizzatore IRCD Giubiasco 
                eff_ircd = 0.25 
                margine_ircd = prezzo_spot_ch - (prezzo_gas_eu / eff_ircd) - (prezzo_co2_eu * 0.2 / eff_ircd) 
                
                # 2. Idroelettrica: Centrale di Biasca
                margine_biasca = prezzo_spot_ch - 5.0 # Costo O&M stimato
                
                # 3. Solare: Diga del Muttsee 
                margine_muttsee = prezzo_spot_ch
                
                st.markdown("---")
                st.subheader("Margini Operativi Istantanei (Sull'ultimo prezzo rilevato)")
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
                
                st.caption(f"Ultimo prezzo Spot CH rilevato da ENTSO-E: **€ {prezzo_spot_ch:.2f} / MWh** (del {data_ultimo_prezzo}) | Proxy Gas: €{prezzo_gas_eu} | Proxy CO2: €{prezzo_co2_eu}")

        except Exception as e:
            st.error(f"Si è verificato un errore durante il recupero dei dati da ENTSO-E: {e}")
