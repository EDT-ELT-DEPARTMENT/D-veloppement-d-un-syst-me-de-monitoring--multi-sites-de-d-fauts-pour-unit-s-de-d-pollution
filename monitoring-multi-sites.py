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
    page_title="Monitoring Sécurité Industrielle CO", 
    layout="wide",
    page_icon="⚠️"
)

st.title("Plateforme de Monitoring : Réacteur et Sécurité Gaz")
st.markdown("---")

# ==============================================================================
# INITIALISATION DES DONNÉES (Session State)
# ==============================================================================
if 'data_history' not in st.session_state:
    st.session_state.data_history = pd.DataFrame(columns=["Temps", "Tension", "CO", "Courant"])

# Modèles mathématiques basés sur vos mesures
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
    # Fluctuations de 2% sur la tension
    fluctuation = np.random.uniform(-0.02, 0.02)
    tension_instantanee = v_consigne * (1 + fluctuation)
    
    # Calcul des réponses du système
    co_instantane = max(0, model_co(tension_instantanee))
    i_instantane = max(0, model_i(tension_instantanee))
    
    # Mise à jour de l'historique
    new_data = {
        "Temps": datetime.now().strftime("%H:%M:%S"),
        "Tension": tension_instantanee,
        "CO": co_instantane,
        "Courant": i_instantane
    }
    
    st.session_state.data_history = pd.concat([st.session_state.data_history, pd.DataFrame([new_data])], ignore_index=True)
    
    # Garder les 50 dernières valeurs
    if len(st.session_state.data_history) > 50:
        st.session_state.data_history = st.session_state.data_history.iloc[-50:]

# ==============================================================================
# AFFICHAGE DU TABLEAU DE BORD
# ==============================================================================
val_co = st.session_state.data_history["CO"].iloc[-1] if not st.session_state.data_history.empty else 0
val_i = st.session_state.data_history["Courant"].iloc[-1] if not st.session_state.data_history.empty else 0
val_v = st.session_state.data_history["Tension"].iloc[-1] if not st.session_state.data_history.empty else v_consigne

# Calcul risque explosion (LIE = 125 000 ppm)
risque_expl = (val_co / 125000) * 100

# Ligne 1 : Indicateurs numériques
col1, col2, col3 = st.columns(3)
col1.metric("Concentration CO (ppm)", f"{val_co:.1f} ppm")
col2.metric("Courant de décharge (mA)", f"{val_i:.2f} mA")
col3.metric("Tension actuelle (kV)", f"{val_v:.2f} kV")

st.markdown("---")

# Ligne 2 : Jauge et Risque Explosion
col_gauge, col_expl = st.columns([1, 1])

with col_gauge:
    st.subheader("Jauge de Toxicité (ppm)")
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

with col_expl:
    st.subheader("Évaluation du Risque d'Explosion")
    
    # Logique couleur risque explosion
    if risque_expl < 0.5:
        couleur_exp = "#2ecc71" # Vert
        txt_exp = "RISQUE NÉGLIGEABLE"
    elif risque_expl < 1.0:
        couleur_exp = "#f1c40f" # Jaune
        txt_exp = "RISQUE FAIBLE"
    else:
        couleur_exp = "#e74c3c" # Rouge
        txt_exp = "DANGER IMMÉDIAT"
        
    st.markdown(f"""
    <div style="background-color: {couleur_exp}; padding: 30px; border-radius: 15px; color: white; text-align: center;">
        <h2 style="color: white;">{txt_exp}</h2>
        <p style="font-size: 20px;">Taux de LIE atteint : {risque_expl:.4f}%</p>
    </div>
    """, unsafe_allow_html=True)

# Ligne 3 : Courbes historiques
col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    st.subheader("Évolution Concentration CO")
    fig_co = go.Figure()
    if not st.session_state.data_history.empty:
        fig_co.add_trace(go.Scatter(x=st.session_state.data_history["Temps"], y=st.session_state.data_history["CO"], 
                                    mode='lines', name='CO (ppm)', line=dict(color='red', width=3)))
    fig_co.update_layout(yaxis_range=[0, 1000], template="plotly_white")
    st.plotly_chart(fig_co, use_container_width=True)

with col_graph2:
    st.subheader("Évolution Courant")
    fig_i = go.Figure()
    if not st.session_state.data_history.empty:
        fig_i.add_trace(go.Scatter(x=st.session_state.data_history["Temps"], y=st.session_state.data_history["Courant"], 
                                    mode='lines', name='I (mA)', line=dict(color='orange', width=3)))
    fig_i.update_layout(yaxis_range=[0, 15], template="plotly_white")
    st.plotly_chart(fig_i, use_container_width=True)

# ==============================================================================
# RAFRAÎCHISSEMENT AUTOMATIQUE
# ==============================================================================
if active_monitoring:
    time.sleep(0.5) 
    st.rerun()
else:
    st.sidebar.info("Cochez la case 'Démarrer' pour activer la simulation.")
