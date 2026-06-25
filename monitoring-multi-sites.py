import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==============================================================================
# CONFIGURATION DE LA PAGE
# ==============================================================================
st.set_page_config(
    page_title="Monitoring Industriel - Performance Réacteur", 
    page_icon="⚡", 
    layout="wide"
)

# ==============================================================================
# DONNÉES RÉELLES ET MODÉLISATION MATHÉMATIQUE
# ==============================================================================

# Vos données réelles pour l'installation pétrolière
V_data = np.array([2.0, 4.0, 6.0, 8.0, 10.0])
CO_data = np.array([800.0, 780.0, 700.0, 650.0, 480.0])
I_data = np.array([0.48, 1.87, 5.20, 8.90, 10.45])

# Calcul des modèles polynomiaux (degré 2 pour suivre la courbure)
# CO = a*V^2 + b*V + c
coeffs_co = np.polyfit(V_data, CO_data, 2)
model_co = np.poly1d(coeffs_co)

# I = a*V^2 + b*V + c
coeffs_i = np.polyfit(V_data, I_data, 2)
model_i = np.poly1d(coeffs_i)

# Calcul théorique pour 0 ppm
# On trouve la racine du polynôme pour CO = 0
roots = model_co.roots
# On filtre les racines réelles > 10
v_target = [r for r in roots if r > 10]
v_zero_target = v_target[0] if v_target else 15.0

# ==============================================================================
# TITRE ET SIDEBAR
# ==============================================================================
st.title("Plateforme de Monitoring : Performance et Sécurité Gaz")
st.markdown("---")

st.sidebar.header("Paramètres de contrôle")
v_selected = st.sidebar.slider(
    "Ajuster la Tension (kV)", 
    min_value=2.0, 
    max_value=20.0, 
    value=6.0, 
    step=0.1
)

# ==============================================================================
# CALCUL DYNAMIQUE
# ==============================================================================
# Prédictions selon le modèle
co_predit = max(0, model_co(v_selected))
i_predit = max(0, model_i(v_selected))

# ==============================================================================
# AFFICHAGE DES KPIs
# ==============================================================================
st.subheader(f"État du réacteur à {v_selected:.1f} kV")

col1, col2, col3 = st.columns(3)

col1.metric("Tension Appliquée", f"{v_selected:.1f} kV")
col2.metric("Courant de Décharge (Prédit)", f"{i_predit:.2f} mA")
col3.metric("Concentration CO (Prédite)", f"{co_predit:.1f} ppm", 
            delta="Critique" if co_predit > 700 else "Optimal", 
            delta_color="inverse")

# ==============================================================================
# VISUALISATION GRAPHIQUE
# ==============================================================================
col_gauche, col_droite = st.columns([1, 2])

with col_gauche:
    st.subheader("Analyse du modèle")
    st.markdown(f"""
    **Modèle de réduction du CO :**
    - Fonction : $CO(V) = {coeffs_co[0]:.2f}V^2 + {coeffs_co[1]:.2f}V + {coeffs_co[2]:.2f}$
    - Tension théorique pour 0 ppm : **{v_zero_target:.1f} kV**
    
    *Ce modèle permet d'estimer l'efficacité du réacteur au-delà de la plage expérimentale testée (10 kV).*
    """)
    
    st.write("---")
    st.subheader("Données expérimentales")
    df_exp = pd.DataFrame({
        "Tension (kV)": V_data,
        "CO (ppm)": CO_data,
        "Courant (mA)": I_data
    })
    st.dataframe(df_exp, hide_index=True, use_container_width=True)

with col_droite:
    st.subheader("Courbe de réduction dynamique")
    
    # Création du graphique
    v_range = np.linspace(2, 20, 100)
    co_range = np.maximum(0, model_co(v_range))
    
    fig = go.Figure()
    
    # Courbe théorique
    fig.add_trace(go.Scatter(
        x=v_range, 
        y=co_range, 
        mode='lines', 
        name='Modèle CO(V)', 
        line=dict(color='cyan', width=3)
    ))
    
    # Points expérimentaux
    fig.add_trace(go.Scatter(
        x=V_data, 
        y=CO_data, 
        mode='markers', 
        name='Mesures réelles', 
        marker=dict(size=12, color='white', line=dict(width=2, color='DarkSlateGrey'))
    ))
    
    # Point de fonctionnement actuel
    fig.add_trace(go.Scatter(
        x=[v_selected], 
        y=[co_predit], 
        mode='markers', 
        name='Point actuel', 
        marker=dict(size=18, color='red', symbol='x')
    ))
    
    fig.update_layout(
        xaxis_title="Tension (kV)",
        yaxis_title="Concentration CO (ppm)",
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
