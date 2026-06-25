import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta

# ==========================================
# Configuration de la page
# ==========================================
st.set_page_config(page_title="Monitoring Multi-Sites | Dépollution", page_icon="🏭", layout="wide")

# ==========================================
# Fonctions de simulation de données (Remplacer par flux MQTT/IoT)
# ==========================================
def generate_sensor_data(site_type, points=50):
    """Simule les données des capteurs pour les unités de dépollution."""
    times = [datetime.now() - timedelta(minutes=i) for i in range(points, 0, -1)]
    
    if site_type == "Cimenterie":
        # Paramètres pour un électrofiltre et émissions
        tension = np.random.normal(50, 2, points) # kV
        courant = np.random.normal(800, 50, points) # mA
        poussieres = np.random.normal(15, 3, points) # mg/Nm3 (Limite ~20)
        return pd.DataFrame({"Heure": times, "Tension_kV": tension, "Courant_mA": courant, "Poussieres_mg": poussieres})
        
    elif site_type == "Installation Pétrolière":
        # Paramètres pour une unité de désulfuration / laveur de gaz
        debit_gaz = np.random.normal(15000, 500, points) # m3/h
        so2 = np.random.normal(45, 5, points) # mg/Nm3 (Limite ~50)
        nox = np.random.normal(180, 10, points) # mg/Nm3 (Limite ~200)
        return pd.DataFrame({"Heure": times, "Debit_m3h": debit_gaz, "SO2_mg": so2, "NOx_mg": nox})

# ==========================================
# Interface Utilisateur (Sidebar)
# ==========================================
st.sidebar.title("Paramètres de Monitoring")
site_selection = st.sidebar.selectbox("Sélectionnez le site à surveiller :", ["Cimenterie", "Installation Pétrolière"])
auto_refresh = st.sidebar.checkbox("Activer le rafraîchissement temps réel", value=False)

st.title(f"Supervision de l'Unité de Dépollution : {site_selection}")
st.markdown("---")

# ==========================================
# Affichage Cimenterie
# ==========================================
if site_selection == "Cimenterie":
    st.subheader("État de l'Électrofiltre (Filtre à particules)")
    
    # Génération des données
    df = generate_sensor_data("Cimenterie")
    latest = df.iloc[-1]
    
    # Métriques principales (KPIs)
    col1, col2, col3 = st.columns(3)
    col1.metric("Tension Haute Tension", f"{latest['Tension_kV']:.1f} kV", delta="-0.5 kV" if latest['Tension_kV'] < 48 else "OK", delta_color="inverse")
    col2.metric("Courant de Décharge", f"{latest['Courant_mA']:.0f} mA")
    col3.metric("Émission Particules Fines", f"{latest['Poussieres_mg']:.1f} mg/Nm³", delta="+2.1 mg" if latest['Poussieres_mg'] > 18 else "-0.3 mg", delta_color="inverse")
    
    # Graphique d'évolution
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Heure"], y=df["Poussieres_mg"], mode='lines+markers', name='Poussières (mg/Nm³)', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=df["Heure"], y=df["Tension_kV"], mode='lines', name='Tension (kV)', line=dict(color='blue', dash='dot')))
    fig.update_layout(title="Évolution des paramètres opératoires et des rejets", xaxis_title="Temps", yaxis_title="Valeurs", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# Affichage Installation Pétrolière
# ==========================================
elif site_selection == "Installation Pétrolière":
    st.subheader("Unité de Traitement des Gaz (Désulfuration & DeNOx)")
    
    # Génération des données
    df = generate_sensor_data("Installation Pétrolière")
    latest = df.iloc[-1]
    
    # Métriques principales (KPIs)
    col1, col2, col3 = st.columns(3)
    col1.metric("Débit des Gaz", f"{latest['Debit_m3h']:.0f} m³/h")
    col2.metric("Émission SO2", f"{latest['SO2_mg']:.1f} mg/Nm³", delta="Alerte Haute" if latest['SO2_mg'] > 48 else "Normale", delta_color="inverse")
    col3.metric("Émission NOx", f"{latest['NOx_mg']:.1f} mg/Nm³")
    
    # Graphique d'évolution
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Heure"], y=df["SO2_mg"], mode='lines', fill='tozeroy', name='SO2 (mg/Nm³)', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df["Heure"], y=df["NOx_mg"], mode='lines', name='NOx (mg/Nm³)', line=dict(color='purple')))
    fig.update_layout(title="Surveillance des émissions gazeuses continues", xaxis_title="Temps", yaxis_title="Concentration (mg/Nm³)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# Logique de rafraîchissement
# ==========================================
if auto_refresh:
    time.sleep(2) # Simule un délai de réception MQTT
    st.rerun()
