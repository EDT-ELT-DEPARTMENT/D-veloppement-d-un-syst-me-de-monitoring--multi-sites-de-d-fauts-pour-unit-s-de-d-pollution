import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta

# ==========================================
# Configuration de la page
# ==========================================
st.set_page_config(
    page_title="Monitoring Industriel | Supervision", 
    page_icon="🏭", 
    layout="wide"
)

# ==========================================
# Fonctions de simulation de données
# ==========================================
def get_sensor_data(site_type, points=50):
    """
    Génère des données de simulation pour les capteurs industriels.
    Dans une version de production, cette fonction sera remplacée par 
    une requête vers votre base de données ou votre flux MQTT.
    """
    times = [datetime.now() - timedelta(minutes=i) for i in range(points, 0, -1)]
    
    if site_type == "Cimenterie":
        tension = np.random.normal(50, 2, points)
        courant = np.random.normal(800, 50, points)
        poussieres = np.random.normal(15, 3, points)
        return pd.DataFrame({
            "Heure": times, 
            "Tension_kV": tension, 
            "Courant_mA": courant, 
            "Poussieres_mg": poussieres
        })
        
    elif site_type == "Installation Pétrolière":
        debit_gaz = np.random.normal(15000, 500, points)
        so2 = np.random.normal(45, 5, points)
        nox = np.random.normal(180, 10, points)
        return pd.DataFrame({
            "Heure": times, 
            "Debit_m3h": debit_gaz, 
            "SO2_mg": so2, 
            "NOx_mg": nox
        })

# ==========================================
# Interface Utilisateur (Sidebar)
# ==========================================
st.sidebar.title("Paramètres de Monitoring")
site_selection = st.sidebar.selectbox(
    "Sélectionnez le site à surveiller :", 
    ["Cimenterie", "Installation Pétrolière"]
)
auto_refresh = st.sidebar.checkbox("Activer le rafraîchissement temps réel", value=False)

st.title(f"Supervision de l'Unité de Dépollution : {site_selection}")
st.markdown("---")

# ==========================================
# Logique d'affichage par site
# ==========================================

# Cas 1 : Cimenterie
if site_selection == "Cimenterie":
    st.subheader("État de l'Électrofiltre (Filtre à particules)")
    
    # Récupération des données
    df = get_sensor_data("Cimenterie")
    latest = df.iloc[-1]
    
    # Affichage des KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Tension Haute Tension", f"{latest['Tension_kV']:.1f} kV")
    col2.metric("Courant de Décharge", f"{latest['Courant_mA']:.0f} mA")
    col3.metric("Émission Particules Fines", f"{latest['Poussieres_mg']:.1f} mg/Nm³")
    
    # Visualisation
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Heure"], y=df["Poussieres_mg"], mode='lines+markers', name='Poussières (mg/Nm³)', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=df["Heure"], y=df["Tension_kV"], mode='lines', name='Tension (kV)', line=dict(color='blue', dash='dot')))
    fig.update_layout(title="Évolution des paramètres opératoires et des rejets", xaxis_title="Temps", yaxis_title="Valeurs", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# Cas 2 : Installation Pétrolière
elif site_selection == "Installation Pétrolière":
    st.subheader("Unité de Traitement des Gaz (Désulfuration & DeNOx)")
    
    # Récupération des données
    df = get_sensor_data("Installation Pétrolière")
    latest = df.iloc[-1]
    
    # Affichage des KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Débit des Gaz", f"{latest['Debit_m3h']:.0f} m³/h")
    col2.metric("Émission SO2", f"{latest['SO2_mg']:.1f} mg/Nm³")
    col3.metric("Émission NOx", f"{latest['NOx_mg']:.1f} mg/Nm³")
    
    # Visualisation
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Heure"], y=df["SO2_mg"], mode='lines', fill='tozeroy', name='SO2 (mg/Nm³)', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df["Heure"], y=df["NOx_mg"], mode='lines', name='NOx (mg/Nm³)', line=dict(color='purple')))
    fig.update_layout(title="Surveillance des émissions gazeuses continues", xaxis_title="Temps", yaxis_title="Concentration (mg/Nm³)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# Logique de rafraîchissement automatique
# ==========================================
if auto_refresh:
    time.sleep(2) 
    st.rerun()
