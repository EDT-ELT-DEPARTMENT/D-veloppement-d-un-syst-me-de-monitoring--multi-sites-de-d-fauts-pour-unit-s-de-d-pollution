import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta
from scipy.interpolate import PchipInterpolator

# ==============================================================================
# Titre du Projet : Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA
# ==============================================================================

# Configuration de la page
st.set_page_config(
    page_title="Plateforme de gestion des EDTs-S2-2026", 
    page_icon="⚡", 
    layout="wide"
)

# Initialisation de l'état pour les données
if 'data_history' not in st.session_state:
    st.session_state.data_history = pd.DataFrame(columns=["Heure", "Gaz_ADC", "Courant_mA", "Tension_kV"])

# ==============================================================================
# Fonctions de modélisation physique
# ==============================================================================

def get_caracteristique_iv_modele():
    """Définit le modèle de la caractéristique I-V du réacteur fil-cylindre."""
    tensions_exp = np.array([2.0, 4.0, 6.0, 8.0, 10.0])
    courants_exp = np.array([0.48, 1.87, 5.20, 8.90, 10.45])
    return PchipInterpolator(tensions_exp, courants_exp)

def afficher_caracteristique_iv():
    """Affiche la signature électrique (I-V) du filtre."""
    st.subheader("Caractéristique Électrique (I-V) du Réacteur")
    
    tensions_kv = [2.0, 4.0, 6.0, 8.0, 10.0]
    courants_ma = [0.48, 1.87, 5.20, 8.90, 10.45]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=tensions_kv, 
        y=courants_ma, 
        mode='lines+markers',
        name='Courbe I-V Expérimentale',
        line=dict(color='#00F2FF', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title="Signature électrique du filtre cylindrique (100mm x 100mm)",
        xaxis_title="Tension (kV)",
        yaxis_title="Courant de décharge (mA)",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# Interface Principale
# ==============================================================================

st.title("Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA")
st.markdown("---")

# Sidebar pour les paramètres
st.sidebar.title("Configuration")
auto_refresh = st.sidebar.checkbox("Activer le rafraîchissement temps réel", value=True)

# Dispositions des éléments
col_gauche, col_droite = st.columns([1, 1])

with col_gauche:
    st.subheader("Monitoring des paramètres")
    # Simulation des données (à remplacer par la lecture série Arduino)
    # Disposition demandée : Enseignements, Code, Enseignants, Horaire, Jours, Lieu, Promotion
    data_table = pd.DataFrame({
        "Enseignements": ["Stabilité Réseaux", "Éclairage LED", "Intelligence Artificielle"],
        "Code": ["SDRE", "LEDPA", "TIA"],
        "Enseignants": ["REZ", "Bermaki", "Touhami"],
        "Horaire": ["8h-9h30", "9h30-11h", "9h30-11h"],
        "Jours": ["Dimanche", "Dimanche", "Lundi"],
        "Lieu": ["S06", "S06", "S06"],
        "Promotion": ["M2RE", "M2RE", "M2RE"]
    })
    st.table(data_table)

with col_droite:
    afficher_caracteristique_iv()

# ==============================================================================
# Logique de rafraîchissement
# ==============================================================================
if auto_refresh:
    time.sleep(2)
    st.rerun()
