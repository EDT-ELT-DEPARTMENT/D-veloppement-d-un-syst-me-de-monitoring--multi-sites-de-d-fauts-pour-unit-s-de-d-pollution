import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta

# ==============================================================================
# CONFIGURATION DE LA PLATEFORME
# ==============================================================================
st.set_page_config(
    page_title="Monitoring Sécurité CO", 
    page_icon="⚠️", 
    layout="wide"
)

# ==============================================================================
# GÉNÉRATION DES DONNÉES (Simulation Temps Réel)
# ==============================================================================
def get_sensor_data(site_type, points=50):
    """Génère des données centrées sur la sécurité : Tension, Courant, CO."""
    times = [datetime.now() - timedelta(minutes=i) for i in range(points, 0, -1)]
    
    if site_type == "Cimenterie":
        # Paramètres pour Cimenterie (Filtrage électrostatique)
        tension = np.random.normal(50, 2, points)      # kV
        courant = np.random.normal(800, 50, points)    # mA
        co_ppm = np.random.normal(25, 2, points)       # ppm (Concentration CO)
        
    else: # Installation Pétrolière
        # Paramètres pour Pétrolier (Réacteur Plasma)
        tension = np.random.normal(7, 1.5, points)     # kV
        courant = np.random.normal(6, 2, points)       # mA
        co_ppm = np.random.normal(600, 50, points)     # ppm (Concentration CO)
        
    return pd.DataFrame({
        "Heure": times,
        "Tension_kV": tension,
        "Courant_mA": courant,
        "CO_ppm": co_ppm
    })

# ==============================================================================
# INTERFACE UTILISATEUR
# ==============================================================================
st.title("Supervision Sécurité Gaz : Monitoring du CO")
st.markdown("---")

# Sidebar
st.sidebar.title("Paramètres de Monitoring")
site_selection = st.sidebar.selectbox(
    "Sélectionnez le site à surveiller :", 
    ["Cimenterie", "Installation Pétrolière"]
)
auto_refresh = st.sidebar.checkbox("Activer le rafraîchissement temps réel", value=False)

# Récupération des données
df = get_sensor_data(site_selection)
latest = df.iloc[-1]

# ==============================================================================
# KPIs (Indicateurs de Performance)
# ==============================================================================
st.subheader(f"État actuel : {site_selection}")

# Affichage des 3 métriques critiques
col1, col2, col3 = st.columns(3)
col1.metric("Tension Appliquée", f"{latest['Tension_kV']:.1f} kV")
col2.metric("Courant de Décharge", f"{latest['Courant_mA']:.1f} mA")
col3.metric("Concentration CO", f"{latest['CO_ppm']:.1f} ppm", delta="ALERTE" if latest['CO_ppm'] > 750 else "Normal", delta_color="inverse")

# ==============================================================================
# VISUALISATION GRAPHIQUE
# ==============================================================================
st.markdown("### Analyse de l'évolution du CO")

fig = go.Figure()

# Courbe CO
fig.add_trace(go.Scatter(
    x=df["Heure"], 
    y=df["CO_ppm"], 
    mode='lines', 
    name='Concentration CO (ppm)', 
    line=dict(color='red', width=3)
))

# Axes secondaires pour la tension et le courant (si besoin de corrélation)
fig.update_layout(
    title="Évolution de la concentration de CO (Risque Explosif)",
    xaxis_title="Temps",
    yaxis_title="Concentration CO (ppm)",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

# Graphique de corrélation Tension/Courant
fig_corr = go.Figure()
fig_corr.add_trace(go.Scatter(x=df["Tension_kV"], y=df["Courant_mA"], mode='markers', name='Corrélation I-V'))
fig_corr.update_layout(
    title="Corrélation Tension (kV) / Courant (mA)",
    xaxis_title="Tension (kV)",
    yaxis_title="Courant (mA)",
    template="plotly_white"
)
st.plotly_chart(fig_corr, use_container_width=True)

# ==============================================================================
# RAFRAÎCHISSEMENT
# ==============================================================================
if auto_refresh:
    time.sleep(2) 
    st.rerun()
