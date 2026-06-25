import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import time
from datetime import datetime
# Masquer les éléments du menu supérieur (Share, Star, Edit, etc.)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stAppDeployButton {display:none;}
            #stDecoration {display:none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
# ==============================================================================
# CONFIGURATION DE LA PLATEFORME
# ==============================================================================
st.set_page_config(
    page_title="Plateforme de Monitoring Multi-Sites", 
    layout="wide",
    page_icon="⚡"
)

st.title("Plateforme de Monitoring Multi-Sites et de Diagnostic de Défauts pour Unités de Dépollution Atmosphérique")
st.markdown("---")

# ==============================================================================
# INITIALISATION DES DONNÉES (Session State)
# ==============================================================================
if 'data_history' not in st.session_state:
    st.session_state.data_history = pd.DataFrame(columns=["Temps", "Tension", "CO", "Courant"])

# Modèles mathématiques basés sur les données réelles
V_ref = np.array([2.0, 4.0, 6.0, 8.0, 10.0])
CO_ref = np.array([800.0, 780.0, 700.0, 650.0, 480.0])
I_ref = np.array([0.48, 1.87, 5.20, 8.90, 10.45])

model_co = np.poly1d(np.polyfit(V_ref, CO_ref, 2))
model_i = np.poly1d(np.polyfit(V_ref, I_ref, 2))

# ==============================================================================
# BARRE LATÉRALE DE CONTRÔLE
# ==============================================================================
st.sidebar.header("Paramètres de Contrôle")
v_consigne = st.sidebar.slider("Tension de consigne (kV)", 2.0, 12.0, 8.0, 0.1)
active_monitoring = st.sidebar.checkbox("Démarrer le monitoring en temps réel", value=False)

# ==============================================================================
# LOGIQUE DE SIMULATION DYNAMIQUE
# ==============================================================================
if active_monitoring:
    fluctuation = np.random.uniform(-0.02, 0.02)
    tension_instantanee = v_consigne * (1 + fluctuation)
    co_instantane = max(0, model_co(tension_instantanee))
    i_instantane = max(0, model_i(tension_instantanee))
    
    new_data = {
        "Temps": datetime.now().strftime("%H:%M:%S"),
        "Tension": tension_instantanee,
        "CO": co_instantane,
        "Courant": i_instantane
    }
    
    st.session_state.data_history = pd.concat([st.session_state.data_history, pd.DataFrame([new_data])], ignore_index=True)
    if len(st.session_state.data_history) > 50:
        st.session_state.data_history = st.session_state.data_history.iloc[-50:]

# ==============================================================================
# RÉCUPÉRATION DES VALEURS ACTUELLES
# ==============================================================================
if not st.session_state.data_history.empty:
    val_co = st.session_state.data_history["CO"].iloc[-1]
    val_i = st.session_state.data_history["Courant"].iloc[-1]
    val_v = st.session_state.data_history["Tension"].iloc[-1]
else:
    val_co, val_i, val_v = 0, 0, v_consigne

# ==============================================================================
# LIGNE 1 : INDICATEURS NUMÉRIQUES
# ==============================================================================
col1, col2, col3 = st.columns(3)
col1.metric("Concentration CO", f"{val_co:.1f} ppm")
col2.metric("Courant de décharge", f"{val_i:.2f} mA")
col3.metric("Tension actuelle", f"{val_v:.2f} kV")

st.markdown("---")

# ==============================================================================
# LIGNE 2 : RISQUE HUMAIN ET JAUGE
# ==============================================================================
col_data, col_gauge = st.columns([1, 1])

with col_data:
    st.subheader("⚠️ Évaluation du Risque pour l'Être Humain")
    st.table(pd.DataFrame({
        "Concentration (ppm)": ["< 50", "100 - 200", "400 - 600", "800"],
        "Risque / Effet sur la santé": [
            "Seuil limite d'exposition moyenne (8 heures).",
            "Risque modéré : maux de tête, vertiges, essoufflement.",
            "Danger grave : malaise, confusion mentale après 1h.",
            "Mortel : perte de connaissance en moins de 1h, décès en 2-3h."
        ]
    }))

with col_gauge:
    st.subheader("Jauge de Toxicité (ppm)")
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = val_co,
        gauge = {'axis': {'range': [0, 1000]}, 'steps': [
                {'range': [0, 50], 'color': "green"}, {'range': [50, 100], 'color': "lightgreen"},
                {'range': [100, 200], 'color': "yellow"}, {'range': [200, 400], 'color': "orange"},
                {'range': [400, 600], 'color': "red"}, {'range': [600, 1000], 'color': "darkred"}
            ]}
    ))
    fig_gauge.update_layout(height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)

# ==============================================================================
# LIGNE 3 : RISQUE D'EXPLOSION ET SIMULATION COAXIALE
# ==============================================================================
col_expl, col_field = st.columns([1, 1])

with col_expl:
    st.subheader("Évaluation du Risque d'Explosion")
    risque_expl = (val_co / 125000) * 100
    color = "#e74c3c" if risque_expl >= 1.0 else ("#f1c40f" if risque_expl >= 0.5 else "#2ecc71")
    st.markdown(f"""
    <div style="background-color: {color}; padding: 20px; border-radius: 10px; color: white; text-align: center;">
        <h2 style="color: white;">{'DANGER' if risque_expl >= 1 else 'SÉCURISÉ'}</h2>
        <p>Taux de LIE atteint : {risque_expl:.4f}%</p>
    </div>
    """, unsafe_allow_html=True)

with col_field:
    st.subheader("Simulation Champ Électrique (Fil-Cylindre)")
    # Simulation géométrie coaxiale
    R, r0 = 50.0, 0.05 # mm
    # Création d'une coupe transversale
    x = np.linspace(-R, R, 200)
    y = np.linspace(-R, R, 200)
    X, Y = np.meshgrid(x, y)
    r = np.sqrt(X**2 + Y**2)
    # Champ électrique E = V / (r * ln(R/r0))
    # On normalise avec V=1 pour visualiser la distribution
    E = 1 / (r * np.log(R/r0))
    E[r < r0] = np.nan # Cœur du fil
    
    fig, ax = plt.subplots(figsize=(6, 6))
    contour = ax.contourf(X, Y, E, levels=50, cmap='plasma')
    circle = plt.Circle((0, 0), R, color='black', fill=False, linewidth=3)
    ax.add_artist(circle)
    ax.scatter(0, 0, color='white', s=20)
    ax.set_title(f"Coupe transversale (R={R}mm, r0={r0}mm)")
    plt.colorbar(contour, label='Intensité relative du champ')
    st.pyplot(fig)

# ==============================================================================
# LIGNE 4 : COURBES HISTORIQUES
# ==============================================================================
st.markdown("---")
col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    st.subheader("Historique Concentration CO (ppm)")
    fig_co = go.Figure()
    if not st.session_state.data_history.empty:
        fig_co.add_trace(go.Scatter(
            x=st.session_state.data_history["Temps"], 
            y=st.session_state.data_history["CO"], 
            mode='lines', name='CO (ppm)', line=dict(color='red', width=3)
        ))
    fig_co.update_layout(yaxis_range=[0, 1000], template="plotly_white")
    st.plotly_chart(fig_co, use_container_width=True, key="co_chart_dynamic")

with col_graph2:
    st.subheader("Historique Courant (mA)")
    fig_i = go.Figure()
    if not st.session_state.data_history.empty:
        fig_i.add_trace(go.Scatter(
            x=st.session_state.data_history["Temps"], 
            y=st.session_state.data_history["Courant"], 
            mode='lines', name='I (mA)', line=dict(color='orange', width=3)
        ))
    fig_i.update_layout(yaxis_range=[0, 15], template="plotly_white")
    st.plotly_chart(fig_i, use_container_width=True, key="current_chart_dynamic")

if active_monitoring:
    time.sleep(0.1) # Réduit à 0.1s pour plus de fluidité
    st.rerun()
