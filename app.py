import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import norm, weibull_min
from plotly.subplots import make_subplots

# ==========================================
# 1. SETUP TERMINALE, CSS & EDU-TOOLTIPS
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
    
    /* FIX: Impedisce al testo dei toggle (Edu Mode) di andare a capo */
    div[data-testid="stWidgetLabel"] p { white-space: nowrap; }
    
    /* TOOLTIP DIDATTICO CSS */
    .edu-tooltip { position: relative; display: inline-block; border-bottom: 1px dotted #3B82F6; cursor: help; color: #93C5FD; font-weight: 600;}
    .edu-tooltip .edu-tooltiptext { visibility: hidden; width: 280px; background-color: #1F2937; color: #F9FAFB; text-align: left; border-radius: 6px; padding: 12px; position: absolute; z-index: 999; bottom: 125%; left: 50%; margin-left: -140px; opacity: 0; transition: opacity 0.3s; font-size: 11px; box-shadow: 0px 10px 15px rgba(0,0,0,0.8); border: 1px solid #3B82F6; font-family: 'Inter', sans-serif; font-weight: normal;}
    .edu-tooltip:hover .edu-tooltiptext { visibility: visible; opacity: 1; }
    
    /* Stile per i radio button del quiz */
    div[role="radiogroup"] > label { background-color: #1F2937; padding: 15px; border-radius: 8px; border: 1px solid #374151; margin-bottom: 10px; cursor: pointer; transition: all 0.2s; }
    div[role="radiogroup"] > label:hover { background-color: #374151; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MOTORE DI TRADUZIONE (i18n) & EDU HELPER
# ==========================================
if 'lang' not in st.session_state: st.session_state.lang = 'IT'
if 'edu_mode' not in st.session_state: st.session_state.edu_mode = True

T = {
    'IT': {
        'auth_title': 'Identificazione Biometrica / Hardware Key Richiesta',
        'auth_btn': 'Decripta Terminale',
        'ws1': '🎛️ Simulatore Strategico (Classico)',
        'ws2': '🌍 Dati Reali Svizzeri (ENTSO-E)',
        'ws3': '🤖 Autonomous AI & MARL',
        'ws4': '🌍 Climate & Grid Intel',
        'ws5': '📈 Exotics & Structuring',
        'ws6': '🏛️ Enterprise Risk & XVA',
        'ws7': '🎓 Practice Test (Analyst)',
        'prompt': 'Chiedi all\'AI',
        'market_params': '⚙️ Parametri di Mercato'
    },
    'EN': {
        'auth_title': 'Biometric Identification / Hardware Key Required',
        'auth_btn': 'Decrypt Terminal',
        'ws1': '🎛️ Strategic Simulator (Classic)',
        'ws2': '🌍 Swiss Real Data (ENTSO-E)',
        'ws3': '🤖 Autonomous AI & MARL',
        'ws4': '🌍 Climate & Grid Intel',
        'ws5': '📈 Exotics & Structuring',
        'ws6': '🏛️ Enterprise Risk & XVA',
        'ws7': '🎓 Practice Test (Analyst)',
        'prompt': 'Ask AI Copilot',
        'market_params': '⚙️ Market Parameters'
    },
    'FR': {
        'auth_title': 'Identification Biométrique / Clé Matérielle Requise',
        'auth_btn': 'Déchiffrer le Terminal',
        'ws1': '🎛️ Simulateur Stratégique (Classique)',
        'ws2': '🌍 Données Réelles Suisses (ENTSO-E)',
        'ws3': '🤖 IA Autonome & MARL',
        'ws4': '🌍 Climat & Réseau Intel',
        'ws5': '📈 Exotiques & Structuration',
        'ws6': '🏛️ Risque d\'Entreprise & XVA',
        'ws7': '🎓 Test Pratique (Analyste)',
        'prompt': 'Demander à l\'IA',
        'market_params': '⚙️ Paramètres du Marché'
    }
}

def _(key, default=None):
    return T.get(st.session_state.lang, {}).get(key, default or key)

def edu(term, explanation):
    if st.session_state.edu_mode:
        return f'<div class="edu-tooltip">{term}<span class="edu-tooltiptext"><b>💡 Lo Sapevi?</b><br><br>{explanation}</span></div>'
    return term

# ==========================================
# 3. AUTENTICAZIONE
# ==========================================
if 'authenticated' not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    lang_sel = st.selectbox("🌐 Language / Lingua / Langue", ["IT", "EN", "FR"], index=["IT", "EN", "FR"].index(st.session_state.lang))
    if lang_sel != st.session_state.lang:
        st.session_state.lang = lang_sel
        st.rerun()
        
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<h2 style='text-align: center; color: #3B82F6;'>💠 SINGULARITY OS</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{_('auth_title')}</p>", unsafe_allow_html=True)
        pwd = st.text_input("Key (Scrivi 'admin')", type="password")
        if st.button(_('auth_btn')):
            if pwd == "admin": 
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Access Denied.")
    st.stop()

# ==========================================
# 4. CORE DATA ENGINE & API ENTSO-E
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
    df['Wind_Speed_ms'] = weibull_min.rvs(2, loc=0, scale=8, size=days)
    df['Sentiment_NLP'] = np.clip(np.random.normal(0.1, 0.4, days), -1, 1)
    return df

df = generate_singularity_data()
ult = df.iloc[-1]

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistema Quantitativo Operativo. Come posso assisterti?"}]

# ==========================================
# 5. SIDEBAR & GLOBAL CONTROLS
# ==========================================
with st.sidebar:
    st.markdown("<h2>💠 SINGULARITY</h2>", unsafe_allow_html=True)
    
    col_l, col_e = st.columns([1, 1.5])
    with col_l:
        new_lang = st.selectbox("🌐 Lang", ["IT", "EN", "FR"], index=["IT", "EN", "FR"].index(st.session_state.lang))
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            st.rerun()
    with col_e:
        st.session_state.edu_mode = st.toggle("🎓 Edu Mode", value=st.session_state.edu_mode, help="Attiva i tooltip esplicativi sui termini tecnici.")
    
    st.markdown("---")
    
    workspace = st.radio("🏢 WORKSPACES", [
        _('ws1'), _('ws2'), _('ws3'), _('ws4'), _('ws5'), _('ws6'), _('ws7')
    ])
    
    st.markdown("---")
    st.markdown("### 💬 Copilot Quant LLM")
    for msg in st.session_state.messages:
        st.markdown(f"<div class='chat-msg'><b>{msg['role'].upper()}:</b> {msg['content']}</div>", unsafe_allow_html=True)
    
    if prompt := st.chat_input(_('prompt')):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": f"Elaborazione: '{prompt}'. Il modello indica delta-hedging."})
        st.rerun()

def render_kpi(title, value, col):
    col.markdown(f"<div class='metric-container'><div class='metric-label'>{title}</div><div class='metric-val'>{value}</div></div>", unsafe_allow_html=True)

# ==========================================
# WORKSPACE 1: SIMULATORE STRATEGICO
# ==========================================
if workspace == _('ws1'):
    st.markdown(f"<h1>{_('ws1')}</h1>", unsafe_allow_html=True)
    st.info("📌 **Nota Operativa:** Il grafico calcola i margini operativi lordi. Attiva o disattiva le centrali per sovrapporre le rette di profittabilità e confrontare i costi marginali (Punto di Break-Even).")

    chart_container = st.container()
    st.markdown("---")
    
    st.markdown(f"### 🎛️ Seleziona Livelli (Overlay Grafico)")
    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    show_gas = t_col1.toggle("🏭 Gas Naturale (CSS)", value=True)
    show_coal = t_col2.toggle("⛏️ Carbone (CDS)", value=True)
    show_hydro = t_col3.toggle("💧 Idroelettrica", value=False)
    show_solar = t_col4.toggle("☀️ Solare", value=False)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader(_('market_params'))
    
    param_cols = st.columns(4)
    with param_cols[0]:
        st.markdown("**Variabili Globali**")
        p_elec = st.number_input("Prezzo Energia Corrente (€/MWh)", min_value=0.0, max_value=400.0, value=100.0, step=1.0)
        
    costo_marginale_gas = 0
    if show_gas:
        with param_cols[1]:
            st.markdown("**Impostazioni Gas**")
            p_gas = st.number_input("Prezzo Gas (€/MWh)", value=40.0)
            p_co2_gas = st.number_input("Prezzo CO2 (€/tCO2)", value=80.0, key="co2_gas")
            eff_gas = st.number_input("Efficienza Gas (η)", value=0.50, step=0.01)
            costo_marginale_gas = (p_gas / eff_gas) + (p_co2_gas * 0.2 / eff_gas)

    costo_marginale_coal = 0
    if show_coal:
        with param_cols[2]:
            st.markdown("**Impostazioni Carbone**")
            p_coal = st.number_input("Prezzo Carbone (€/MWh)", value=20.0)
            p_co2_coal = st.number_input("Prezzo CO2 (€/tCO2)", value=80.0, key="co2_coal")
            eff_coal = st.number_input("Efficienza Carbone (η)", value=0.40, step=0.01)
            costo_marginale_coal = (p_coal / eff_coal) + (p_co2_coal * 0.34 / eff_coal)

    costo_marginale_hydro = 0
    if show_hydro:
        with param_cols[3]:
            st.markdown("**Impostazioni Idroelettrica**")
            costo_om_hydro = st.number_input("Costi O&M (€/MWh)", value=5.0)
            costo_marginale_hydro = costo_om_hydro
            
    costo_marginale_solar = 0 

    with chart_container:
        prezzi_range = np.linspace(0, 300, 150)
        fig_sim = go.Figure()
        
        fig_sim.add_hline(y=0, line_width=1, line_dash="solid", line_color="rgba(255,255,255,0.3)")
        colors = {"Gas": "#ef4444", "Coal": "#a8a29e", "Hydro": "#3b82f6", "Solar": "#eab308"}
        
        if show_gas:
            m_gas_arr = prezzi_range - costo_marginale_gas
            fig_sim.add_trace(go.Scatter(x=prezzi_range, y=m_gas_arr, mode='lines', name="Gas Naturale (CSS)", line=dict(color=colors["Gas"], width=3)))
            fig_sim.add_vline(x=costo_marginale_gas, line_dash="dot", line_color=colors["Gas"], annotation_text=f" BE Gas: {costo_marginale_gas:.1f} €", annotation_position="bottom right")
            
        if show_coal:
            m_coal_arr = prezzi_range - costo_marginale_coal
            fig_sim.add_trace(go.Scatter(x=prezzi_range, y=m_coal_arr, mode='lines', name="Carbone (CDS)", line=dict(color=colors["Coal"], width=3)))
            fig_sim.add_vline(x=costo_marginale_coal, line_dash="dot", line_color=colors["Coal"], annotation_text=f" BE Coal: {costo_marginale_coal:.1f} €", annotation_position="top right")

        if show_hydro:
            m_hydro_arr = prezzi_range - costo_marginale_hydro
            fig_sim.add_trace(go.Scatter(x=prezzi_range, y=m_hydro_arr, mode='lines', name="Idroelettrica", line=dict(color=colors["Hydro"], width=3)))
            fig_sim.add_vline(x=costo_marginale_hydro, line_dash="dot", line_color=colors["Hydro"], annotation_text=f" BE Idro: {costo_marginale_hydro:.1f} €", annotation_position="bottom right")

        if show_solar:
            m_solar_arr = prezzi_range - costo_marginale_solar
            fig_sim.add_trace(go.Scatter(x=prezzi_range, y=m_solar_arr, mode='lines', name="Solare", line=dict(color=colors["Solar"], width=3)))
            fig_sim.add_vline(x=costo_marginale_solar, line_dash="dot", line_color=colors["Solar"], annotation_text=" BE Solare: 0 €", annotation_position="top right")

        fig_sim.update_layout(
            title="Confronto Margini Operativi (Merit Order Simulation)",
            xaxis_title="Prezzo Elettricità (€/MWh)",
            yaxis_title="Margine (€/MWh)",
            template="plotly_dark",
            height=450,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_sim, use_container_width=True)

    st.markdown("---")
    
    calc_cols = st.columns(2)
    with calc_cols[0]:
        st.markdown("### Modelli Matematici e Formule")
        if show_gas:
            st.markdown(f"**{edu('Clean Spark Spread (CSS)', 'Indica il profitto teorico di una centrale a gas dopo aver pagato il gas e i permessi per inquinare (CO2).')}**")
            st.markdown("$$CSS = P_{elec} - \\frac{P_{gas}}{\\eta} - \\frac{P_{CO_2} \\cdot E_f}{\\eta}$$")
        if show_coal:
            st.markdown(f"**{edu('Clean Dark Spread (CDS)', 'Il profitto teorico di una centrale a CARBONE. A causa del fattore di emissione elevato (0.34 contro 0.2 del gas), è molto sensibile ai prezzi della CO2.')}**")
            st.markdown("$$CDS = P_{elec} - \\frac{P_{coal}}{\\eta} - \\frac{P_{CO_2} \\cdot E_f}{\\eta}$$")
        if show_hydro:
            st.markdown(f"**{edu('Dispatching Idroelettrico', 'Si decide di far cadere l\'acqua dai bacini solo quando il prezzo di mercato copre l\'usura meccanica delle turbine (O&M)')}**")
            st.markdown("$$Margine = P_{elec} - O\\&M_{var}$$")
        if show_solar:
            st.markdown(f"**{edu('Merit Order (Rinnovabili)', 'Il solare ha un costo marginale (MC) pari a ZERO. Il sole è gratis.')}**")
            st.markdown("$$Margine = P_{elec}$$")

    with calc_cols[1]:
        st.markdown(f"### Analisi di Profitto Istantaneo")
        st.markdown(f"*Calcolato al Prezzo Corrente inserito: **{p_elec} €/MWh***")
        
        res_cols = st.columns(2)
        idx = 0
        
        if show_gas:
            margine = p_elec - costo_marginale_gas
            col_target = res_cols[idx % 2]
            color = "#10B981" if margine > 0 else "#EF4444"
            status = "🟢 ON (In-the-Money)" if margine > 0 else "🔴 OFF (Out-of-Money)"
            col_target.markdown(f"<div style='background:#1F2937; padding:10px; border-radius:8px; margin-bottom:10px; border-left:4px solid {color};'><b>Gas Naturale</b><br><span style='font-size:20px; font-weight:bold; color:{color};'>€ {margine:.2f}</span><br><span style='font-size:12px;'>AI Status: {status}</span></div>", unsafe_allow_html=True)
            idx += 1
            
        if show_coal:
            margine = p_elec - costo_marginale_coal
            col_target = res_cols[idx % 2]
            color = "#10B981" if margine > 0 else "#EF4444"
            status = "🟢 ON (In-the-Money)" if margine > 0 else "🔴 OFF (Out-of-Money)"
            col_target.markdown(f"<div style='background:#1F2937; padding:10px; border-radius:8px; margin-bottom:10px; border-left:4px solid {color};'><b>Carbone</b><br><span style='font-size:20px; font-weight:bold; color:{color};'>€ {margine:.2f}</span><br><span style='font-size:12px;'>AI Status: {status}</span></div>", unsafe_allow_html=True)
            idx += 1
            
        if show_hydro:
            margine = p_elec - costo_marginale_hydro
            col_target = res_cols[idx % 2]
            color = "#10B981" if margine > 0 else "#EF4444"
            status = "🟢 ON (In-the-Money)" if margine > 0 else "🔴 OFF (Out-of-Money)"
            col_target.markdown(f"<div style='background:#1F2937; padding:10px; border-radius:8px; margin-bottom:10px; border-left:4px solid {color};'><b>Idroelettrica</b><br><span style='font-size:20px; font-weight:bold; color:{color};'>€ {margine:.2f}</span><br><span style='font-size:12px;'>AI Status: {status}</span></div>", unsafe_allow_html=True)
            idx += 1
            
        if show_solar:
            margine = p_elec - costo_marginale_solar
            col_target = res_cols[idx % 2]
            color = "#10B981" if margine > 0 else "#EF4444"
            status = "🟢 ON (In-the-Money)" if margine > 0 else "🔴 OFF (Out-of-Money)"
            col_target.markdown(f"<div style='background:#1F2937; padding:10px; border-radius:8px; margin-bottom:10px; border-left:4px solid {color};'><b>Solare</b><br><span style='font-size:20px; font-weight:bold; color:{color};'>€ {margine:.2f}</span><br><span style='font-size:12px;'>AI Status: {status}</span></div>", unsafe_allow_html=True)
            idx += 1

# ==========================================
# WORKSPACE 2: DATI REALI SVIZZERI (ENTSO-E)
# ==========================================
elif workspace == _('ws2'):
    st.markdown(f"<h1>{_('ws2')}</h1>", unsafe_allow_html=True)
    
    desc_html = edu("API Ufficiale ENTSO-E", "ENTSO-E (European Network of Transmission System Operators for Electricity) è l'associazione europea dei gestori di rete. La loro piattaforma Transparency Platform (transparency.entsoe.eu) è la fonte dati primaria per ogni trader quantitativo, offrendo dati su produzione, consumi e blackout per tutta Europa.")
    st.markdown(f"Questa dashboard interroga l'{desc_html} per il mercato Day-Ahead Svizzero (Swissix).", unsafe_allow_html=True)
    
    st.subheader("⚙️ Console Timeframe")
    
    oggi = datetime.date.today()
    default_inizio = oggi - datetime.timedelta(days=7)

    col_inizio, col_fine, col_btn = st.columns([2, 2, 1])
    with col_inizio:
        data_inizio_selezionata = st.date_input("Data Inizio", value=default_inizio)
    with col_fine:
        data_fine_selezionata = st.date_input("Data Fine", value=oggi)
    with col_btn:
        st.write(""); st.write("")
        if st.button("🚀 Aggiorna API Cache"): scarica_dati_entsoe.clear()

    st.markdown("---")
    
    try:
        with st.spinner("⏳ Connessione a ENTSO-E in corso..."):
            api_key = "69b86d28-17c2-4e13-a587-1598048a6675"
            prezzi_ch = scarica_dati_entsoe(api_key, data_inizio_selezionata, data_fine_selezionata)
            
            prezzo_spot_ch = prezzi_ch.iloc[-1]
            valore_integrale = prezzi_ch.sum()
            
            fig_entsoe = go.Figure()
            fig_entsoe.add_trace(go.Scatter(
                x=prezzi_ch.index, 
                y=prezzi_ch.values, 
                fill='tozeroy', 
                fillcolor='rgba(59, 130, 246, 0.2)',
                mode='lines',
                line=dict(color='#3b82f6', width=2),
                name="Prezzo Spot (€/MWh)"
            ))
            fig_entsoe.update_layout(
                title=f"Andamento Prezzo Spot & Integrale del Valore (Totale Baseload 1 MW: {valore_integrale:,.0f} €)",
                xaxis_title="Data e Ora", 
                yaxis_title="Prezzo (€/MWh)", 
                template="plotly_dark", 
                height=350,
                margin=dict(l=40, r=40, t=40, b=40)
            )
            st.plotly_chart(fig_entsoe, use_container_width=True)
            
            eff_ircd = 0.25; prezzo_gas_eu = 38.5; prezzo_co2_eu = 68.0  
            mc_gas = (prezzo_gas_eu / eff_ircd) + (prezzo_co2_eu * 0.2 / eff_ircd) 
            mc_hydro = 5.0
            mc_solar = 0.0

            margine_ircd = prezzo_spot_ch - mc_gas
            margine_hydro = prezzo_spot_ch - mc_hydro
            margine_solar = prezzo_spot_ch - mc_solar
            
            st.subheader("Margini Operativi Istantanei (Sull'ultima candela oraria)")
            col1, col2, col3 = st.columns(3)
            
            col1.metric(label="🏭 IRCD Giubiasco", value=f"€ {margine_ircd:.2f}", delta="Termovalorizzatore (Proxy Gas)", help="Margine per un impianto WtE (Waste-to-Energy)")
            col2.metric(label="💧 Centrale Biasca", value=f"€ {margine_hydro:.2f}", delta="Idroelettrico", help="Margine decurtato dai costi di O&M")
            col3.metric(label="☀️ Diga del Muttsee", value=f"€ {margine_solar:.2f}", delta="Solare d'Alta Quota", help="Impianto solare alpino, massima efficienza invernale.")
            
            st.markdown("---")

            titolo_mo = edu("Merit Order & Produzione Stimata", "Il Merit Order mette in fila le centrali dalla più economica (Rinnovabili) alla più costosa (Gas/Carbone). L'intersezione con la domanda determina il prezzo. Qui mostriamo anche la stima dell'energia prodotta nel timeframe calcolando quante ore la singola centrale è risultata 'In-The-Money' (Prezzo Spot > Costo Marginale).")
            st.markdown(f"### {titolo_mo}", unsafe_allow_html=True)

            cap_solar = 50   
            cap_hydro = 250  
            cap_gas = 100    
            tot_hours = len(prezzi_ch)
            
            prod_solar = cap_solar * (tot_hours * 0.30)
            ore_in_money_hydro = (prezzi_ch > mc_hydro).sum()
            prod_hydro = cap_hydro * ore_in_money_hydro
            ore_in_money_gas = (prezzi_ch > mc_gas).sum()
            prod_gas = cap_gas * ore_in_money_gas
            
            df_mo = pd.DataFrame({
                "Centrale": ["☀️ Solare (Muttsee)", "💧 Idro (Biasca)", "🏭 Gas WtE (Giubiasco)"],
                "Marginal_Cost": [mc_solar, mc_hydro, mc_gas],
                "Capacity": [cap_solar, cap_hydro, cap_gas],
                "Production": [prod_solar, prod_hydro, prod_gas],
                "Color": ["#eab308", "#3b82f6", "#ef4444"]
            }).sort_values(by="Marginal_Cost") 
            
            df_mo['Cum_Capacity'] = df_mo['Capacity'].cumsum()
            df_mo['X_Center'] = df_mo['Cum_Capacity'] - (df_mo['Capacity'] / 2)
            
            fig_mo = go.Figure()
            
            for i, row in df_mo.iterrows():
                fig_mo.add_trace(go.Bar(
                    x=[row['X_Center']],
                    y=[row['Marginal_Cost']],
                    width=[row['Capacity']],
                    marker_color=row['Color'],
                    name=row['Centrale'],
                    text=f"Prod. Stima:<br><b>{row['Production']:,.0f} MWh</b>",
                    textposition="outside",
                    hovertemplate=(
                        f"<b>{row['Centrale']}</b><br>" +
                        "Costo Marginale: %{y:.1f} €/MWh<br>" +
                        "Capacità: %{width} MW<br>" +
                        f"Prod. Timeframe: {row['Production']:,.0f} MWh<extra></extra>"
                    )
                ))
            
            avg_price = prezzi_ch.mean()
            fig_mo.add_hline(y=avg_price, line_dash="dot", line_color="white", 
                             annotation_text=f"Prezzo Medio Timeframe: {avg_price:.1f} €/MWh", 
                             annotation_position="top left")
            
            fig_mo.update_layout(
                title="Curva di Offerta Aggregata (Merit Order)",
                xaxis_title="Capacità Cumulata (MW)",
                yaxis_title="Costo Marginale (€/MWh)",
                template="plotly_dark",
                barmode='overlay',
                height=400,
                showlegend=True,
                margin=dict(t=50, b=50, l=50, r=50)
            )
            fig_mo.update_xaxes(range=[0, df_mo['Cum_Capacity'].max() + 50])
            fig_mo.update_yaxes(range=[0, max(mc_gas * 1.3, avg_price * 1.3)])
            
            st.plotly_chart(fig_mo, use_container_width=True)
            
    except Exception as e:
        st.error(f"Errore connessione ENTSO-E: {e}")

# ==========================================
# WORKSPACE 3: AUTONOMOUS AI & MARL
# ==========================================
elif workspace == _('ws3'):
    titolo_marl = edu("Multi-Agent Reinforcement Learning (MARL)", "Nel MARL, algoritmi (agenti) operano in un ambiente simulato, compiendo azioni (compra/vendi) e ricevendo una ricompensa (Profitto) o una penalità (Perdita). Col tempo, la rete neurale 'impara' le strategie ottimali senza programmazione esplicita.")
    st.markdown(f"<h1>🤖 {titolo_marl}</h1>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    render_kpi("Stato Agente AI", "🟢 ACTIVE", c1)
    render_kpi("Sharpe Ratio AI", "2.84", c2)
    render_kpi(edu("Flash Crash Prob", "Probabilità stimata dai Processi di Hawkes che si verifichi un crollo repentino dei prezzi guidato da algoritmi HFT."), f"1.4%", c3)
    render_kpi(edu("NLP Sentiment", "Natural Language Processing: algoritmo che legge le news di Reuters/Bloomberg e assegna uno score (-1 Bear, +1 Bull)."), f"{ult['Sentiment_NLP']:.2f}", c4)
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        epoches = np.arange(1000)
        reward_curve = -50 + 100 * np.log(epoches + 1) / np.log(1000) + np.random.normal(0, 5, 1000)
        fig_rl = px.line(x=epoches, y=reward_curve, title="Learning Curve dell'Agente Quantitativo")
        fig_rl.update_layout(template="plotly_dark", xaxis_title="Epoche di Addestramento", yaxis_title="Reward (PnL in €)")
        st.plotly_chart(fig_rl, use_container_width=True)
        
    with col_b:
        regime = "BULLISH" if ult['Sentiment_NLP'] > 0 else "BEARISH"
        st.markdown(f"<h3>Regime: {regime}</h3>", unsafe_allow_html=True)
        st.markdown(f"**{edu('Stat Arb Z-Score', 'Statistical Arbitrage: Z-Score misura di quante deviazioni standard lo spread tra due asset (es. Gas/Power) si è discostato dalla media storica.')}:** +2.4", unsafe_allow_html=True)
        
        heatmap_lat = np.random.normal(1.5, 0.2, (5, 5))
        fig_lat = px.imshow(heatmap_lat, color_continuous_scale="RdYlGn_r", title="Network Latency (ms)")
        fig_lat.update_layout(template="plotly_dark", height=200, margin=dict(l=0, r=0, t=30, b=0), xaxis_title="Gateway Node", yaxis_title="Exchange Node")
        st.plotly_chart(fig_lat, use_container_width=True)

# ==========================================
# WORKSPACE 4: CLIMATE & GRID INTEL
# ==========================================
elif workspace == _('ws4'):
    st.markdown(f"<h1>{_('ws4')}</h1>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    enso_html = edu("ENSO Index", "El Niño-Southern Oscillation. Fenomeno climatico nel Pacifico. I trader energetici lo osservano perché anomalie qui influenzano la rigidità degli inverni in Europa, e di conseguenza la domanda di gas e power.")
    render_kpi(enso_html, "1.2 (El Niño)", c1)
    
    vortex_html = edu("Polar Vortex", "Vortice Polare: se debole/instabile, l'aria gelida artica scivola verso l'Europa causando ondate di gelo estremo (es. Beast from the East).")
    render_kpi(vortex_html, "Stabile", c2)
    
    inertia_html = edu("Grid Inertia", "L'inerzia della rete. Mantenuta dalle enormi turbine rotanti delle centrali termiche. Con l'aumento di solare/eolico (che non hanno masse rotanti), l'inerzia crolla, rendendo la rete instabile. Molto importante per i trader di 'Ancillary Services'.")
    render_kpi(inertia_html, "CRITICA", c3)
    render_kpi("Dynamic Line Rating", "+15% Cap", c4)
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        titolo_wind = edu("Wind Power Curve", "Curva di potenza teorica di una turbina eolica. Mostra come i megawatt generati dipendano in modo non lineare (spesso cubico) dalla velocità del vento. Raggiunto il 'Rated Wind Speed', la potenza si appiattisce al massimo. Oltre il 'Cut-out Speed', la turbina si blocca per sicurezza, azzerando la produzione di colpo e causando picchi di prezzo in borsa.")
        st.markdown(f"### {titolo_wind}", unsafe_allow_html=True)
        
        wind_speeds = np.linspace(0, 30, 200)
        rated_power = 3000
        power = np.where(wind_speeds < 3, 0, 
                np.where(wind_speeds <= 12, rated_power * ((wind_speeds - 3) / 9)**3, 
                np.where(wind_speeds <= 25, rated_power, 0)))
        
        fig_wind = px.line(x=wind_speeds, y=power)
        fig_wind.update_layout(template="plotly_dark", xaxis_title="Velocità Vento (m/s)", yaxis_title="Potenza Generata (MW)")
        st.plotly_chart(fig_wind, use_container_width=True)
        
    with col_w2:
        titolo_hydro = edu("Hydro Reservoir Topography", "Rappresentazione topografica 3D del livello dell'acqua di un bacino idroelettrico alpino. Maggiore è il volume e l'altezza dell'acqua, maggiore è l'energia potenziale accumulata (State of Charge - SoC) pronta per essere convertita in MWh alla prima occasione profittevole.")
        st.markdown(f"### {titolo_hydro}", unsafe_allow_html=True)
        
        X, Y = np.meshgrid(np.linspace(-5, 5, 30), np.linspace(-5, 5, 30))
        Z = (X**2 * 0.8 + Y**2 * 1.2) * 5 + 400
        Z = np.clip(Z, 420, 600) 
        
        fig_hydro = go.Figure(data=[go.Surface(z=Z, colorscale="Blues", reversescale=True)])
        fig_hydro.update_layout(template="plotly_dark", height=300, margin=dict(l=0, r=0, t=0, b=0), scene=dict(xaxis_title="Latitudine (X)", yaxis_title="Longitudine (Y)", zaxis_title="Livello Acqua (m)"))
        st.plotly_chart(fig_hydro, use_container_width=True)

# ==========================================
# WORKSPACE 5: EXOTICS & STRUCTURING
# ==========================================
elif workspace == _('ws5'):
    st.markdown(f"<h1>{_('ws5')}</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    render_kpi(edu("SABR Alpha", "Parametro del modello SABR (Stochastic Alpha Beta Rho) che governa il livello iniziale della volatilità stocastica."), "0.354", c1)
    render_kpi("SABR Beta", "0.500", c2)
    render_kpi(edu("Quanto Corr (ρ)", "Correlazione in un'opzione 'Quanto', un derivato in cui l'asset sottostante è in una valuta (es. Gas in USD) ma regolato in un'altra (EUR) ad un tasso fisso."), "-0.45", c3)
    
    col_e1, col_e2 = st.columns([1.5, 1])
    with col_e1:
        st.markdown("### Implied Volatility Smile")
        strikes = np.linspace(30, 150, 40)
        smile = 0.4 + 0.0001 * (strikes - 80)**2 - 0.002 * (strikes - 80)
        fig_sabr = px.line(x=strikes, y=smile*100)
        fig_sabr.add_vline(x=80, line_dash="dash", line_color="red")
        fig_sabr.update_layout(template="plotly_dark", xaxis_title="Strike Price (€/MWh)", yaxis_title="Implied Volatility (%)")
        st.plotly_chart(fig_sabr, use_container_width=True)
        
    with col_e2:
        st.markdown("### 3rd Order Greeks")
        st.markdown(f"🚀 **{edu('Speed', 'Variazione del Gamma rispetto a cambiamenti nel prezzo spot (Derivata terza del premio).')} (dGamma/dSpot):** -0.0014", unsafe_allow_html=True)
        st.markdown(f"🎨 **{edu('Color', 'Decadimento temporale del Gamma (dGamma/dTime).')} (dGamma/dTime):** +0.0251", unsafe_allow_html=True)
        st.markdown(f"🌪️ **{edu('Zomma', 'Sensibilità del Gamma ai cambiamenti di volatilità. Fondamentale per i portafogli Gamma-hedged.')} (dGamma/dVol):** +0.1042", unsafe_allow_html=True)

# ==========================================
# WORKSPACE 6: ENTERPRISE RISK & XVA
# ==========================================
elif workspace == _('ws6'):
    st.markdown(f"<h1>{_('ws6')}</h1>", unsafe_allow_html=True)
    
    msg_error = edu("SIMM MARGIN Breach", "Standard Initial Margin Model: calcolo standard ISDA. Margin Breach significa che le perdite stimate superano la garanzia (collaterale) versata in borsa, innescando una chiamata a margine immediata.")
    st.markdown(f"<div style='background-color:rgba(255, 75, 75, 0.15); color:#ff4b4b; padding:1rem; border:1px solid #ff4b4b; border-radius:0.5rem; margin-bottom:1rem;'>🚨 **{msg_error} WARNING:** ICE Endex.</div>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    render_kpi(edu("FRTB Expected Shortfall", "Fundamental Review of the Trading Book. L'Expected Shortfall (ES) ha sostituito il VaR per le banche. Calcola la perdita MEDIA nel peggiore X% dei casi (Coda della distribuzione)."), "€ 45.2 M", c1)
    render_kpi(edu("CVA", "Credit Valuation Adjustment: Sconto sul fair value di un derivato a causa del rischio che la controparte fallisca."), "€ 2.1 M", c2)
    render_kpi("DVA", "€ 0.5 M", c3)
    render_kpi("ESG Score", "12 / 100", c4)
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown(f"### {edu('Liquidity Horizon', 'Sotto le nuove norme FRTB, non puoi assumere di vendere un asset istantaneamente. Il capitale da accantonare cresce in base a quanti giorni servono per liquidare il portafoglio in caso di crisi.')}", unsafe_allow_html=True)
        horizons = pd.DataFrame({"Asset Class": ["Power", "Gas", "Coal", "Carbon"], "Capital Charge": [15.2, 18.5, 8.4, 3.1]})
        fig_frtb = px.bar(horizons, x="Asset Class", y="Capital Charge")
        fig_frtb.update_layout(template="plotly_dark", height=300, xaxis_title="Classe di Asset", yaxis_title="Capitale Assorbito (M€)")
        st.plotly_chart(fig_frtb, use_container_width=True)
        
    with col_r2:
        st.markdown(f"### {edu('Wrong-Way Risk (WWR)', 'Si verifica quando l\'esposizione verso una controparte (EAD) aumenta in concomitanza con la probabilità di default (PD) della controparte stessa. Es: Compri opzioni Put su Enron da Enron stessa.')}", unsafe_allow_html=True)
        ead = np.random.lognormal(mean=2, sigma=0.5, size=100)
        pd_cpty = 0.01 + ead * 0.002 + np.random.normal(0, 0.01, 100)
        fig_wwr = px.scatter(x=ead, y=pd_cpty)
        fig_wwr.update_layout(template="plotly_dark", height=300, xaxis_title="Esposizione al Default - EAD (M€)", yaxis_title="Probabilità di Default - PD (%)")
        st.plotly_chart(fig_wwr, use_container_width=True)

# ==========================================
# WORKSPACE 7: PRACTICE TEST (ANALYST)
# ==========================================
elif workspace == _('ws7'):
    st.markdown("<h1>🎓 Practice Test - Energy Analyst & Trader (European Markets)</h1>", unsafe_allow_html=True)
    
    c_prog1, c_prog2 = st.columns([4, 1])
    with c_prog1:
        st.progress(8/15)
    with c_prog2:
        st.markdown("<div style='text-align: right; font-weight: bold;'>8/15 &nbsp;&nbsp; <span style='color:#EF4444;'>❌ 0</span> &nbsp;&nbsp; <span style='color:#10B981;'>✔️ 3</span></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<h3 style='line-height: 1.5; color: #E5E7EB; margin-bottom: 25px;'>Al fine di ottimizzare il proprio profilo LinkedIn per attirare l'attenzione dei recruiter di aziende di trading di materie prime come DXT Commodities, quale approccio nella sezione 'Esperienza' dimostra meglio un set di competenze quantificabili e rilevanti?</h3>", unsafe_allow_html=True)
    
    if 'quiz_answered' not in st.session_state:
        st.session_state.quiz_answered = False
        st.session_state.quiz_choice = None

    def check_answer():
        st.session_state.quiz_answered = True

    choice = st.radio(
        "Seleziona un'opzione:",
        options=[
            "A. Enfatizzare competenze trasversali generiche, scrivendo: 'Eccellenti capacità di comunicazione e forte propensione al lavoro di squadra in ambienti ad alta pressione'.",
            "B. Concentrarsi esclusivamente sulle nozioni accademiche apprese, elencando tutti i corsi universitari seguiti inerenti all'energia e all'economia.",
            "C. Utilizzare il metodo STAR e inserire metriche, ad esempio: 'Sviluppato un modello in Python per l'analisi dello spark spread storico, riducendo i tempi di reportistica del 20%'."
        ],
        key="quiz_choice",
        label_visibility="collapsed",
        index=None if not st.session_state.quiz_answered else (2 if "C." in st.session_state.quiz_choice else (0 if "A." in st.session_state.quiz_choice else 1))
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not st.session_state.quiz_answered:
        st.button("Conferma Risposta", on_click=check_answer, type="primary")
    else:
        if "C." in st.session_state.quiz_choice:
            st.markdown("""
            <div style='background-color:rgba(16, 185, 129, 0.1); border:1px solid #10B981; border-radius:8px; padding:20px; margin-bottom:15px;'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>
                    <span style='color:#10B981; font-weight:bold; font-size:18px;'>✔️ (La tua risposta) Corretta</span>
                </div>
                <p style='color:#E5E7EB; line-height:1.6;'>Questo approccio combina competenze tecniche specifiche (Python, spark spread), descrive un'azione concreta (sviluppato un modello) e quantifica il risultato (ridotto i tempi del 20%), che è il metodo più efficace per dimostrare valore.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Ricomincia", type="secondary"):
                st.session_state.quiz_answered = False
                st.rerun()
        else:
            st.markdown("""
            <div style='background-color:rgba(239, 68, 68, 0.1); border:1px solid #EF4444; border-radius:8px; padding:20px; margin-bottom:15px;'>
                <span style='color:#EF4444; font-weight:bold; font-size:18px;'>❌ Risposta Errata</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Riprova", type="secondary"):
                st.session_state.quiz_answered = False
                st.rerun()

# Footer
st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #4B5563; font-size: 10px;'>Singularity OS V16 | {_('auth_btn')} | Edu Mode: {st.session_state.edu_mode}</div>", unsafe_allow_html=True)
