import streamlit as st
import pandas as pd
import numpy as np

# Configuration de la page
st.set_page_config(
	page_title="Analyse des Villes Potentielles",
	page_icon="📍",
	layout="wide"
)

# CSS personnalisé
st.markdown("""
<style>
	.main-header {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		padding: 2rem;
		border-radius: 10px;
		color: white;
		margin-bottom: 2rem;
	}
	.metric-card {
		background: white;
		padding: 1.5rem;
		border-radius: 10px;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}
	.score-high {
		background-color: #d4edda;
		color: #155724;
		padding: 0.5rem;
		border-radius: 5px;
		font-weight: bold;
	}
	.score-medium {
		background-color: #d1ecf1;
		color: #0c5460;
		padding: 0.5rem;
		border-radius: 5px;
		font-weight: bold;
	}
	.score-low {
		background-color: #fff3cd;
		color: #856404;
		padding: 0.5rem;
		border-radius: 5px;
		font-weight: bold;
	}
</style>
""", unsafe_allow_html=True)

# Données des villes
@st.cache_data
def load_data():
	# Charger les données depuis le fichier CSV
	df = pd.read_csv('data.csv', sep=';')
	return df

def calculate_score(row):
	"""Calcul du score pondéré"""
	poids_pop60 = 0.35
	poids_revenu = 0.25
	poids_proprio = 0.20
	poids_zone = 0.15
	poids_pop = 0.05
    
	score_pop60 = min((row['plus60ans'] / 35) * 100, 100)
	score_revenu = min((row['revenuMedian'] / 27000) * 100, 100)
	score_proprio = min((row['tauxProprietaires'] / 65) * 100, 100)
	score_zone = min(((row['zoneChalandise'] - 300) / 120) * 100, 100)
	score_pop = min((row['population'] / 150000) * 100, 100)
    
	score_total = (
		score_pop60 * poids_pop60 +
		score_revenu * poids_revenu +
		score_proprio * poids_proprio +
		score_zone * poids_zone +
		score_pop * poids_pop
	)
    
	return round(score_total)

def calculate_foyers(row):
	"""Calcul des foyers et clients potentiels"""
	nb_personnes_60plus = round((row['population'] * row['plus60ans']) / 100)
	foyers_potentiels = round(nb_personnes_60plus / 2.2)
	taux_penetration = 0.15 if row['zoneChalandise'] >= 300 else 0.10
	clients_potentiels = round(foyers_potentiels * taux_penetration)
    
	return pd.Series({
		'foyersPotentiels': foyers_potentiels,
		'clientsPotentiels': clients_potentiels,
		'personnes60plus': nb_personnes_60plus
	})

# Chargement des données
df = load_data()

# Calcul du score et des foyers
df['score'] = df.apply(calculate_score, axis=1)
df[['foyersPotentiels', 'clientsPotentiels', 'personnes60plus']] = df.apply(calculate_foyers, axis=1)

# Header
st.markdown("""
<div class="main-header">
	<h1>📍 Analyse des Villes Potentielles</h1>
	<p style="font-size: 1.1rem; margin-top: 0.5rem;">Service de nettoyage de poubelles pour particuliers</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Filtres
st.sidebar.header("🔍 Filtres")

search_term = st.sidebar.text_input("🔎 Rechercher", placeholder="Ville ou département...")

region_filter = st.sidebar.selectbox(
	"Région",
	["Toutes"] + sorted(df['region'].unique().tolist())
)

min_population = st.sidebar.number_input(
	"Population minimale",
	min_value=0,
	max_value=int(df['population'].max()),
	value=3000,
	step=1000
)

min_score = st.sidebar.slider(
	"Score minimal",
	min_value=0,
	max_value=100,
	value=0,
	step=5
)

# Application des filtres
filtered_df = df.copy()

if search_term:
	filtered_df = filtered_df[
		filtered_df['nom'].str.contains(search_term, case=False, na=False) |
		filtered_df['departement'].str.contains(search_term, case=False, na=False)
	]

if region_filter != "Toutes":
	filtered_df = filtered_df[filtered_df['region'] == region_filter]

filtered_df = filtered_df[filtered_df['population'] >= min_population]
filtered_df = filtered_df[filtered_df['score'] >= min_score]

# Tri
sort_by = st.sidebar.selectbox(
	"Trier par",
	["Score", "Population 60+", "Revenu médian", "Clients potentiels", "Population totale"],
	index=0
)

sort_order = st.sidebar.radio("Ordre", ["Décroissant", "Croissant"])

sort_mapping = {
	"Score": "score",
	"Population 60+": "plus60ans",
	"Revenu médian": "revenuMedian",
	"Clients potentiels": "clientsPotentiels",
	"Population totale": "population"
}

filtered_df = filtered_df.sort_values(
	by=sort_mapping[sort_by],
	ascending=(sort_order == "Croissant")
)

# Statistiques globales
col1, col2, col3 = st.columns(3)

with col1:
	st.metric("🏙️ Villes analysées", len(filtered_df))

with col2:
	avg_score = round(filtered_df['score'].mean()) if len(filtered_df) > 0 else 0
	st.metric("⭐ Score moyen", f"{avg_score}/100")

with col3:
	total_clients = filtered_df['clientsPotentiels'].sum()
	st.metric("👥 Clients potentiels total", f"{total_clients:,}")

# Méthodologie
with st.expander("📊 Méthodologie de scoring", expanded=False):
	st.markdown("""
	**Pondération du score :**
	- 🎯 **35%** Population 60+ ans (cible principale)
	- 💰 **25%** Revenu médian (pouvoir d'achat)
	- 🏠 **20%** Taux de propriétaires (stabilité, entretien)
	- 📍 **15%** Zone de chalandise (min 300 personnes)
	- 👥 **5%** Population totale (marché potentiel)
    
	**Calcul des clients potentiels :**
	- Taux de pénétration estimé : 10-15% des foyers de 60+ ans
	- Taille moyenne des foyers : 2,2 personnes
	""")

# Tableau des résultats
st.subheader("📋 Résultats détaillés")

if len(filtered_df) > 0:
	# Préparation de l'affichage
	display_df = filtered_df[[
		'nom', 'departement', 'region', 'score', 'population', 
		'plus60ans', 'personnes60plus', 'revenuMedian', 
		'tauxProprietaires', 'zoneChalandise', 
		'foyersPotentiels', 'clientsPotentiels'
	]].copy()
    
	# Fonction pour colorer le score
	def color_score(val):
		if val >= 80:
			return 'background-color: #d4edda; color: #155724; font-weight: bold'
		elif val >= 60:
			return 'background-color: #d1ecf1; color: #0c5460; font-weight: bold'
		elif val >= 40:
			return 'background-color: #fff3cd; color: #856404; font-weight: bold'
		else:
			return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
    
	# Renommage des colonnes
	display_df.columns = [
		'Ville', 'Département', 'Région', 'Score', 'Population', 
		'60+ (%)', '60+ (nb)', 'Revenu médian', 'Proprio (%)', 'Zone', 
		'Foyers pot.', 'Clients pot.'
	]
    
	# Affichage avec ou sans style selon la taille
	if len(display_df) > 5000:
		# Pour les grands ensembles de données, afficher sans style
		st.info(f"⚠️ Affichage de {len(display_df):,} villes. Le style est désactivé pour améliorer les performances.")
		st.dataframe(display_df, use_container_width=True, height=600)
	else:
		# Pour les petits ensembles, afficher avec style
		styled_df = display_df.style.applymap(
			color_score, 
			subset=['Score']
		).format({
			'Population': '{:,.0f}',
			'Revenu médian': '{:,.0f} €',
			'60+ (nb)': '{:,.0f}',
			'Foyers pot.': '{:,.0f}',
			'Clients pot.': '{:,.0f}',
			'60+ (%)': '{:.1f}%',
			'Proprio (%)': '{:.0f}%',
			'Score': '{:.0f}/100'
		})
		st.dataframe(styled_df, use_container_width=True, height=600)
    
	# Bouton de téléchargement
	csv = display_df.to_csv(index=False).encode('utf-8')
	st.download_button(
		label="📥 Télécharger les résultats (CSV)",
		data=csv,
		file_name='analyse_villes.csv',
		mime='text/csv',
	)
    
	# Top 10
	st.subheader("🏆 Top 10 des villes")
	top10 = filtered_df.nlargest(10, 'score')[['nom', 'score', 'clientsPotentiels', 'plus60ans', 'revenuMedian']]
    
	col1, col2 = st.columns([2, 1])
    
	with col1:
		st.bar_chart(top10.set_index('nom')['score'])
    
	with col2:
		for idx, row in top10.iterrows():
			st.markdown(f"""
			**{row['nom']}**  
			Score: {row['score']}/100  
			Clients: {row['clientsPotentiels']}  
			---
			""")
else:
	st.warning("⚠️ Aucune ville ne correspond aux critères de filtrage")

# Footer
st.markdown("---")
st.markdown("💡 **Astuce :** Ajustez les filtres dans la barre latérale pour affiner votre recherche")