import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import os

st.set_page_config(layout="wide", page_title="City Analytics Dashboard")

# Use Mapbox when available, otherwise fall back to OpenStreetMap to avoid token issues
mapbox_token = os.getenv("MAPBOX_API_KEY", "") or os.getenv("MAPBOX_TOKEN", "")
if mapbox_token:
    pdk.settings.mapbox_api_key = mapbox_token
map_style = "mapbox://styles/mapbox/light-v9" if mapbox_token else "open-street-map"

# --- DATA LOADING ---
@st.cache_data
def load_data():
    import os
    # Prefer official INSEE dataset when present
    if os.path.exists('cities_insee.csv'):
        df = pd.read_csv('cities_insee.csv')
        # Standardize columns to match app expectations
        df = df.rename(columns={'nom': 'City', 'population': 'Population'})
        # Fill or synthesize missing analytic columns
        np.random.seed(42)
        if 'Average_Income' not in df.columns:
            df['Average_Income'] = np.round(np.random.normal(22000, 4000, len(df))).astype(int)
        if 'Age_0_18_Pct' not in df.columns:
            arr = np.random.dirichlet([2, 3, 3, 2], len(df)) * 100
            df['Age_0_18_Pct'] = np.round(arr[:, 0], 1)
            df['Age_19_40_Pct'] = np.round(arr[:, 1], 1)
            df['Age_41_60_Pct'] = np.round(arr[:, 2], 1)
            df['Age_60_Plus_Pct'] = np.round(arr[:, 3], 1)
        # Ensure lat/lon exist
        if df[['lat', 'lon']].isnull().any().any():
            lats = np.random.uniform(41.0, 51.5, len(df))
            lons = np.random.uniform(-5.0, 9.5, len(df))
            df['lat'] = df['lat'].fillna(pd.Series(lats))
            df['lon'] = df['lon'].fillna(pd.Series(lons))
    elif os.path.exists('cities_data.csv'):
        df = pd.read_csv('cities_data.csv')
    else:
        try:
            from generate_data import generate_french_city_data
            df_gen = generate_french_city_data(5000)
            df_gen.to_csv('cities_data.csv', index=False)
            df = df_gen
        except Exception as e:
            raise FileNotFoundError(f"Data file not found and auto-generation failed: {e}")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Data file missing or generation failed: {e}")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Configuration")

st.sidebar.subheader("Filtrage de base")
min_population = st.sidebar.slider("Population Minimum", 0, 100000, 5000, step=1000)
min_income = st.sidebar.slider("Revenu Moyen Minimum (€)", 10000, 50000, 15000, step=1000)

st.sidebar.subheader("Pondération du Score")
st.sidebar.info("Ajustez l'importance de chaque critère pour identifier les meilleures cibles.")

w_pop = st.sidebar.slider("Poids: Population", 0.0, 10.0, 5.0)
w_income = st.sidebar.slider("Poids: Revenu", 0.0, 10.0, 7.0)
w_age_0_18 = st.sidebar.slider("Poids: 0-18 ans", 0.0, 10.0, 1.0)
w_age_19_40 = st.sidebar.slider("Poids: 19-40 ans", 0.0, 10.0, 2.0)
w_age_41_60 = st.sidebar.slider("Poids: 41-60 ans", 0.0, 10.0, 8.0)
w_age_60_plus = st.sidebar.slider("Poids: 60+ ans", 0.0, 10.0, 4.0)

# --- DATA PROCESSING ---
# Filter data
filtered_df = df[
    (df['Population'] >= min_population) &
    (df['Average_Income'] >= min_income)
].copy()

# Normalize columns for scoring (Min-Max scaling)
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

if not filtered_df.empty:
    s_pop = normalize(filtered_df['Population'])
    s_inc = normalize(filtered_df['Average_Income'])
    s_a1 = normalize(filtered_df['Age_0_18_Pct'])
    s_a2 = normalize(filtered_df['Age_19_40_Pct'])
    s_a3 = normalize(filtered_df['Age_41_60_Pct'])
    s_a4 = normalize(filtered_df['Age_60_Plus_Pct'])

    filtered_df['Score'] = (
        s_pop * w_pop +
        s_inc * w_income +
        s_a1 * w_age_0_18 +
        s_a2 * w_age_19_40 +
        s_a3 * w_age_41_60 +
        s_a4 * w_age_60_plus
    )
    
    if filtered_df['Score'].max() > filtered_df['Score'].min():
        filtered_df['Score'] = (filtered_df['Score'] - filtered_df['Score'].min()) / (filtered_df['Score'].max() - filtered_df['Score'].min()) * 100
    else:
        filtered_df['Score'] = 0

    filtered_df = filtered_df.sort_values(by='Score', ascending=False)
else:
    st.warning("Aucune ville ne correspond aux critères de filtre.")
    st.stop()

# --- DASHBOARD LAYOUT ---
st.title("🎯 Analyse de Cibles - Nettoyage Poubelles")
st.markdown(f"**{len(filtered_df)} villes** correspondent aux critères.")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Cartographie des Opportunités")
    def get_color(score):
        r = int(score * 2.55)
        g = int((100 - score) * 2.55)
        b = 0
        return [r, g, b, 160]

    filtered_df['color'] = filtered_df['Score'].apply(get_color)

    layer = pdk.Layer(
        "ScatterplotLayer",
        filtered_df,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius="Population",
        radius_scale=0.05,
        radius_min_pixels=3,
        radius_max_pixels=30,
        pickable=True,
        auto_highlight=True
    )

    view_state = pdk.ViewState(
        latitude=46.603354,
        longitude=1.888334,
        zoom=5,
        pitch=0,
    )

    tooltip = {
        "html": "<b>{City}</b><br/>Score: {Score:.1f}<br/>Pop: {Population}<br/>Revenu: {Average_Income}€",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style=map_style
    )

    st.pydeck_chart(r)

with col2:
    st.subheader("Top 10 Cibles")
    top_10 = filtered_df[['City', 'Score', 'Population', 'Average_Income', 'Age_41_60_Pct']].head(10)
    display_df = top_10.copy()
    display_df['Score'] = display_df['Score'].apply(lambda x: f"{x:.1f}")
    display_df['Average_Income'] = display_df['Average_Income'].apply(lambda x: f"{x:,.0f}€")
    display_df['Cible Principale %'] = display_df['Age_41_60_Pct'].apply(lambda x: f"{x}%")
    display_df = display_df.drop(columns=['Age_41_60_Pct'])
    st.dataframe(display_df, width='stretch', hide_index=True)
    st.write("---")
    st.metric("Total Population Ciblée", f"{filtered_df['Population'].sum():,}".replace(",", " "))
    st.metric("Revenu Moyen Global", f"{int(filtered_df['Average_Income'].mean()):,}€".replace(",", " "))

st.subheader("Données Détaillées")
st.dataframe(filtered_df.drop(columns=['color']), width='stretch')