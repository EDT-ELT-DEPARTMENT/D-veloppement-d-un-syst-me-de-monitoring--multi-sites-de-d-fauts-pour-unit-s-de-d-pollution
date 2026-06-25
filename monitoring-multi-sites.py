import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime

# ==============================================================================
# CONFIGURATION ET INITIALISATION
# ==============================================================================
st.set_page_config(page_title="Monitoring Dynamique CO", layout="wide")

st.title("Monitoring Dynamique : Réponse du Système aux Fluctuations")
st.markdown("---")

# Initialisation de l'historique des données en mémoire
if 'data_history' not in st.session_state:
    st.session_state.data_history = pd.DataFrame(columns=["Temps", "Tension", "CO", "Courant"])

# Modèles mathématiques établis (degré 2)
V_ref = np.array([2.0, 4.0, 6.0, 8.0, 10.0])
CO_ref = np.array([800.0, 780.0, 700.0, 650.0, 480.0])
I_ref = np.array([0.48, 1.87, 5.20, 8.90, 10.45])

model_co = np.poly1d(np.polyfit(V_ref, CO_ref, 2))
model_i = np.poly1d(np.polyfit(V_ref, I_ref, 2))

# ==============================================================================
# SIDEBAR DE CONTRÔLE
# ==============================================================================
st.sidebar.header("Paramètres de Contrôle")
v_consigne = st.sidebar.slider("Tension de consigne (kV)", 2.0, 12.0, 8.0, 0.1)
active_monitoring = st.sidebar.checkbox("Démarrer le monitoring en temps réel", value=False)

# ==============================================================================
# LOGIQUE DYNAMIQUE
# ==============================================================================

# Si le monitoring est actif, nous générons une nouvelle mesure
if active_monitoring:
    # 1. Calcul de la tension avec fluctuation de 2% (Bruit aléatoire)
    fluctuation = np.random.uniform(-0.02, 0.02)
    tension_instantanee = v_consigne * (1 + fluctuation)
    
    # 2. Calcul des réponses du système
    co_instantane = max(0, model_co(tension_instantanee))
    i_instantane = max(0, model_i(tension_instantanee))
    
    # 3. Ajout au DataFrame historique
    new_data = {
        "Temps": datetime.now().strftime("%H:%M:%S"),
        "Tension": tension_instantanee,
        "CO": co_instantane,
        "Courant": i_instantane
    }
    
    st.session_state.data_history = pd.concat([
        st.session_state.data_history, 
        pd.DataFrame([new_data])
    ], ignore_index=True)
    
    # Garder seulement les 50 dernières mesures
    if len(st.session_state.data_history) > 50:
        st.session_state.data_history = st.session_state.data_history.iloc[-50:]

# ==============================================================================
# AFFICHAGE DES AFFICHEURS NUMÉRIQUES (METRICS)
# ==============================================================================
st.subheader("Indicateurs Temps Réel")
col_met1, col_met2, col_met3 = st.columns(3)

# Valeurs par défaut si pas de données
val_co = st.session_state.data_history["CO"].iloc[-1] if not st.session_state.data_history.empty else 0
val_i = st.session_state.data_history["Courant"].iloc[-1] if not st.session_state.data_history.empty else 0
val_v = st.session_state.data_history["Tension"].iloc[-1] if not st.session_state.data_history.empty else v_consigne

col_met1.metric("Concentration CO", f"{val_co:.1f} ppm")
col_met2.metric("Courant de Décharge", f"{val_i:.2f} mA")
col_met3.metric("Tension Actuelle", f"{val_v:.2f} kV")

st.markdown("---")

# ==============================================================================
# AFFICHAGE DES COURBES
# ==============================================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Historique Concentration CO (ppm)")
    fig_co = go.Figure()
    if not st.session_state.data_history.empty:
        fig_co.add_trace(go.Scatter(
            x=st.session_state.data_history["Temps"], 
            y=st.session_state.data_history["CO"], 
            mode='lines', 
            name='CO (ppm)', 
            line=dict(color='red', width=3)
        ))
    fig_co.update_layout(yaxis_range=[0, 1000], template="plotly_white")
    st.plotly_chart(fig_co, use_container_width=True)

with col2:
    st.subheader("Historique Courant (mA)")
    fig_i = go.Figure()
    if not st.session_state.data_history.empty:
        fig_i.add_trace(go.Scatter(
            x=st.session_state.data_history["Temps"], 
            y=st.session_state.data_history["Courant"], 
            mode='lines', 
            name='I (mA)', 
            line=dict(color='orange', width=3)
        ))
    fig_i.update_layout(yaxis_range=[0, 15], template="plotly_white")
    st.plotly_chart(fig_i, use_container_width=True)

# ==============================================================================
# RAFRAÎCHISSEMENT AUTOMATIQUE
# ==============================================================================
if active_monitoring:
    time.sleep(0.5) 
    st.rerun()
else:
    st.info("Activez le monitoring dans la barre latérale pour démarrer.")
