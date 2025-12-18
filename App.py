import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(
	page_title="Analyse Marché - Nettoyage Poubelles",
	page_icon="🗑️",
	layout="wide",
	initial_sidebar_state="expanded"
)

# CSS personnalisé professionnel
st.markdown("""
<style>
	/* Design premium */
	.main-header {
		background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%);
		padding: 2.5rem;
		border-radius: 15px;
		color: white;
		margin-bottom: 2rem;
		box-shadow: 0 10px 30px rgba(0,0,0,0.2);
	}
	
	.priority-a {
		background: linear-gradient(135deg, #10b981 0%, #059669 100%);
		color: white;
		padding: 0.5rem 1rem;
		border-radius: 8px;
		font-weight: bold;
		display: inline-block;
	}
	
	.priority-b {
		background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
		color: white;
		padding: 0.5rem 1rem;
		border-radius: 8px;
		font-weight: bold;
		display: inline-block;
	}
	
	.priority-c {
		background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
		color: white;
		padding: 0.5rem 1rem;
		border-radius: 8px;
		font-weight: bold;
		display: inline-block;
	}
	
	.priority-d {
		background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
		color: white;
		padding: 0.5rem 1rem;
		border-radius: 8px;
		font-weight: bold;
		display: inline-block;
	}
	
	.stMetric {
		background: white;
		padding: 1rem;
		border-radius: 10px;
		box-shadow: 0 4px 6px rgba(0,0,0,0.1);
	}
	
	h1, h2, h3 {
		color: #1e3c72;
	}
</style>
""", unsafe_allow_html=True)

# Données des villes
@st.cache_data
def load_data():
	df = pd.read_csv('data.csv', sep=';')
	return df

def calculate_score(row):
	"""Calcul du score pondéré adapté au nettoyage de poubelles - favorise les périphéries"""
	
	# Pondérations adaptées (périphéries > centres-villes)
	poids_maisons = 0.40        # AUGMENTÉ - Critère principal pour périphéries
	poids_proprio = 0.25        # Stabilité clientèle
	poids_pop60 = 0.15          # RÉDUIT - Moins critique que le type d'habitat
	poids_revenu = 0.10         # Pouvoir d'achat
	poids_familles = 0.10       # AUGMENTÉ - Familles en périphérie
	# Population totale supprimée - favorise petites villes périphériques
    
	# Calcul des scores individuels
	score_maisons = min((row['pct_maison'] / 90) * 100, 100)
	score_proprio = min((row['tauxProprietaires'] / 70) * 100, 100)
	score_pop60 = min((row['plus60ans'] / 35) * 100, 100)
	score_revenu = min((row['revenuMedian'] / 27000) * 100, 100)
	score_familles = min((row['pct_30_44'] / 25) * 100, 100)
    
	# BONUS PÉRIPHÉRIE : Favorise zones pavillonnaires (>70% maisons)
	bonus_peripherie = 0
	if row['pct_maison'] > 80:
		bonus_peripherie = 15  # Bonus important pour zones très pavillonnaires
	elif row['pct_maison'] > 70:
		bonus_peripherie = 10  # Bonus moyen
	elif row['pct_maison'] > 60:
		bonus_peripherie = 5   # Petit bonus
    
	# PÉNALITÉ CENTRE-VILLE : Pénalise zones denses (>60% appartements)
	penalite_centre = 0
	if row['pct_appartement'] > 70:
		penalite_centre = -20  # Forte pénalité pour centres très denses
	elif row['pct_appartement'] > 60:
		penalite_centre = -15  # Pénalité moyenne
	elif row['pct_appartement'] > 50:
		penalite_centre = -10  # Petite pénalité
    
	# PÉNALITÉ GRANDE VILLE : Les très grandes villes = centres denses
	penalite_grande_ville = 0
	if row['population'] > 100000:
		penalite_grande_ville = -10  # Grandes villes = centres denses
	elif row['population'] > 50000:
		penalite_grande_ville = -5   # Villes moyennes
    
	# Score total pondéré avec bonus/pénalités
	score_base = (
		score_maisons * poids_maisons +
		score_proprio * poids_proprio +
		score_pop60 * poids_pop60 +
		score_revenu * poids_revenu +
		score_familles * poids_familles
	)
    
	score_total = score_base + bonus_peripherie + penalite_centre + penalite_grande_ville
    
	# Limiter entre 0 et 100
	score_total = max(0, min(100, score_total))
    
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

def calculate_revenue(row):
	"""Calcul du revenu annuel estimé"""
	prix_mensuel = 15  # €/mois par client
	revenu_annuel = row['clientsPotentiels'] * prix_mensuel * 12
	return revenu_annuel

def get_priority_level(score, revenue):
	"""Détermination du niveau de priorité"""
	if score >= 75 and revenue >= 50000:
		return "A"
	elif score >= 60 and revenue >= 30000:
		return "B"
	elif score >= 45:
		return "C"
	else:
		return "D"

def get_priority_label(priority):
	"""Label complet de priorité"""
	labels = {
		"A": "🟢 A - Priorité Maximale",
		"B": "🔵 B - Priorité Élevée",
		"C": "🟡 C - Potentiel Moyen",
		"D": "🔴 D - Faible Priorité"
	}
	return labels.get(priority, "N/A")

def get_saturation(row):
	"""Indicateur de saturation marché"""
	ratio = row['clientsPotentiels'] / row['population'] if row['population'] > 0 else 0
	if ratio > 0.05:
		return "🟢 Fort Potentiel"
	elif ratio > 0.03:
		return "🟡 Potentiel Moyen"
	else:
		return "🔴 Faible Potentiel"

# Fonctions utilitaires
def get_score_emoji(score):
	if score >= 80: return "🟢"
	elif score >= 60: return "🔵"
	elif score >= 40: return "🟡"
	else: return "🔴"

def score_to_rgb(score):
	red = int(255 * (100 - score) / 100)
	green = int(255 * score / 100)
	return [red, green, 0, 160]

# Chargement des données
df = load_data()

# Calcul du score et des foyers
df['score'] = df.apply(calculate_score, axis=1)
df[['foyersPotentiels', 'clientsPotentiels', 'personnes60plus']] = df.apply(calculate_foyers, axis=1)
df['revenuAnnuel'] = df.apply(calculate_revenue, axis=1)
df['priorite'] = df.apply(lambda row: get_priority_level(row['score'], row['revenuAnnuel']), axis=1)
df['saturation'] = df.apply(get_saturation, axis=1)

# Header professionnel
st.markdown("""
<div class="main-header">
	<h1>🗑️ Analyse de Marché - Nettoyage de Poubelles</h1>
	<p style="font-size: 1.2rem; margin-top: 0.5rem;">Outil d'aide à la décision pour franchisés</p>
	<p style="font-size: 0.9rem; opacity: 0.9;">36,744 villes analysées en France</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Filtres
st.sidebar.header("🔍 Filtres de Recherche")

search_term = st.sidebar.text_input("🔎 Rechercher", placeholder="Ville ou département...")

region_filter = st.sidebar.selectbox(
	"Région",
	["Toutes"] + sorted(df['region'].unique().tolist())
)

priority_filter = st.sidebar.multiselect(
	"Niveau de Priorité",
	["A", "B", "C", "D"],
	default=["A", "B"]
)

min_population = st.sidebar.number_input(
	"Population minimale",
	min_value=0,
	max_value=int(df['population'].max()),
	value=3000,
	step=1000
)

min_revenue = st.sidebar.number_input(
	"Revenu annuel minimum (€)",
	min_value=0,
	max_value=int(df['revenuAnnuel'].max()),
	value=20000,
	step=5000
)

min_score = st.sidebar.slider(
	"Score minimal",
	min_value=0,
	max_value=100,
	value=50,
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

if priority_filter:
	filtered_df = filtered_df[filtered_df['priorite'].isin(priority_filter)]

filtered_df = filtered_df[filtered_df['population'] >= min_population]
filtered_df = filtered_df[filtered_df['revenuAnnuel'] >= min_revenue]
filtered_df = filtered_df[filtered_df['score'] >= min_score]

# Tri
sort_by = st.sidebar.selectbox(
	"Trier par",
	["Revenu Annuel", "Score", "Clients potentiels", "Population totale"],
	index=0
)

sort_order = st.sidebar.radio("Ordre", ["Décroissant", "Croissant"])

sort_mapping = {
	"Revenu Annuel": "revenuAnnuel",
	"Score": "score",
	"Clients potentiels": "clientsPotentiels",
	"Population totale": "population"
}

filtered_df = filtered_df.sort_values(
	by=sort_mapping[sort_by],
	ascending=(sort_order == "Croissant")
)

# Dashboard principal
st.subheader("📊 Vue d'Ensemble du Marché")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
	st.metric("🏙️ Villes Sélectionnées", f"{len(filtered_df):,}")

with col2:
	avg_revenue = filtered_df['revenuAnnuel'].mean() if len(filtered_df) > 0 else 0
	st.metric("💰 Revenu Moyen", f"{avg_revenue:,.0f} €/an")

with col3:
	total_revenue = filtered_df['revenuAnnuel'].sum()
	st.metric("💵 Revenu Total", f"{total_revenue:,.0f} €/an")

with col4:
	priority_a_count = len(filtered_df[filtered_df['priorite'] == 'A'])
	st.metric("🟢 Villes Priorité A", f"{priority_a_count:,}")

with col5:
	total_clients = filtered_df['clientsPotentiels'].sum()
	st.metric("👥 Clients Totaux", f"{total_clients:,}")

st.markdown("---")

# Graphiques visuels
if len(filtered_df) > 0:
	st.subheader("📈 Analyse Visuelle")
	
	tab1, tab2, tab3 = st.tabs(["💰 Top Revenus", "🎯 Distribution Priorités", "🗺️ Analyse Régionale"])
	
	with tab1:
		st.markdown("### Top 20 Villes par Revenu Annuel Potentiel")
		top_revenue = filtered_df.nlargest(20, 'revenuAnnuel')[['nom', 'revenuAnnuel', 'clientsPotentiels', 'priorite']].reset_index(drop=True)
		
		fig = px.bar(
			top_revenue,
			x='nom',
			y='revenuAnnuel',
			color='priorite',
			color_discrete_map={'A': '#10b981', 'B': '#3b82f6', 'C': '#f59e0b', 'D': '#ef4444'},
			title="Revenu Annuel Potentiel par Ville",
			labels={'revenuAnnuel': 'Revenu Annuel (€)', 'nom': 'Ville'},
			height=500
		)
		fig.update_layout(showlegend=True, xaxis_tickangle=-45)
		st.plotly_chart(fig, use_container_width=True)
	
	with tab2:
		st.markdown("### Distribution des Villes par Niveau de Priorité")
		priority_counts = filtered_df['priorite'].value_counts().reset_index()
		priority_counts.columns = ['Priorité', 'Nombre']
		
		fig = px.pie(
			priority_counts,
			values='Nombre',
			names='Priorité',
			color='Priorité',
			color_discrete_map={'A': '#10b981', 'B': '#3b82f6', 'C': '#f59e0b', 'D': '#ef4444'},
			title="Répartition des Villes par Priorité",
			height=500
		)
		st.plotly_chart(fig, use_container_width=True)
		
		col1, col2 = st.columns(2)
		with col1:
			st.dataframe(priority_counts, use_container_width=True)
		with col2:
			priority_revenue = filtered_df.groupby('priorite')['revenuAnnuel'].sum().reset_index()
			priority_revenue.columns = ['Priorité', 'Revenu Total (€)']
			priority_revenue['Revenu Total (€)'] = priority_revenue['Revenu Total (€)'].apply(lambda x: f"{x:,.0f} €")
			st.dataframe(priority_revenue, use_container_width=True)
	
	with tab3:
		st.markdown("### Analyse par Région")
		region_stats = filtered_df.groupby('region').agg({
			'revenuAnnuel': 'sum',
			'clientsPotentiels': 'sum',
			'nom': 'count'
		}).reset_index()
		region_stats.columns = ['Région', 'Revenu Total', 'Clients Totaux', 'Nb Villes']
		region_stats = region_stats.sort_values('Revenu Total', ascending=False)
		
		fig = px.bar(
			region_stats.head(15),
			x='Région',
			y='Revenu Total',
			title="Top 15 Régions par Revenu Potentiel",
			labels={'Revenu Total': 'Revenu Annuel Total (€)'},
			height=500
		)
		fig.update_layout(xaxis_tickangle=-45)
		st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Plan de déploiement
if len(filtered_df) > 0:
	st.subheader("🚀 Plan de Déploiement Recommandé")
	
	priority_a = filtered_df[filtered_df['priorite'] == 'A']
	priority_b = filtered_df[filtered_df['priorite'] == 'B']
	priority_c = filtered_df[filtered_df['priorite'] == 'C']
	
	col1, col2, col3 = st.columns(3)
	
	with col1:
		st.markdown("### 📅 Phase 1 (0-6 mois)")
		st.markdown(f"**Villes Priorité A** : {len(priority_a)}")
		st.markdown(f"**Investissement** : {len(priority_a) * 25000:,} €")
		st.markdown(f"**Revenu Annuel** : {priority_a['revenuAnnuel'].sum():,.0f} €")
		st.markdown(f"**ROI Estimé** : 12-18 mois")
	
	with col2:
		st.markdown("### 📅 Phase 2 (6-12 mois)")
		st.markdown(f"**Villes Priorité B** : {len(priority_b)}")
		st.markdown(f"**Investissement** : {len(priority_b) * 25000:,} €")
		st.markdown(f"**Revenu Annuel** : {priority_b['revenuAnnuel'].sum():,.0f} €")
		st.markdown(f"**ROI Estimé** : 18-24 mois")
	
	with col3:
		st.markdown("### 📅 Phase 3 (12-24 mois)")
		st.markdown(f"**Villes Priorité C** : {len(priority_c)}")
		st.markdown(f"**Investissement** : {len(priority_c) * 25000:,} €")
		st.markdown(f"**Revenu Annuel** : {priority_c['revenuAnnuel'].sum():,.0f} €")
		st.markdown(f"**ROI Estimé** : 24-36 mois")

st.markdown("---")

# Tableau des résultats
st.subheader("📋 Résultats Détaillés")

if len(filtered_df) > 0:
	display_df = filtered_df[[
		'nom', 'departement', 'region', 'priorite', 'score', 
		'revenuAnnuel', 'clientsPotentiels', 'population',
		'pct_maison', 'tauxProprietaires', 'plus60ans', 'saturation'
	]].copy()
	
	display_df.columns = [
		'Ville', 'Département', 'Région', 'Priorité', 'Score',
		'Revenu Annuel (€)', 'Clients', 'Population',
		'% Maisons', '% Proprio', '% 60+', 'Saturation'
	]
	
	# Affichage sans style si trop de lignes
	if len(display_df) > 5000:
		st.info(f"⚠️ Affichage de {len(display_df):,} villes. Le style est désactivé pour améliorer les performances.")
		st.dataframe(display_df, use_container_width=True, height=600)
	else:
		st.dataframe(display_df, use_container_width=True, height=600)
	
	# Bouton de téléchargement
	csv = display_df.to_csv(index=False).encode('utf-8')
	st.download_button(
		label="📥 Télécharger les résultats (CSV)",
		data=csv,
		file_name='analyse_villes_franchise.csv',
		mime='text/csv',
	)
else:
	st.warning("⚠️ Aucune ville ne correspond aux critères de filtrage")

# Méthodologie
st.markdown("---")
with st.expander("📊 Méthodologie & Calculs", expanded=False):
	st.markdown("""
	### Scoring (0-100 points) - Optimisé pour Périphéries
	
	**Pondération adaptée (favorise banlieues/périphéries) :**
	- 🏠 **40%** % de maisons (AUGMENTÉ - zones pavillonnaires)
	- 👤 **25%** Taux de propriétaires (stabilité)
	- 🎯 **15%** Population 60+ ans (cible principale)
	- 💰 **10%** Revenu médian (capacité à payer)
	- 👨‍👩‍👧 **10%** Familles 30-44 ans (AUGMENTÉ - familles en périphérie)
	
	**🟢 BONUS PÉRIPHÉRIE (zones pavillonnaires) :**
	- **+15 points** si >80% de maisons (zones très pavillonnaires)
	- **+10 points** si 70-80% de maisons
	- **+5 points** si 60-70% de maisons
	
	**🔴 PÉNALITÉS CENTRES-VILLES (zones denses) :**
	- **-20 points** si >70% d'appartements (centres très denses)
	- **-15 points** si 60-70% d'appartements
	- **-10 points** si 50-60% d'appartements
	- **-10 points** si population >100,000 (grandes villes denses)
	- **-5 points** si population 50,000-100,000
	
	**Pourquoi favoriser les périphéries ?**
	- ✅ **Plus de maisons** = poubelles individuelles (vs collectives)
	- ✅ **Meilleure circulation** = accès facile pour le service
	- ✅ **Zones pavillonnaires** = clients propriétaires stables
	- ❌ **Centres-villes** = appartements, poubelles collectives, circulation difficile
	
	### Calcul du Revenu Annuel
	
	**Formule** : Clients Potentiels × 15€/mois × 12 mois
	- **Prix** : 15€/mois par client
	- **Clients** : 10-15% des foyers de 60+ ans
	
	### Niveaux de Priorité
	
	- **A (Priorité Maximale)** : Score ≥ 75 ET Revenu ≥ 50,000€
	- **B (Priorité Élevée)** : Score ≥ 60 ET Revenu ≥ 30,000€
	- **C (Potentiel Moyen)** : Score ≥ 45
	- **D (Faible Priorité)** : Score < 45
	
	### Investissement Franchise
	
	- **Coût par ville** : 25,000€ (équipement, marketing, formation)
	- **ROI Priorité A** : 12-18 mois
	- **ROI Priorité B** : 18-24 mois
	- **ROI Priorité C** : 24-36 mois
	""")

# Footer
st.markdown("---")
st.markdown("💡 **Astuce** : Utilisez les filtres pour affiner votre stratégie de déploiement par région ou niveau de priorité")