import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==============================================================================
# CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="Modélisation CO", layout="wide")

st.title("Modélisation Mathématique : Réduction du CO par Plasma")

# Données réelles
V_data = np.array([2, 4, 6, 8, 10])
CO_data = np.array([800, 780, 700, 650, 480])

# Calcul du modèle polynomial (degré 2)
coeffs = np.polyfit(V_data, CO_data, 2)
poly_model = np.poly1d(coeffs)

# Calcul du point théorique à 0 ppm (racine du polynôme)
# On cherche la plus petite racine positive supérieure à 10
roots = poly_model.roots
v_zero_target = [r for r in roots if r > 10][0]

# ==============================================================================
# INTERFACE D'AJUSTEMENT
# ==============================================================================
st.sidebar.header("Paramètres de contrôle")
v_selected = st.sidebar.slider("Ajuster la Tension (kV)", min_value=2.0, max_value=20.0, value=6.0, step=0.1)

# Calcul dynamique
co_predit = poly_model(v_selected)
co_predit = max(0, co_predit) # Le CO ne peut pas être négatif

# Affichage des résultats
col1, col2 = st.columns(2)

with col1:
    st.metric("Tension Actuelle", f"{v_selected:.1f} kV")
    st.metric("Concentration CO Prédite", f"{co_predit:.1f} ppm")
    st.markdown(f"**Tension théorique pour 0 ppm :** {v_zero_target:.1f} kV")

# ==============================================================================
# VISUALISATION DYNAMIQUE
# ==============================================================================
st.subheader("Courbe de réduction du CO")

# Création des points pour la courbe lisse
v_range = np.linspace(2, 20, 100)
co_range = poly_model(v_range)
co_range = np.maximum(0, co_range)

fig = go.Figure()

# Courbe du modèle
fig.add_trace(go.Scatter(x=v_range, y=co_range, mode='lines', name='Modèle Mathématique', line=dict(color='cyan', width=3)))

# Points expérimentaux
fig.add_trace(go.Scatter(x=V_data, y=CO_data, mode='markers', name='Données Réelles', marker=dict(size=12, color='white')))

# Point actuel
fig.add_trace(go.Scatter(x=[v_selected], y=[co_predit], mode='markers', name='Point de Fonctionnement', marker=dict(size=15, color='red', symbol='x')))

fig.update_layout(
    xaxis_title="Tension (kV)",
    yaxis_title="Concentration CO (ppm)",
    template="plotly_dark",
    title="Évolution du CO : Modèle quadratique"
)

st.plotly_chart(fig, use_container_width=True)

st.info(f"Pour optimiser le système, la tension cible devrait être maintenue au-dessus de {v_selected:.1f} kV pour minimiser les émissions.")
