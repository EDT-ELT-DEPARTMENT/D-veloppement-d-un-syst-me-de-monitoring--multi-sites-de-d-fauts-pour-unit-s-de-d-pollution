import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==============================================================================
# CONFIGURATION DE LA PLATEFORME
# ==============================================================================
st.set_page_config(
    page_title="Simulation Dynamique CO", 
    page_icon="⚡", 
    layout="wide"
)

st.title("Simulation Dynamique : Réponse du Système aux Fluctuations de Tension")
st.markdown("---")

# ==============================================================================
# 1. MODÉLISATION MATHÉMATIQUE (Base de données réelle)
# ==============================================================================
# Vos données expérimentales
V_data = np.array([2.0, 4.0, 6.0, 8.0, 10.0])
CO_data = np.array([800.0, 780.0, 700.0, 650.0, 480.0])
I_data = np.array([0.48, 1.87, 5.20, 8.90, 10.45])

# Création des modèles polynomiaux (degré 2)
model_co = np.poly1d(np.polyfit(V_data, CO_data, 2))
model_i = np.poly1d(np.polyfit(V_data, I_data, 2))

# ==============================================================================
# 2. INTERFACE DE CONTRÔLE (Sidebar)
# ==============================================================================
st.sidebar.header("Paramètres de la Simulation")
v_consigne = st.sidebar.slider(
    "Tension de consigne (kV)", 
    min_value=2.0, 
    max_value=12.0, 
    value=8.0, 
    step=0.1
)

# Nombre de points temporels
n_points = 50

# ==============================================================================
# 3. GÉNÉRATION DES DONNÉES DYNAMIQUES
# ==============================================================================
# Génération du temps
t = np.linspace(0, 10, n_points)

# Application de la fluctuation de 2% (Bruit aléatoire entre -0.02 et +0.02)
fluctuation = np.random.uniform(-0.02, 0.02, n_points)
v_t = v_consigne * (1 + fluctuation)

# Calcul des réponses dynamiques selon les modèles
co_t = model_co(v_t)
i_t = model_i(v_t)

# Préparation du DataFrame pour l'affichage
df_sim = pd.DataFrame({
    "Temps": t,
    "Tension_V": v_t,
    "CO_ppm": co_t,
    "Courant_mA": i_t
})

# ==============================================================================
# 4. AFFICHAGE DES RÉSULTATS
# ==============================================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Visualisation Temporelle : Concentration CO")
    fig_co = go.Figure()
    fig_co.add_trace(go.Scatter(
        x=df_sim["Temps"], 
        y=df_sim["CO_ppm"], 
        mode='lines', 
        name='CO (ppm)', 
        line=dict(color='red', width=3)
    ))
    fig_co.update_layout(
        xaxis_title="Temps (s)", 
        yaxis_title="CO (ppm)", 
        template="plotly_white",
        title="Variation de la concentration de CO"
    )
    st.plotly_chart(fig_co, use_container_width=True)

with col2:
    st.subheader("Visualisation Temporelle : Courant")
    fig_i = go.Figure()
    fig_i.add_trace(go.Scatter(
        x=df_sim["Temps"], 
        y=df_sim["Courant_mA"], 
        mode='lines', 
        name='Courant (mA)', 
        line=dict(color='orange', width=3)
    ))
    fig_i.update_layout(
        xaxis_title="Temps (s)", 
        yaxis_title="Courant (mA)", 
        template="plotly_white",
        title="Variation du courant de décharge"
    )
    st.plotly_chart(fig_i, use_container_width=True)

# ==============================================================================
# 5. SYNTHÈSE DES DONNÉES
# ==============================================================================
st.markdown("### Synthèse des mesures en temps réel")
st.dataframe(df_sim.head(10), use_container_width=True)

st.warning("Note : Le modèle montre qu'une fluctuation de 2% sur la tension entraîne une variation proportionnelle du courant, ce qui impacte directement l'efficacité d'oxydation du CO.")
