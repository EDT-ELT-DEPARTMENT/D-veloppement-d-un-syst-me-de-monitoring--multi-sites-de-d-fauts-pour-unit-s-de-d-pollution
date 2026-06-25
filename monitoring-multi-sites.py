import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime

# ==============================================================================
# CONFIGURATION DE LA PLATEFORME
# ==============================================================================
st.set_page_config(
    page_title="Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA", 
    layout="wide",
    page_icon="⚠️"
)

st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")
st.subheader("Module : Monitoring Industriel et Sécurité Gaz")
st.markdown("---")

# Initialisation de l'historique
if 'data_history' not in st.session_state:
    st.session_state.data_history = pd.DataFrame(columns=["Temps", "Tension", "CO", "Courant"])

# Modèles mathématiques
V_ref = np.array([2.0, 4.0, 6.0, 8.0, 10.0])
CO_ref = np.array([800.0, 780.0, 700.0, 650.0, 480.0])
I_ref = np.array([0.48, 1.87, 5.20, 8.90, 10.45])
model_co = np.poly1d(np.polyfit(V_ref, CO_ref, 2))
model_i = np.poly1d(np.polyfit(V_ref, I_ref, 2))

# ==============================================================================
# SIDEBAR
# ==============================================================================
st.sidebar.header("Paramètres")
v_consigne = st.sidebar.slider("Tension (kV)", 2.0, 12.0, 8.0, 0.1)
active_monitoring = st.sidebar.checkbox("Démarrer le monitoring", value=False)

if active_monitoring:
    tension_inst = v_consigne * (1 + np.random.uniform(-0.02, 0.02))
    co_inst = max(0, model_co(tension_inst))
    i_inst = max(0, model_i(tension_inst))
    
    new_data = {"Temps": datetime.now().strftime("%H:%M:%S"), "Tension": tension_inst, "CO": co_inst, "Courant": i_inst}
    st.session_state.data_history = pd.concat([st.session_state.data_history, pd.DataFrame([new_data])], ignore_index=True)
    if len(st.session_state.data_history) > 50: st.session_state.data_history = st.session_state.data_history.iloc[-50:]

val_co = st.session_state.data_history["CO"].iloc[-1] if not st.session_state.data_history.empty else 0
val_i = st.session_state.data_history["Courant"].iloc[-1] if not st.session_state.data_history.empty else 0

# ==============================================================================
# AFFICHAGE DU TABLEAU DES RISQUES (DONNÉES UTILISATEUR)
# ==============================================================================
col_data, col_gauge = st.columns([1, 1])

with col_data:
    st.subheader("⚠️ Évaluation du Risque Humain")
    data_toxicite = {
        "Concentration (ppm)": ["< 50", "100 - 200", "400 - 600", "800"],
        "Risque / Effet sur la santé": [
            "Seuil limite d'exposition moyenne (8 heures).",
            "Risque modéré : maux de tête, vertiges, essoufflement.",
            "Danger grave : malaise, confusion mentale après 1h.",
            "Mortel : perte de connaissance en moins de 1h, décès en 2-3h."
        ]
    }
    st.table(pd.DataFrame(data_toxicite))

with col_gauge:
    st.subheader("Jauge de Toxicité (ppm)")
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = val_co,
        gauge = {
            'axis': {'range': [0, 1000]},
            'steps': [
                {'range': [0, 50], 'color': "green"},
                {'range': [50, 100], 'color': "lightgreen"},
                {'range': [100, 200], 'color': "yellow"},
                {'range': [200, 400], 'color': "orange"},
                {'range': [400, 600], 'color': "red"},
                {'range': [600, 1000], 'color': "darkred"}
            ]
        }
    ))
    fig_gauge.update_layout(height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)

# ==============================================================================
# RISQUE D'EXPLOSION
# ==============================================================================
risque_expl = (val_co / 125000) * 100

st.subheader("Évaluation du Risque d'Explosion")
if risque_expl < 0.5:
    couleur_exp = "#2ecc71"
    txt_exp = "Risque Négligeable (LIE < 0.5%)"
elif risque_expl < 1.0:
    couleur_exp = "#f1c40f"
    txt_exp = "Risque Faible"
else:
    couleur_exp = "#e74c3c"
    txt_exp = "DANGER IMMÉDIAT"

st.markdown(f"""
<div style="background-color: {couleur_exp}; padding: 20px; border-radius: 10px; color: white; text-align: center;">
    <h2 style="color: white;">{txt_exp}</h2>
    <p>Niveau actuel : {risque_expl:.4f}% de la Limite Inférieure d'Explosivité</p>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# RAFRAÎCHISSEMENT
# ==============================================================================
if active_monitoring:
    time.sleep(0.5) 
    st.rerun()
