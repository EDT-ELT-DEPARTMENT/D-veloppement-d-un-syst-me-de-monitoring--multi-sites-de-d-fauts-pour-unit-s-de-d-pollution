import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==============================================================================
# CONFIGURATION DE LA PLATEFORME
# ==============================================================================
st.set_page_config(
    page_title="Monitoring Industriel - Performance Réacteur", 
    page_icon="⚡", 
    layout="wide"
)

st.title("Plateforme de Monitoring : Performance et Sécurité Gaz")
st.markdown("---")

# ==============================================================================
# DONNÉES EXPÉRIMENTALES (Vos mesures)
# ==============================================================================
# Ces données sont utilisées pour l'Installation Pétrolière
data_petroliere = pd.DataFrame({
    "Tension (kV)": [2, 4, 6, 8, 10],
    "Capteur CO (ppm)": [800, 780, 700, 650, 480],
    "Courant de décharge (mA)": [0.48, 1.87, 5.20, 8.90, 10.45]
})

# Données pour la Cimenterie (Basées sur un modèle similaire pour le monitoring)
data_cimenterie = pd.DataFrame({
    "Tension (kV)": [2, 4, 6, 8, 10],
    "Capteur CO (ppm)": [850, 820, 750, 680, 520],
    "Courant de décharge (mA)": [0.40, 1.50, 4.80, 8.20, 9.90]
})

# ==============================================================================
# SIDEBAR
# ==============================================================================
st.sidebar.title("Paramètres")
site_selection = st.sidebar.selectbox("Sélectionnez le site :", ["Installation Pétrolière", "Cimenterie"])

# ==============================================================================
# LOGIQUE D'AFFICHAGE
# ==============================================================================

# Sélection du jeu de données selon le site
df = data_petroliere if site_selection == "Installation Pétrolière" else data_cimenterie

st.header(f"Suivi Technique : {site_selection}")

# Affichage des KPIs (Dernière valeur enregistrée)
latest = df.iloc[-1]
col1, col2, col3 = st.columns(3)
col1.metric("Tension Appliquée", f"{latest['Tension (kV)']} kV")
col2.metric("Courant de Décharge", f"{latest['Courant de décharge (mA)']} mA")
col3.metric("Concentration CO", f"{latest['Capteur CO (ppm)']} ppm", delta="Optimal" if latest['Capteur CO (ppm)'] < 500 else "Alerte", delta_color="inverse")

# Mise en page : Tableau à gauche, Graphique à droite
col_gauche, col_droite = st.columns([1, 2])

with col_gauche:
    st.subheader("Données de mesures")
    st.dataframe(df, hide_index=True, use_container_width=True)
    
    st.markdown("""
    **Analyse :** La corrélation entre la tension et la baisse du CO montre l'efficacité de la décharge couronne. 
    À 10 kV, le courant de décharge est maximal, ce qui correspond au point de traitement le plus efficace pour l'oxydation du CO.
    """)

with col_droite:
    st.subheader("Corrélation Tension / Courant / Concentration CO")
    
    # Création du graphique à double axe (Y1: Courant, Y2: CO)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Trace Courant
    fig.add_trace(
        go.Scatter(x=df["Tension (kV)"], y=df["Courant de décharge (mA)"], 
                   name="Courant (mA)", line=dict(color="orange", width=4), mode='lines+markers'),
        secondary_y=False
    )
    
    # Trace CO
    fig.add_trace(
        go.Scatter(x=df["Tension (kV)"], y=df["Capteur CO (ppm)"], 
                   name="CO (ppm)", line=dict(color="red", width=4), mode='lines+markers'),
        secondary_y=True
    )
    
    fig.update_layout(
        xaxis_title="Tension Appliquée (kV)",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_yaxes(title_text="Courant de décharge (mA)", secondary_y=False)
    fig.update_yaxes(title_text="Concentration CO (ppm)", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)
