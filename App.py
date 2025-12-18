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
	villes = [
		# Nouvelle-Aquitaine
		{"nom": "La Rochelle", "population": 77196, "plus60ans": 26.5, "revenuMedian": 22100, "tauxProprietaires": 52, "region": "Nouvelle-Aquitaine", "zoneChalandise": 350, "departement": "Charente-Maritime"},
		{"nom": "Rochefort", "population": 24118, "plus60ans": 30.2, "revenuMedian": 19800, "tauxProprietaires": 55, "region": "Nouvelle-Aquitaine", "zoneChalandise": 320, "departement": "Charente-Maritime"},
		{"nom": "Royan", "population": 18934, "plus60ans": 35.8, "revenuMedian": 21300, "tauxProprietaires": 58, "region": "Nouvelle-Aquitaine", "zoneChalandise": 380, "departement": "Charente-Maritime"},
		{"nom": "Saintes", "population": 25268, "plus60ans": 28.4, "revenuMedian": 20100, "tauxProprietaires": 53, "region": "Nouvelle-Aquitaine", "zoneChalandise": 340, "departement": "Charente-Maritime"},
		{"nom": "Cognac", "population": 18806, "plus60ans": 27.9, "revenuMedian": 19500, "tauxProprietaires": 50, "region": "Nouvelle-Aquitaine", "zoneChalandise": 310, "departement": "Charente"},
		{"nom": "Angoulême", "population": 41740, "plus60ans": 26.8, "revenuMedian": 19900, "tauxProprietaires": 48, "region": "Nouvelle-Aquitaine", "zoneChalandise": 360, "departement": "Charente"},
		{"nom": "Niort", "population": 58660, "plus60ans": 24.2, "revenuMedian": 21200, "tauxProprietaires": 51, "region": "Nouvelle-Aquitaine", "zoneChalandise": 330, "departement": "Deux-Sèvres"},
		{"nom": "Bressuire", "population": 19882, "plus60ans": 27.5, "revenuMedian": 20400, "tauxProprietaires": 61, "region": "Nouvelle-Aquitaine", "zoneChalandise": 325, "departement": "Deux-Sèvres"},
		{"nom": "Périgueux", "population": 29560, "plus60ans": 29.1, "revenuMedian": 19700, "tauxProprietaires": 51, "region": "Nouvelle-Aquitaine", "zoneChalandise": 325, "departement": "Dordogne"},
		{"nom": "Bergerac", "population": 27680, "plus60ans": 30.8, "revenuMedian": 19200, "tauxProprietaires": 54, "region": "Nouvelle-Aquitaine", "zoneChalandise": 320, "departement": "Dordogne"},
		{"nom": "Bayonne", "population": 51228, "plus60ans": 27.8, "revenuMedian": 21400, "tauxProprietaires": 48, "region": "Nouvelle-Aquitaine", "zoneChalandise": 345, "departement": "Pyrénées-Atlantiques"},
		{"nom": "Biarritz", "population": 25532, "plus60ans": 33.2, "revenuMedian": 24100, "tauxProprietaires": 56, "region": "Nouvelle-Aquitaine", "zoneChalandise": 365, "departement": "Pyrénées-Atlantiques"},
		{"nom": "Pau", "population": 77215, "plus60ans": 26.1, "revenuMedian": 21100, "tauxProprietaires": 47, "region": "Nouvelle-Aquitaine", "zoneChalandise": 360, "departement": "Pyrénées-Atlantiques"},
		{"nom": "Limoges", "population": 132175, "plus60ans": 27.4, "revenuMedian": 20100, "tauxProprietaires": 48, "region": "Nouvelle-Aquitaine", "zoneChalandise": 405, "departement": "Haute-Vienne"},
        
		# Bretagne
		{"nom": "Vannes", "population": 54020, "plus60ans": 25.1, "revenuMedian": 23400, "tauxProprietaires": 54, "region": "Bretagne", "zoneChalandise": 365, "departement": "Morbihan"},
		{"nom": "Lorient", "population": 57662, "plus60ans": 24.3, "revenuMedian": 20800, "tauxProprietaires": 48, "region": "Bretagne", "zoneChalandise": 340, "departement": "Morbihan"},
		{"nom": "Quimper", "population": 63473, "plus60ans": 25.8, "revenuMedian": 21900, "tauxProprietaires": 52, "region": "Bretagne", "zoneChalandise": 355, "departement": "Finistère"},
		{"nom": "Saint-Brieuc", "population": 45207, "plus60ans": 26.4, "revenuMedian": 20600, "tauxProprietaires": 49, "region": "Bretagne", "zoneChalandise": 335, "departement": "Côtes-d'Armor"},
		{"nom": "Brest", "population": 139456, "plus60ans": 22.1, "revenuMedian": 20200, "tauxProprietaires": 45, "region": "Bretagne", "zoneChalandise": 420, "departement": "Finistère"},
		{"nom": "Rennes", "population": 221272, "plus60ans": 19.8, "revenuMedian": 22300, "tauxProprietaires": 42, "region": "Bretagne", "zoneChalandise": 445, "departement": "Ille-et-Vilaine"},
		{"nom": "Saint-Malo", "population": 46803, "plus60ans": 28.6, "revenuMedian": 22700, "tauxProprietaires": 53, "region": "Bretagne", "zoneChalandise": 345, "departement": "Ille-et-Vilaine"},
        
		# Pays de la Loire
		{"nom": "La Roche-sur-Yon", "population": 54878, "plus60ans": 25.9, "revenuMedian": 21700, "tauxProprietaires": 54, "region": "Pays de la Loire", "zoneChalandise": 345, "departement": "Vendée"},
		{"nom": "Cholet", "population": 54186, "plus60ans": 26.2, "revenuMedian": 21100, "tauxProprietaires": 56, "region": "Pays de la Loire", "zoneChalandise": 340, "departement": "Maine-et-Loire"},
		{"nom": "Laval", "population": 49728, "plus60ans": 25.3, "revenuMedian": 21400, "tauxProprietaires": 53, "region": "Pays de la Loire", "zoneChalandise": 335, "departement": "Mayenne"},
		{"nom": "Le Mans", "population": 143813, "plus60ans": 23.8, "revenuMedian": 20500, "tauxProprietaires": 47, "region": "Pays de la Loire", "zoneChalandise": 425, "departement": "Sarthe"},
		{"nom": "Nantes", "population": 320732, "plus60ans": 20.5, "revenuMedian": 22100, "tauxProprietaires": 41, "region": "Pays de la Loire", "zoneChalandise": 485, "departement": "Loire-Atlantique"},
		{"nom": "Angers", "population": 154508, "plus60ans": 22.7, "revenuMedian": 21300, "tauxProprietaires": 44, "region": "Pays de la Loire", "zoneChalandise": 430, "departement": "Maine-et-Loire"},
		{"nom": "Les Sables-d'Olonne", "population": 45826, "plus60ans": 32.8, "revenuMedian": 21900, "tauxProprietaires": 61, "region": "Pays de la Loire", "zoneChalandise": 360, "departement": "Vendée"},
        
		# Provence-Alpes-Côte d'Azur
		{"nom": "Fréjus", "population": 54458, "plus60ans": 30.8, "revenuMedian": 21800, "tauxProprietaires": 59, "region": "Provence-Alpes-Côte d'Azur", "zoneChalandise": 365, "departement": "Var"},
		{"nom": "Hyères", "population": 56199, "plus60ans": 32.1, "revenuMedian": 21400, "tauxProprietaires": 62, "region": "Provence-Alpes-Côte d'Azur", "zoneChalandise": 370, "departement": "Var"},
		{"nom": "Nice", "population": 341522, "plus60ans": 26.7, "revenuMedian": 21200, "tauxProprietaires": 44, "region": "Provence-Alpes-Côte d'Azur", "zoneChalandise": 485, "departement": "Alpes-Maritimes"},
		{"nom": "Marseille", "population": 873076, "plus60ans": 21.8, "revenuMedian": 18900, "tauxProprietaires": 42, "region": "Provence-Alpes-Côte d'Azur", "zoneChalandise": 595, "departement": "Bouches-du-Rhône"},
		{"nom": "Toulon", "population": 176198, "plus60ans": 26.3, "revenuMedian": 19600, "tauxProprietaires": 46, "region": "Provence-Alpes-Côte d'Azur", "zoneChalandise": 440, "departement": "Var"},
		{"nom": "Aix-en-Provence", "population": 145721, "plus60ans": 22.9, "revenuMedian": 24800, "tauxProprietaires": 47, "region": "Provence-Alpes-Côte d'Azur", "zoneChalandise": 425, "departement": "Bouches-du-Rhône"},
		{"nom": "Cannes", "population": 74545, "plus60ans": 29.2, "revenuMedian": 23400, "tauxProprietaires": 48, "region": "Provence-Alpes-Côte d'Azur", "zoneChalandise": 370, "departement": "Alpes-Maritimes"},
        
		# Occitanie
		{"nom": "Toulouse", "population": 498003, "plus60ans": 18.9, "revenuMedian": 22400, "tauxProprietaires": 39, "region": "Occitanie", "zoneChalandise": 520, "departement": "Haute-Garonne"},
		{"nom": "Montpellier", "population": 299096, "plus60ans": 20.3, "revenuMedian": 20900, "tauxProprietaires": 38, "region": "Occitanie", "zoneChalandise": 475, "departement": "Hérault"},
		{"nom": "Nîmes", "population": 151001, "plus60ans": 25.1, "revenuMedian": 18600, "tauxProprietaires": 45, "region": "Occitanie", "zoneChalandise": 425, "departement": "Gard"},
		{"nom": "Perpignan", "population": 121934, "plus60ans": 26.8, "revenuMedian": 18500, "tauxProprietaires": 48, "region": "Occitanie", "zoneChalandise": 400, "departement": "Pyrénées-Orientales"},
		{"nom": "Béziers", "population": 77177, "plus60ans": 28.7, "revenuMedian": 18900, "tauxProprietaires": 51, "region": "Occitanie", "zoneChalandise": 365, "departement": "Hérault"},
        
		# Auvergne-Rhône-Alpes
		{"nom": "Lyon", "population": 522969, "plus60ans": 19.6, "revenuMedian": 22800, "tauxProprietaires": 37, "region": "Auvergne-Rhône-Alpes", "zoneChalandise": 530, "departement": "Rhône"},
		{"nom": "Grenoble", "population": 158454, "plus60ans": 20.8, "revenuMedian": 21400, "tauxProprietaires": 41, "region": "Auvergne-Rhône-Alpes", "zoneChalandise": 430, "departement": "Isère"},
		{"nom": "Annecy", "population": 128199, "plus60ans": 21.8, "revenuMedian": 26300, "tauxProprietaires": 52, "region": "Auvergne-Rhône-Alpes", "zoneChalandise": 410, "departement": "Haute-Savoie"},
		{"nom": "Clermont-Ferrand", "population": 147284, "plus60ans": 22.4, "revenuMedian": 21100, "tauxProprietaires": 43, "region": "Auvergne-Rhône-Alpes", "zoneChalandise": 420, "departement": "Puy-de-Dôme"},
	]
    
	df = pd.DataFrame(villes)
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
		'60+ (%)', '60+ (nb)', 'Revenu médian', 
		'Proprio (%)', 'Zone', 
		'Foyers pot.', 'Clients pot.'
	]
    
	# Style
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