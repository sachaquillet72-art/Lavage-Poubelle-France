import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

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
	"""Calcul du score pondéré adapté au nettoyage de poubelles"""
	
	# Pondérations adaptées au nettoyage de poubelles
	poids_maisons = 0.35        # Critère principal : poubelles individuelles
	poids_proprio = 0.25        # Stabilité clientèle, investissement entretien
	poids_pop60 = 0.20          # Cible principale, besoin réel
	poids_revenu = 0.10         # Pouvoir d'achat
	poids_pop = 0.05            # Taille du marché
	poids_familles = 0.05       # Familles avec enfants, besoin d'hygiène
    
	# Calcul des scores individuels (normalisés sur 100)
	score_maisons = min((row['pct_maison'] / 90) * 100, 100)
	score_proprio = min((row['tauxProprietaires'] / 70) * 100, 100)
	score_pop60 = min((row['plus60ans'] / 35) * 100, 100)
	score_revenu = min((row['revenuMedian'] / 27000) * 100, 100)
	score_pop = min((row['population'] / 150000) * 100, 100)
	score_familles = min((row['pct_30_44'] / 25) * 100, 100)
    
	# Score total pondéré
	score_total = (
		score_maisons * poids_maisons +
		score_proprio * poids_proprio +
		score_pop60 * poids_pop60 +
		score_revenu * poids_revenu +
		score_pop * poids_pop +
		score_familles * poids_familles
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

# Fonctions utilitaires
def get_score_emoji(score):
	"""Retourne l'emoji selon le score"""
	if score >= 80: return "🟢"
	elif score >= 60: return "🔵"
	elif score >= 40: return "🟡"
	else: return "🔴"

def score_to_rgb(score):
	"""Convertit score en couleur RGB pour la carte"""
	red = int(255 * (100 - score) / 100)
	green = int(255 * score / 100)
	return [red, green, 0, 160]

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
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
	st.metric("🏙️ Villes analysées", len(filtered_df))

with col2:
	avg_score = round(filtered_df['score'].mean()) if len(filtered_df) > 0 else 0
	st.metric("⭐ Score moyen", f"{avg_score}/100")

with col3:
	total_clients = filtered_df['clientsPotentiels'].sum()
	st.metric("👥 Clients potentiels", f"{total_clients:,}")

with col4:
	if len(filtered_df) > 0:
		best_city = filtered_df.nlargest(1, 'score').iloc[0]
		st.metric("🥇 Meilleure ville", best_city['nom'], f"{best_city['score']}/100")
	else:
		st.metric("🥇 Meilleure ville", "N/A")

with col5:
	total_pop = filtered_df['population'].sum()
	st.metric("👥 Population totale", f"{total_pop:,}")

# Classement des meilleures villes
if len(filtered_df) > 0:
	st.subheader("🏆 Top 20 des Meilleures Villes")
	
	col1, col2 = st.columns(2)
	
	with col1:
		st.markdown("### 📊 Par Score Global")
		top_score = filtered_df.nlargest(min(20, len(filtered_df)), 'score')[['nom', 'score', 'departement', 'region']].reset_index(drop=True)
		for idx, row in top_score.iterrows():
			emoji = get_score_emoji(row['score'])
			st.markdown(f"{emoji} **{idx+1}. {row['nom']}** ({row['departement']}) - Score: **{row['score']}/100**")
	
	with col2:
		st.markdown("### 👥 Par Clients Potentiels")
		top_clients = filtered_df.nlargest(min(20, len(filtered_df)), 'clientsPotentiels')[['nom', 'clientsPotentiels', 'departement']].reset_index(drop=True)
		for idx, row in top_clients.iterrows():
			st.markdown(f"**{idx+1}. {row['nom']}** ({row['departement']}) - **{row['clientsPotentiels']:,}** clients")

st.markdown("---")

# Carte interactive
if len(filtered_df) > 0 and len(filtered_df) <= 10000:
	st.subheader("🗺️ Carte Interactive des Villes")
	
	# Préparer les données pour la carte
	map_data = filtered_df[['lat', 'lon', 'nom', 'score', 'departement']].copy()
	map_data['color'] = map_data['score'].apply(score_to_rgb)
	
	# Créer la carte pydeck
	layer = pdk.Layer(
		'ScatterplotLayer',
		data=map_data,
		get_position='[lon, lat]',
		get_color='color',
		get_radius=2000,
		pickable=True,
	)
	
	view_state = pdk.ViewState(
		latitude=46.603354,  # Centre de la France
		longitude=1.888334,
		zoom=5,
		pitch=0,
	)
	
	st.pydeck_chart(pdk.Deck(
		layers=[layer],
		initial_view_state=view_state,
		tooltip={"text": "{nom} ({departement})\nScore: {score}/100"}
	))
	
	st.caption("💡 Survolez les points pour voir les détails. Vert = score élevé, Rouge = score bas")
elif len(filtered_df) > 10000:
	st.info("⚠️ Carte désactivée pour plus de 10,000 villes. Utilisez les filtres pour réduire le nombre de résultats.")

st.markdown("---")

# Dashboard Analytique
if len(filtered_df) > 0:
	st.subheader("📊 Analyse par Zones à Fort Potentiel")
	
	tab1, tab2, tab3 = st.tabs(["🌍 Par Région", "📍 Par Département", "📈 Synthèse"])
	
	with tab1:
		st.markdown("### Clients Potentiels par Région")
		
		# Agrégation par région
		region_stats = filtered_df.groupby('region').agg({
			'clientsPotentiels': 'sum',
			'population': 'sum',
			'score': 'mean',
			'nom': 'count'
		}).round(0)
		region_stats.columns = ['Clients Potentiels', 'Population', 'Score Moyen', 'Nb Villes']
		region_stats = region_stats.sort_values('Clients Potentiels', ascending=False)
		
		col1, col2 = st.columns([2, 1])
		
		with col1:
			st.bar_chart(region_stats['Clients Potentiels'])
		
		with col2:
			st.dataframe(
				region_stats.style.format({
					'Clients Potentiels': '{:,.0f}',
					'Population': '{:,.0f}',
					'Score Moyen': '{:.1f}',
					'Nb Villes': '{:.0f}'
				}),
				use_container_width=True
			)
	
	with tab2:
		st.markdown("### Top 15 Départements à Fort Potentiel")
		
		# Agrégation par département
		dept_stats = filtered_df.groupby('departement').agg({
			'clientsPotentiels': 'sum',
			'score': 'mean',
			'nom': 'count',
			'population': 'sum'
		}).round(0)
		dept_stats.columns = ['Clients Potentiels', 'Score Moyen', 'Nb Villes', 'Population']
		top_depts = dept_stats.nlargest(15, 'Clients Potentiels')
		
		col1, col2 = st.columns([2, 1])
		
		with col1:
			st.bar_chart(top_depts['Clients Potentiels'])
		
		with col2:
			st.dataframe(
				top_depts.style.format({
					'Clients Potentiels': '{:,.0f}',
					'Score Moyen': '{:.1f}',
					'Nb Villes': '{:.0f}',
					'Population': '{:,.0f}'
				}),
				use_container_width=True
			)
	
	with tab3:
		st.markdown("### Synthèse des Zones Prioritaires")
		
		col1, col2, col3 = st.columns(3)
		
		with col1:
			if len(region_stats) > 0:
				best_region = region_stats.index[0]
				best_region_clients = region_stats.iloc[0]['Clients Potentiels']
				st.metric(
					"🏆 Meilleure Région",
					best_region,
					f"{best_region_clients:,.0f} clients"
				)
		
		with col2:
			if len(top_depts) > 0:
				best_dept = top_depts.index[0]
				best_dept_clients = top_depts.iloc[0]['Clients Potentiels']
				st.metric(
					"🏆 Meilleur Département",
					best_dept,
					f"{best_dept_clients:,.0f} clients"
				)
		
		with col3:
			avg_clients_per_city = filtered_df['clientsPotentiels'].mean()
			st.metric(
				"📊 Moyenne par Ville",
				f"{avg_clients_per_city:,.0f}",
				"clients potentiels"
			)
		
		st.markdown("---")
		
		# Recommandations
		st.markdown("### 💡 Recommandations Stratégiques")
		
		if len(region_stats) > 0 and len(top_depts) > 0:
			top_3_regions = region_stats.head(3)
			top_3_depts = top_depts.head(3)
			
			st.markdown(f"""
			**Zones prioritaires pour le déploiement :**
			
			🎯 **Régions à cibler en priorité :**
			1. **{top_3_regions.index[0]}** - {top_3_regions.iloc[0]['Clients Potentiels']:,.0f} clients potentiels ({top_3_regions.iloc[0]['Nb Villes']:.0f} villes)
			2. **{top_3_regions.index[1] if len(top_3_regions) > 1 else 'N/A'}** - {top_3_regions.iloc[1]['Clients Potentiels']:,.0f if len(top_3_regions) > 1 else 0} clients potentiels
			3. **{top_3_regions.index[2] if len(top_3_regions) > 2 else 'N/A'}** - {top_3_regions.iloc[2]['Clients Potentiels']:,.0f if len(top_3_regions) > 2 else 0} clients potentiels
			
			📍 **Départements à fort ROI :**
			1. **{top_3_depts.index[0]}** - {top_3_depts.iloc[0]['Clients Potentiels']:,.0f} clients (Score moyen: {top_3_depts.iloc[0]['Score Moyen']:.1f}/100)
			2. **{top_3_depts.index[1] if len(top_3_depts) > 1 else 'N/A'}** - {top_3_depts.iloc[1]['Clients Potentiels']:,.0f if len(top_3_depts) > 1 else 0} clients
			3. **{top_3_depts.index[2] if len(top_3_depts) > 2 else 'N/A'}** - {top_3_depts.iloc[2]['Clients Potentiels']:,.0f if len(top_3_depts) > 2 else 0} clients
			""")

st.markdown("---")

# Méthodologie
with st.expander("📊 Méthodologie de scoring", expanded=False):
	st.markdown("""
	**Pondération du score (adaptée au nettoyage de poubelles) :**
	- 🏠 **35%** % de maisons (poubelles individuelles vs collectives)
	- 👤 **25%** Taux de propriétaires (stabilité, investissement entretien)
	- 🎯 **20%** Population 60+ ans (cible principale, besoin réel)
	- 💰 **10%** Revenu médian (capacité à payer le service)
	- 👥 **5%** Population totale (taille du marché)
	- 👨‍👩‍👧 **5%** Familles 30-44 ans (enfants, besoin d'hygiène)
    
	**Pourquoi ces critères ?**
	- **Maisons** : Les maisons ont des poubelles individuelles (vs poubelles collectives en appartement)
	- **Propriétaires** : Investissent plus dans l'entretien de leur propriété
	- **60+ ans** : Difficulté à nettoyer, pouvoir d'achat, besoin réel
	- **Familles** : Plus de déchets, valorisent l'hygiène
    
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