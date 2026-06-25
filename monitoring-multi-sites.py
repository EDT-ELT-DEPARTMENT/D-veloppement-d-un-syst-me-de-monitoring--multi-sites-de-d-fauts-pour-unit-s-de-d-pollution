import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime

# ==============================================================================
# CONFIGURATION ET INITIALISATION
# ==============================================================================
st.set_page_config(page_title="Monitoring Sécurité", layout="wide")

st.title("Tableau de Bord : Sécurité Gaz et Risques")
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

# Logique dynamique
if active_monitoring:
    tension_inst = v_consigne * (1 + np.random.uniform(-0.02, 0.02))
    co_inst = max(0, model_co(tension_inst))
    i_inst = max(0, model_i(tension_inst))
    
    new_data = {"Temps": datetime.now().strftime("%H:%M:%S"), "Tension": tension_inst, "CO": co_inst, "Courant": i_inst}
    st.session_state.data_history = pd.concat([st.session_state.data_history, pd.DataFrame([new_data])], ignore_index=True)
    if len(st.session_state.data_history) > 50: st.session_state.data_history = st.session_state.data_history.iloc[-50:]

# ==============================================================================
# LOGIQUE D'AFFICHAGE
# ==============================================================================
val_co = st.session_state.data_history["CO"].iloc[-1] if not st.session_state.data_history.empty else 0
val_i = st.session_state.data_history["Courant"].iloc[-1] if not st.session_state.data_history.empty else 0

# Calcul risque explosion (LIE du CO = 125 000 ppm)
risque_expl = (val_co / 125000) * 100

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Jauge de Toxicité (ppm)")
    # Création de la jauge avec seuils colorés
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = val_co,
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [0, 1000]},
            'bar': {'color': "black"},
            'steps': [
                {'range': [0, 50], 'color': "green"},
                {'range': [50, 100], 'color': "yellow"},
                {'range': [100, 400], 'color': "orange"},
                {'range': [400, 1000], 'color': "red"}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 400}
        }
    ))
    fig_gauge.update_layout(height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    st.subheader("Risque d'Explosion")
    # Affichage du risque
    if risque_expl < 0.5:
        couleur_exp = "green"
        txt_exp = "Risque Négligeable"
    elif risque_expl < 1.0:
        couleur_exp = "orange"
        txt_exp = "Risque Faible"
    else:
        couleur_exp = "red"
        txt_exp = "DANGER IMMÉDIAT"
        
    st.markdown(f"""
    <div style="background-color: {couleur_exp}; padding: 20px; border-radius: 10px; color: white; text-align: center;">
        <h2 style="color: white;">{txt_exp}</h2>
        <p>Taux de LIE atteint : {risque_expl:.4f}%</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.metric("Courant de décharge", f"{val_i:.2f} mA")

# ==============================================================================
# RAFRAÎCHISSEMENT
# ==============================================================================
if active_monitoring:
    time.sleep(0.5) 
    st.rerun()
