import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import norm, skew, kurtosis
from plotly.subplots import make_subplots

# ==========================================
# 1. SETUP TERMINALE & AUTENTICAZIONE
# ==========================================
st.set_page_config(page_title="Singularity Quant ETRM", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #030712; color: #F3F4F6; }
    h1, h2, h3 { font-family: 'JetBrains Mono', monospace; color: #60A5FA; }
    .metric-container { background: #111827; border: 1px solid #1F2937; border-top: 3px solid #3B82F6; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.5); }
    .metric-label { font-size: 11px; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;}
    .metric-val { font-size: 22px; color: #F9FAFB; font-family: 'JetBrains Mono', monospace; font-weight: bold; margin-top: 5px;}
    .chat-msg { background: #1F2937; padding: 10px; border-radius: 8px; margin-bottom: 10px; font-family: 'JetBrains Mono', monospace; font-size: 12px; border-left: 3px solid #10B981;}
    .stButton>button { width: 100%; font-family: 'JetBrains Mono', monospace; font-weight: bold; background: #1D4ED8; color: white; border: none; }
    .stButton>button:hover { background: #2563EB; }
    </style>
""", unsafe_allow_html=True)

# Auth Mock (Basta scrivere 'admin' come avevi impostato)
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<h2 style='text-align: center; color: #3B82F6;'>💠 SINGULARITY OS</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Identificazione Biometrica / Hardware Key Richiesta</p>", unsafe_allow_html=True)
        pwd = st.text_input("Inserisci Chiave Crittografica", type="password")
        if st.button("Decripta Terminale"):
            if pwd == "admin": 
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Accesso Negato.")
    st.stop()

# ==========================================
# 2. CORE DATA ENGINE & VECCHIA FUNZIONE ENTSO-E
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def scarica_dati_entsoe(api_key, start_date, end_date):
    from entsoe import EntsoePandasClient
    client = EntsoePandasClient(api_key=api_key)
    
    inizio_tz = pd.Timestamp(start_date, tz='Europe/Zurich')
    fine_tz = pd.Timestamp(end_date, tz='Europe/Zurich') + pd.Timedelta(days=1) - pd.Timedelta(hours=1)
    
    prezzi = client.query_day_ahead_prices('CH', start=inizio_tz, end=fine_tz)
    
    prezzi.name = "Prezzo Spot (€/MWh)"
    prezzi.index.name = "Data e Ora"
    
    return prezzi

@st.cache_data(ttl=1800, show_spinner=False)
def generate_singularity_data():
    np.random.seed(42)
    days = 500
    dates = pd.date_range(end=datetime.date.today(), periods=days)
    base_drift = 0.0001
    prices = np.zeros(days); prices[0] = 50
    vol = np.zeros(days); vol[0] = 0.02
    for i in range(1, days):
        vol[i] = 0.02 + 0.8 * vol[i-1] + np.random.exponential(0.005) if np.random.rand() > 0.9 else 0.02 + 0.95 * vol[i-1]
        prices[i] = prices[i-1] * np.exp((base_drift - 0.5*vol[i]**2) + vol[i]*np.random.normal())
    df = pd.DataFrame({'Power_EUR': prices}, index=dates)
    df['Returns'] = df['Power_EUR'].pct_change().fillna(0)
    df['Gas_USD'] = 15 + df['Power_EUR']*0.15 + np.random.normal(0,1,days)
    df['EUR_USD'] = 1.05 + np.cumsum(np.random.normal(0, 0.001, days))
    df['CO2_EUA'] = 80 + np.cumsum(np.random.normal(0.02, 0.5, days))
    df['Sentiment_NLP'] = np.clip(np.random.normal(0.1, 0.4, days), -1, 1)
    return df

df = generate_singularity_data()
ult = df.iloc[-1]

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistema Quantitativo Operativo. Come posso assisterti nell'ottimizzazione del portafoglio oggi?"}]

# ==========================================
# 3. SIDEBAR WORKSPACES AGGIORNATA
# ==========================================
with st.sidebar:
    st.markdown("<h2>💠 SINGULARITY</h2>", unsafe_allow_html=True)
    st.markdown("*Quantitative Global Macro System*")
    st.markdown("---")
    
    workspace = st.radio("🏢 WORKSPACES", [
        "🎛️ Simulatore Strategico (Classico)",
        "🌍 Dati Reali Svizzeri (ENTSO-E)",
        "🤖 Autonomous AI & MARL",
        "🌍 Climate & Grid Intel",
        "📈 Exotics & Structuring",
        "🏛️ Enterprise Risk & XVA"
    ])
    
#    st.markdown("---")
#    st.markdown("### 💬 Copilot Quant LLM")
#    for msg in st.session_state.messages:
#        st.markdown(f"<div class='chat-msg'><b>{msg['role'].upper()}:</b> {msg['content']}</div>", unsafe_allow_html=True)
    
    if prompt := st.chat_input("Chiedi all'AI"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": f"Elaborazione di '{prompt}'. Il modello indica correlazione stabile."})
        st.rerun()

def render_kpi(title, value, col):
    col.markdown(f"<div class='metric-container'><div class='metric-label'>{title}</div><div class='metric-val'>{value}</div></div>", unsafe_allow_html=True)

# ==========================================
# WORKSPACE 1: SIMULATORE STRATEGICO (La tua vecchia Finestra 1)
# ==========================================
if workspace == "🎛️ Simulatore Strategico (Classico)":
    st.title("🎛️ Simulatore Strategico")
    st.info("📌 **Nota Operativa:** Il margine calcolato (Spread) rappresenta esclusivamente il margine di contribuzione operativo lordo. Tale valore **non** include i costi fissi aziendali quali:\n"
            "* Manutenzione ordinaria e straordinaria dell'impianto.\n"
            "* Stipendi dei tecnici e del personale.\n"
            "* Ammortamenti dei macchinari e rate dei prestiti bancari.")

    col_parametri, col_risultati = st.columns([1, 2.5])

    with col_parametri:
        st.subheader("⚙️ Parametri di Mercato")
        tipo_centrale = st.selectbox(
            "Seleziona la tipologia di centrale:", 
            ["Gas Naturale (CSS)", "Carbone (CDS)", "Idroelettrica (Biasca)", "Solare Fotovoltaico (Muttsee)"]
        )
        p_elec = st.slider("Prezzo Energia Elettrica (€/MWh)", 0.0, 300.0, 100.0)

        if tipo_centrale == "Gas Naturale (CSS)":
            p_gas = st.slider("Prezzo Gas Naturale (€/MWh)", 0.0, 150.0, 40.0)
            p_co2 = st.slider("Prezzo CO2 (€/tCO2)", 0.0, 150.0, 80.0)
            efficienza = st.slider("Efficienza Centrale (η)", 0.30, 0.65, 0.50)
        elif tipo_centrale == "Carbone (CDS)":
            p_carbone = st.slider("Prezzo Carbone (€/MWh termico)", 0.0, 100.0, 20.0)
            p_co2 = st.slider("Prezzo CO2 (€/tCO2)", 0.0, 150.0, 80.0)
            efficienza = st.slider("Efficienza Centrale (η)", 0.30, 0.50, 0.40)
        elif tipo_centrale == "Idroelettrica (Biasca)":
            costo_om = st.slider("Costi O&M Variabili (€/MWh)", 0.0, 20.0, 5.0)
        elif tipo_centrale == "Solare Fotovoltaico (Muttsee)":
            st.markdown("*I costi variabili sono assunti pari a zero. Nessun input richiesto.*")

    with col_risultati:
        margine = 0
        titolo_margine = ""
        if tipo_centrale == "Gas Naturale (CSS)":
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
            margine = p_elec - costo_om
            titolo_margine = "Margine Operativo Idroelettrico"
            st.subheader("Modello Matematico")
            st.latex(r"Margine = P_{elec} - O\&M_{var}")
            st.caption("**Legenda:** $P_{elec}$ = Prezzo Elettricità | $O\&M_{var}$ = Costi operativi e manutenzione (es. usura turbine)")
            prezzi_range = np.linspace(50, 250, 50)
            margine_range = prezzi_range - costo_om
        elif tipo_centrale == "Solare Fotovoltaico (Muttsee)":
            margine = p_elec
            titolo_margine = "Margine Lordo Fotovoltaico"
            st.subheader("Modello Matematico")
            st.latex(r"Margine = P_{elec}")
            st.caption("**Legenda:** $P_{elec}$ = Prezzo Elettricità (Correlazione 1:1)")
            prezzi_range = np.linspace(50, 250, 50)
            margine_range = prezzi_range 

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
# WORKSPACE 2: DATI REALI SVIZZERI (La tua vecchia Finestra 2)
# ==========================================
elif workspace == "🌍 Dati Reali Svizzeri (ENTSO-E)":
    st.header("Monitoraggio Impianti Svizzeri (Dati Reali ENTSO-E)")
    st.markdown("Questa dashboard interroga l'API ufficiale ENTSO-E per il mercato Day-Ahead Svizzero (Swissix).")
    
    st.subheader("⚙️ Console Timeframe")
    oggi = datetime.date.today()
    default_inizio = oggi - datetime.timedelta(days=7)

    if 'data_inizio' not in st.session_state:
        st.session_state.data_inizio = default_inizio
    if 'data_fine' not in st.session_state:
        st.session_state.data_fine = oggi

    def resetta_date():
        st.session_state.data_inizio = default_inizio
        st.session_state.data_fine = oggi

    col_inizio, col_fine, col_btn = st.columns([2, 2, 1])
    with col_inizio:
        data_inizio_selezionata = st.date_input("Data Inizio", value=st.session_state.data_inizio, key='data_inizio')
    with col_fine:
        data_fine_selezionata = st.date_input("Data Fine", value=st.session_state.data_fine, key='data_fine')
    with col_btn:
        st.write("") 
        st.write("")
        st.button("⏮️ Reset (Ultimi 7 gg)", on_click=resetta_date)

    if st.button("🚀 Forza Aggiornamento Dati (Svuota Cache)"):
        scarica_dati_entsoe.clear()
        st.success("Cache svuotata! Aggiornamento in corso...")

    st.markdown("---")
    
    try:
        with st.spinner("⏳ Connessione a ENTSO-E in corso... Elaborazione dei dati di mercato..."):
            api_key = "69b86d28-17c2-4e13-a587-1598048a6675"
            prezzi_ch = scarica_dati_entsoe(api_key, data_inizio_selezionata, data_fine_selezionata)
            
            prezzo_spot_ch = prezzi_ch.iloc[-1]
            data_ultimo_prezzo = prezzi_ch.index[-1].strftime('%d/%m/%Y %H:%00')
            
            st.subheader(f"Andamento Prezzo Spot Svizzera (Dal {data_inizio_selezionata.strftime('%d/%m/%Y')} al {data_fine_selezionata.strftime('%d/%m/%Y')})")
            st.line_chart(prezzi_ch, height=350)
            
            prezzo_gas_eu = 38.5  
            prezzo_co2_eu = 68.0  
            eff_ircd = 0.25 
            margine_ircd = prezzo_spot_ch - (prezzo_gas_eu / eff_ircd) - (prezzo_co2_eu * 0.2 / eff_ircd) 
            margine_biasca = prezzo_spot_ch - 5.0
            margine_muttsee = prezzo_spot_ch
            
            st.markdown("---")
            st.subheader("Margini Operativi Istantanei (Sull'ultimo prezzo rilevato)")
            col1, col2, col3 = st.columns(3)
            
            col1.metric(label="🏭 IRCD Giubiasco (Termovalorizzatore)", value=f"€ {margine_ircd:.2f} / MWh", delta="Proxy Margin (Power)", delta_color="off")
            col2.metric(label="💧 Centrale di Biasca (Idro)", value=f"€ {margine_biasca:.2f} / MWh", delta="Margine Netto O&M", delta_color="normal")
            col3.metric(label="☀️ Diga del Muttsee (Fotovoltaico)", value=f"€ {margine_muttsee:.2f} / MWh", delta="Margine Lordo", delta_color="normal")
            
            st.caption(f"Ultimo prezzo Spot CH rilevato da ENTSO-E: **€ {prezzo_spot_ch:.2f} / MWh** (del {data_ultimo_prezzo}) | Proxy Gas: €{prezzo_gas_eu} | Proxy CO2: €{prezzo_co2_eu}")

            with st.expander("💡 Approfondimento: Perché il margine Idroelettrico è minore del Fotovoltaico?"):
                st.markdown("""
                **1. Il costo della materia prima azzera l'impatto dell'efficienza**
                L'efficienza tecnica incide sui margini operativi solo se il carburante si paga (come per il gas). Poiché sole e acqua sono gratuiti, una volta immesso in rete un MWh, il costo del carburante per generarlo è pari a zero per entrambe le tecnologie.

                **2. Invecchiamento vs. Logorio Meccanico**
                * **Solare (Usura legata al tempo):** I pannelli invecchiano e si degradano fisiologicamente anche se non producono (costo fisso di ammortamento). Il costo marginale per l'utilizzo rimane zero.
                * **Idroelettrico (Usura legata all'uso):** Le turbine subiscono enormi stress fisici (vibrazioni, usura cuscinetti) *solo* quando girano. Questo logorio meccanico è un vero Costo Variabile di Manutenzione (O&M variabile), stimato a 5 €/MWh.

                **3. La decisione in Sala Operativa (Dispatching)**
                Il solare immette energia a mercato a prescindere dal prezzo, avendo costo marginale nullo. L'idroelettrico viene invece avviato dal trader solo se il prezzo di mercato offerto supera almeno il costo del "consumo" fisico della turbina (es. > 5 €/MWh), altrimenti è più conveniente tenere la centrale spenta.
                """)

    except Exception as e:
        st.error(f"Si è verificato un errore durante il recupero dei dati da ENTSO-E: {e}")

# ==========================================
# WORKSPACE 3: AI & MARL
# ==========================================
elif workspace == "🤖 Autonomous AI & MARL":
    st.title("🤖 Multi-Agent Reinforcement Learning (MARL)")
    c1, c2, c3, c4 = st.columns(4)
    render_kpi("Stato Agente Primario", "🟢 ACTIVE (Live)", c1)
    render_kpi("Reward (Sharpe Cumulativo)", "2.84", c2)
    render_kpi("Flash Crash Probability", f"{np.random.uniform(0.1, 5.0):.1f}%", c3)
    render_kpi("NLP Trade Sentiment", f"{ult['Sentiment_NLP']:.2f}", c4)
    epoches = np.arange(500)
    reward_curve = -50 + 100 * np.log(epoches + 1) / np.log(500) + np.random.normal(0, 5, 500)
    fig_rl = px.line(x=epoches, y=reward_curve, title="Reward Function dell'Agente (Max Sharpe Ratio)")
    fig_rl.update_layout(template="plotly_dark")
    st.plotly_chart(fig_rl, use_container_width=True)

# ==========================================
# WORKSPACE 4: CLIMATE & GRID
# ==========================================
elif workspace == "🌍 Climate & Grid Intel":
    st.title("🌍 Geospatial Climate Intelligence & Grid Physics")
    wind_speeds = np.linspace(0, 25, 100)
    power = np.where(wind_speeds < 3, 0, np.where(wind_speeds <= 12, (wind_speeds-3)**3 * 10, 3000))
    fig_wind = px.line(x=wind_speeds, y=power, title="Produzione Eolica Teorica vs Velocità Vento")
    fig_wind.update_layout(template="plotly_dark")
    st.plotly_chart(fig_wind, use_container_width=True)

# ==========================================
# WORKSPACE 5: EXOTICS
# ==========================================
elif workspace == "📈 Exotics & Structuring":
    st.title("📈 Exotic Derivatives, SABR & Curve Structuring")
    strikes = np.linspace(30, 150, 40)
    smile = 0.4 + 0.0001 * (strikes - 80)**2 - 0.002 * (strikes - 80)
    fig_sabr = px.line(x=strikes, y=smile*100, title="SABR Implied Volatility Surface Slice")
    fig_sabr.update_layout(template="plotly_dark")
    st.plotly_chart(fig_sabr, use_container_width=True)

# ==========================================
# WORKSPACE 6: RISK & XVA
# ==========================================
elif workspace == "🏛️ Enterprise Risk & XVA":
    st.title("🏛️ Regulatory Capital (FRTB) & XVA Desk")
    st.error("🚨 **SIMM MARGIN BREACH WARNING:** Probabilità 84% di Margin Call su ICE Endex domani.")
    horizons = pd.DataFrame({
        "Asset Class": ["Power (Spot)", "Gas (Prompt)", "Coal (API2)", "Carbon (EUA)"],
        "Capital Charge": [15.2, 18.5, 8.4, 3.1]
    })
    fig_frtb = px.bar(horizons, x="Asset Class", y="Capital Charge", title="Assorbimento Capitale (M€)")
    fig_frtb.update_layout(template="plotly_dark")
    st.plotly_chart(fig_frtb, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #4B5563; font-size: 10px; font-family: monospace;'>"
            "Singularity OS V15 + Classic ETRM Sim | Unified Quantitative Terminal"
            "</div>", unsafe_allow_html=True)
