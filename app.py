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

# Auth Mock
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<h2 style='text-align: center; color: #3B82F6;'>💠 SINGULARITY OS</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Identificazione Biometrica / Hardware Key Richiesta</p>", unsafe_allow_html=True)
        pwd = st.text_input("Inserisci Chiave Crittografica (Scrivi 'admin')", type="password")
        if st.button("Decripta Terminale"):
            if pwd == "admin": 
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Accesso Negato.")
    st.stop()

# ==========================================
# 2. CORE DATA ENGINE (Vettorizzato)
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def generate_singularity_data():
    np.random.seed(42)
    days = 500
    dates = pd.date_range(end=datetime.date.today(), periods=days)
    
    # Prezzi con Hawkes Process Proxy (Clustering di Volatilità)
    base_drift = 0.0001
    prices = np.zeros(days); prices[0] = 50
    vol = np.zeros(days); vol[0] = 0.02
    
    for i in range(1, days):
        # Autoeccitazione della volatilità (Hawkes-like)
        vol[i] = 0.02 + 0.8 * vol[i-1] + np.random.exponential(0.005) if np.random.rand() > 0.9 else 0.02 + 0.95 * vol[i-1]
        prices[i] = prices[i-1] * np.exp((base_drift - 0.5*vol[i]**2) + vol[i]*np.random.normal())
        
    df = pd.DataFrame({'Power_EUR': prices}, index=dates)
    df['Returns'] = df['Power_EUR'].pct_change().fillna(0)
    df['Gas_USD'] = 15 + df['Power_CH']*0.15 if 'Power_CH' in df else 15 + df['Power_EUR']*0.15 + np.random.normal(0,1,days)
    df['EUR_USD'] = 1.05 + np.cumsum(np.random.normal(0, 0.001, days))
    df['CO2_EUA'] = 80 + np.cumsum(np.random.normal(0.02, 0.5, days))
    df['Wind_Speed_ms'] = weibull_min.rvs(2, loc=0, scale=8, size=days) # Distribuzione Weibull vento
    df['Sentiment_NLP'] = np.clip(np.random.normal(0.1, 0.4, days), -1, 1)
    return df

df = generate_singularity_data()
ult = df.iloc[-1]

# Inizializzazione Chat LLM
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistema Quantitativo Operativo. Come posso assisterti nell'ottimizzazione del portafoglio oggi?"}]

# ==========================================
# 3. ARCHITETTURA A MODULI (SIDEBAR WORKSPACES)
# ==========================================
with st.sidebar:
    st.markdown("<h2>💠 SINGULARITY</h2>", unsafe_allow_html=True)
    st.markdown("*Quantitative Global Macro System*")
    st.markdown("---")
    
    workspace = st.radio("🏢 WORKSPACES", [
        "🤖 Autonomous AI & MARL",
        "🌍 Climate & Grid Intel",
        "📈 Exotics & Structuring",
        "🏛️ Enterprise Risk & XVA"
    ])
    
    st.markdown("---")
    st.markdown("### 💬 Copilot Quant LLM")
    for msg in st.session_state.messages:
        st.markdown(f"<div class='chat-msg'><b>{msg['role'].upper()}:</b> {msg['content']}</div>", unsafe_allow_html=True)
    
    if prompt := st.chat_input("Chiedi all'AI (Es: 'Analizza VaR')"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Risposte fittizie del LLM
        reply = f"Elaborazione di '{prompt}'. Il modello indica una correlazione inversa forte oggi. Suggerisco Delta Hedging dinamico."
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

# Funzione Helper per le Metriche
def render_kpi(title, value, col):
    col.markdown(f"<div class='metric-container'><div class='metric-label'>{title}</div><div class='metric-val'>{value}</div></div>", unsafe_allow_html=True)

# ==========================================
# WORKSPACE 1: AUTONOMOUS AI & MARL
# ==========================================
if workspace == "🤖 Autonomous AI & MARL":
    st.title("🤖 Multi-Agent Reinforcement Learning (MARL)")
    st.write("Monitoraggio degli agenti AI che operano in modo autonomo tramite Q-Learning e reti neurali profonde.")
    
    c1, c2, c3, c4 = st.columns(4)
    render_kpi("Stato Agente Primario", "🟢 ACTIVE (Live)", c1)
    render_kpi("Reward (Sharpe Cumulativo)", "2.84", c2)
    render_kpi("Flash Crash Probability", f"{np.random.uniform(0.1, 5.0):.1f}%", c3)
    render_kpi("NLP Trade Sentiment", f"{ult['Sentiment_NLP']:.2f}", c4)
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("### PnL Learning Curve (Epoche di Addestramento)")
        epoches = np.arange(1000)
        # Curva logaritmica tipica del Reinforcement Learning
        reward_curve = -50 + 100 * np.log(epoches + 1) / np.log(1000) + np.random.normal(0, 5, 1000)
        fig_rl = px.line(x=epoches, y=reward_curve, title="Reward Function dell'Agente (Max Sharpe Ratio)")
        fig_rl.update_layout(template="plotly_dark", xaxis_title="Epoche (Simulazioni)", yaxis_title="Cumulative Reward")
        st.plotly_chart(fig_rl, use_container_width=True)
        
    with col_b:
        st.markdown("### Regime Switching (HMM)")
        regime = "BULLISH (Risk-On)" if ult['Sentiment_NLP'] > 0 else "BEARISH (Risk-Off)"
        color = "green" if regime == "BULLISH (Risk-On)" else "red"
        st.markdown(f"<h3 style='color:{color}; text-align:center;'>{regime}</h3>", unsafe_allow_html=True)
        st.write("**Stat Arb Z-Score:** +2.4 (Cointegrazione Gas-Power tesa, l'agente sta shortando lo spread).")
        
        st.markdown("#### Routing Latency (HFT)")
        heatmap_lat = np.random.normal(1.5, 0.2, (5, 5)) # Latenza in millisecondi per 5 exchange e 5 gateway
        fig_lat = px.imshow(heatmap_lat, color_continuous_scale="RdYlGn_r", title="Latenza Gateway (ms)")
        fig_lat.update_layout(template="plotly_dark", height=200, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_lat, use_container_width=True)
        
    st.button("📥 Esporta Pesi Rete Neurale (PyTorch .pt)")

# ==========================================
# WORKSPACE 2: CLIMATE & GRID INTEL
# ==========================================
elif workspace == "🌍 Climate & Grid Intel":
    st.title("🌍 Geospatial Climate Intelligence & Grid Physics")
    
    c1, c2, c3, c4 = st.columns(4)
    enso = np.random.uniform(-1.5, 1.5)
    enso_state = "El Niño (Mite)" if enso > 0.5 else ("La Niña (Freddo)" if enso < -0.5 else "Neutro")
    render_kpi("ENSO Index (Pacifico)", f"{enso:.2f} ({enso_state})", c1)
    render_kpi("Polar Vortex Strength", "Forte (Stabile)", c2)
    render_kpi("Grid Inertia Index", "CRITICO (Bassa)", c3)
    render_kpi("Dynamic Line Rating", "+15% Capacità", c4)
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.markdown("### Wind Power Curve (Weibull Dist.)")
        wind_speeds = np.linspace(0, 25, 100)
        # Curva di potenza tipica di una turbina eolica
        power = np.where(wind_speeds < 3, 0, np.where(wind_speeds <= 12, (wind_speeds-3)**3 * 10, np.where(wind_speeds <= 25, 3000, 0)))
        fig_wind = go.Figure()
        fig_wind.add_trace(go.Scatter(x=wind_speeds, y=power, fill='tozeroy', name="MW Output", line=dict(color="#10B981")))
        fig_wind.update_layout(template="plotly_dark", title="Produzione Eolica Teorica vs Velocità Vento", xaxis_title="m/s", yaxis_title="MW")
        st.plotly_chart(fig_wind, use_container_width=True)
        
    with col_w2:
        st.markdown("### Hydro Reservoir 3D Surface")
        # Superficie 3D fittizia di un bacino alpino
        X, Y = np.meshgrid(np.linspace(-5, 5, 30), np.linspace(-5, 5, 30))
        Z = np.sin(np.sqrt(X**2 + Y**2)) * 100 + 500 # Topografia
        fig_hydro = go.Figure(data=[go.Surface(z=Z, colorscale="Blues")])
        fig_hydro.update_layout(template="plotly_dark", height=400, title="Livello Invaso Idroelettrico (Markov Forecast)", margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_hydro, use_container_width=True)

# ==========================================
# WORKSPACE 3: EXOTICS & STRUCTURING
# ==========================================
elif workspace == "📈 Exotics & Structuring":
    st.title("📈 Exotic Derivatives, SABR & Curve Structuring")
    
    c1, c2, c3 = st.columns(3)
    render_kpi("SABR Alpha (Vol)", "0.354", c1)
    render_kpi("SABR Beta (Skew)", "0.500", c2)
    render_kpi("Quanto Correlation (ρ)", "-0.45", c3)
    
    col_e1, col_e2 = st.columns([1.5, 1])
    with col_e1:
        st.markdown("### SABR Model Volatility Smile")
        # Generazione Smile approssimata per opzioni su commodities
        strikes = np.linspace(30, 150, 40)
        F = 80
        # Formula semplificata visiva
        smile = 0.4 + 0.0001 * (strikes - F)**2 - 0.002 * (strikes - F)
        fig_sabr = px.line(x=strikes, y=smile*100, title="SABR Implied Volatility Surface Slice")
        fig_sabr.add_vline(x=F, line_dash="dash", line_color="red", annotation_text="Forward (ATM)")
        fig_sabr.update_layout(template="plotly_dark", yaxis_title="Implied Vol (%)", xaxis_title="Strike Price (€/MWh)")
        st.plotly_chart(fig_sabr, use_container_width=True)
        
    with col_e2:
        st.markdown("### Exotic Pricer")
        st.write("**Opzione Quanto (Gas USD pagato in EUR)**")
        S = ult['Gas_USD']
        FX = ult['EUR_USD']
        rho = -0.45 # Correlazione
        vol_S, vol_FX = 0.4, 0.1
        quanto_drift_adj = -rho * vol_S * vol_FX
        
        # Black Scholes modificato (Formula semplificata)
        T = 0.5
        d1 = (np.log(S/80) + (0.02 + quanto_drift_adj + 0.5*vol_S**2)*T) / (vol_S*np.sqrt(T))
        d2 = d1 - vol_S*np.sqrt(T)
        quanto_call = S * np.exp(quanto_drift_adj*T) * norm.cdf(d1) - 80 * np.exp(-0.02*T) * norm.cdf(d2)
        
        st.metric("Quanto Call (Strike 80)", f"€ {quanto_call * FX:.2f} (in EUR)")
        
        st.markdown("---")
        st.markdown("#### Greche di Terzo Ordine")
        st.write("🚀 **Speed (dGamma/dSpot):** -0.0014")
        st.write("🎨 **Color (dGamma/dTime):** +0.0251")
        st.write("🌪️ **Zomma (dGamma/dVol):** +0.1042")

# ==========================================
# WORKSPACE 4: ENTERPRISE RISK & XVA
# ==========================================
elif workspace == "🏛️ Enterprise Risk & XVA":
    st.title("🏛️ Regulatory Capital (FRTB) & XVA Desk")
    
    st.error("🚨 **SIMM MARGIN BREACH WARNING:** Probabilità 84% di Margin Call su ICE Endex domani.")
    
    c1, c2, c3, c4 = st.columns(4)
    render_kpi("FRTB Expected Shortfall", "€ 45.2 M", c1)
    render_kpi("CVA (Rischio Default Cpty)", "€ 2.1 M", c2)
    render_kpi("DVA (Nostro Beneficio)", "€ 0.5 M", c3)
    render_kpi("ESG Penalty Score", "12 / 100", c4)
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("### Liquidity Horizon Risk (FRTB)")
        st.write("Il capitale regolamentare scala in base al tempo necessario per smontare le posizioni in caso di crisi.")
        horizons = pd.DataFrame({
            "Asset Class": ["Power (Spot)", "Gas (Prompt)", "Coal (API2)", "Carbon (EUA)"],
            "Liquidity Horizon": ["10 Giorni", "10 Giorni", "20 Giorni", "10 Giorni"],
            "Capital Charge": [15.2, 18.5, 8.4, 3.1]
        })
        fig_frtb = px.bar(horizons, x="Asset Class", y="Capital Charge", color="Liquidity Horizon", title="Assorbimento Capitale per Liquidity Horizon (M€)")
        fig_frtb.update_layout(template="plotly_dark")
        st.plotly_chart(fig_frtb, use_container_width=True)
        
    with col_r2:
        st.markdown("### Wrong-Way Risk (WWR) Monitor")
        st.write("Rischio che la probabilità di default (PD) della controparte aumenti proprio quando l'esposizione (EAD) è massima a nostro favore.")
        
        # Scatter plot proxy per il WWR
        ead = np.random.lognormal(mean=2, sigma=0.5, size=100)
        pd_cpty = 0.01 + ead * 0.002 + np.random.normal(0, 0.01, 100) # Correlazione positiva tra PD ed EAD
        fig_wwr = px.scatter(x=ead, y=pd_cpty, labels={'x':'Exposure at Default (M€)', 'y':'Probability of Default (%)'}, title="Correlazione WWR (Portafoglio OTC)")
        fig_wwr.update_layout(template="plotly_dark")
        st.plotly_chart(fig_wwr, use_container_width=True)

# Footer Enterprise
st.markdown("---")
st.markdown("<div style='text-align: center; color: #4B5563; font-size: 10px; font-family: monospace;'>"
            "Singularity OS V15 | Compiled with Numba/Cython Hooks | AGI-Assisted Quant Terminal"
            "</div>", unsafe_allow_html=True)
