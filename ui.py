import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import io
import zipfile
import base64
import os

from generate_preference import generate_preferences, save_to_csv
from mariage_stable_mesure import (
    read_instance, compute_all_measures, compute_ranks, mariage_stable
)

from test_mesures_graph import test_measures_with_graphs

# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================
st.set_page_config(
    page_title="Mariage Stable - Simulation Animée",
    layout="wide"
)

# ============================================================
# CSS POUR L'EFFET DE FLOU (BLUR)
# ============================================================
st.markdown(
    """
    <style>
    div[data-testid="stDialog"] {
        backdrop-filter: blur(5px) !important;
        background-color: rgba(0, 0, 0, 0.4) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# GESTION DU STATE (Sessions)
# ============================================================
if 'bench_viewer_active' not in st.session_state:
    st.session_state['bench_viewer_active'] = False
if 'bench_data' not in st.session_state:
    st.session_state['bench_data'] = []
if 'current_bench_index' not in st.session_state:
    st.session_state['current_bench_index'] = 0

# Initialisation des variables de résultats pour la persistance
if "engaged_final" not in st.session_state:
    st.session_state["engaged_final"] = None
if "results" not in st.session_state:
    st.session_state["results"] = None
if "figures" not in st.session_state:
    st.session_state["figures"] = None
if "prefs_students" not in st.session_state:
    st.session_state["prefs_students"] = None
if "prefs_schools" not in st.session_state:
    st.session_state["prefs_schools"] = None
if "simulation_history" not in st.session_state:
    st.session_state["simulation_history"] = []  # Pour stocker les logs de l'animation

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def parse_benchmark_csv(filename):
    """Lit le CSV et retourne une liste d'instances."""
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        st.error(f"Le fichier {filename} est introuvable.")
        return []

    instances = []
    current_students = {}
    current_schools = {}
    processing_schools = False

    for _, row in df.iterrows():
        row_type = row['Type'].strip()
        name = row['Nom'].strip()
        prefs = [p.strip() for p in str(row['Préférences']).split('-')]

        if row_type == 'Etudiant':
            if processing_schools:
                instances.append((current_students, current_schools))
                current_students = {}
                current_schools = {}
                processing_schools = False
            current_students[name] = prefs
        
        elif row_type == 'Ecole':
            processing_schools = True
            current_schools[name] = prefs

    if current_students and current_schools:
        instances.append((current_students, current_schools))
        
    return instances

def render_history_log():
    """Réaffiche l'historique de la simulation stocké en mémoire."""
    if st.session_state["simulation_history"]:
        st.subheader("Déroulement pas à pas (Historique)")
        steps_container = st.container()
        with steps_container:
            for item_type, content in st.session_state["simulation_history"]:
                if item_type == "header":
                    st.markdown(content)
                elif item_type == "success":
                    st.success(content)
                elif item_type == "warning":
                    st.warning(content)
                elif item_type == "error":
                    st.error(content)
                elif item_type == "markdown":
                    st.markdown(content)
                elif item_type == "dataframe":
                    st.dataframe(content, use_container_width=True)

# ============================================================
# BOITE DE DIALOGUE (MODALE) POUR LE BENCHMARK
# ============================================================
@st.dialog("Visualiseur d'Instances Benchmark", width="large")
def show_benchmark_modal():
    if not st.session_state['bench_data']:
        st.warning("Aucune donnée à afficher.")
        if st.button("Fermer"):
            st.session_state['bench_viewer_active'] = False
            st.rerun()
        return

    total = len(st.session_state['bench_data'])
    idx = st.session_state['current_bench_index']
    
    col_nav1, col_nav2, col_nav3, col_close = st.columns([1, 2, 1, 1])
    
    with col_nav1:
        if st.button("⬅️ Précédent", disabled=(idx == 0)):
            st.session_state['current_bench_index'] -= 1
            st.rerun()

    with col_nav2:
        st.markdown(f"<h4 style='text-align: center;'>Instance {idx + 1} / {total}</h4>", unsafe_allow_html=True)

    with col_nav3:
        if st.button("Suivant ➡️", disabled=(idx == total - 1)):
            st.session_state['current_bench_index'] += 1
            st.rerun()
            
    with col_close:
        if st.button("❌ Fermer", type="primary"):
            st.session_state['bench_viewer_active'] = False
            st.rerun()

    st.markdown("---")
    curr_students, curr_schools = st.session_state['bench_data'][idx]
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown("#### 👩‍🎓 Préférences Étudiants")
        df_students = pd.DataFrame([
            {"Nom": name, "Préférences": " → ".join(prefs)} 
            for name, prefs in curr_students.items()
        ])
        st.dataframe(df_students, use_container_width=True)
    
    with col_v2:
        st.markdown("#### 🏫 Préférences Écoles")
        df_schools = pd.DataFrame([
            {"Nom": name, "Préférences": " → ".join(prefs)} 
            for name, prefs in curr_schools.items()
        ])
        st.dataframe(df_schools, use_container_width=True)


# ============================================================
# INTERFACE PRINCIPALE
# ============================================================

st.title("Simulation animée de l'algorithme du mariage stable (Gale–Shapley)")
st.markdown(""" 
Ce projet simule pas à pas le processus d'appariement entre étudiants et écoles selon leurs préférences respectives.
""")

# ============================================================
# BARRE LATÉRALE
# ============================================================
st.sidebar.header("Paramètres Simulation")
n_entites = st.sidebar.slider("Nombre d'entités ", 2, 50, 5)
nb_tests = st.sidebar.slider("Nombre d'instances aléatoires", 1, 50, 5)
speed = st.sidebar.slider("Vitesse d'exécution (démo)", 0.0, 5.0, 1.0)
start_btn = st.sidebar.button("Générer et exécuter l'algorithme")

st.sidebar.markdown("---")
st.sidebar.header("Visualiseur Benchmark")

if st.sidebar.button("📂 Charger instances benchmark"):
    instances = parse_benchmark_csv("instances_bench_temp.csv")
    if instances:
        st.session_state['bench_data'] = instances
        st.session_state['bench_viewer_active'] = True
        st.session_state['current_bench_index'] = 0
    else:
        st.sidebar.warning("Aucune instance trouvée (lancez une simulation d'abord).")


# ============================================================
# VERSION ANIMÉE DE L'ALGORITHME
# ============================================================

def mariage_stable_animated(pref_student, pref_school, speed=0.5):
    """Exécute l'algo, anime l'UI et enregistre l'historique."""
    steps_container = st.container()
    free_students = list(pref_student.keys())
    proposals = {p: [] for p in pref_student}
    engaged = {s: None for s in pref_school}
    
    history = [] # Pour sauvegarder les étapes

    step = 1
    while free_students:
        current_student = free_students[0]
        next_school = None

        for school in pref_student[current_student]:
            if school not in proposals[current_student]:
                next_school = school
                break

        if next_school is None:
            free_students.pop(0)
            continue

        proposals[current_student].append(next_school)
        current_eng = engaged[next_school]

        # Affichage & Enregistrement
        header_txt = f"### Étape {step}"
        sub_txt = f"👩‍🎓 **{current_student}** propose à 🏫 **{next_school}**"
        
        with steps_container:
            st.markdown(header_txt)
            st.markdown(sub_txt)
        
        history.append(("header", header_txt))
        history.append(("markdown", sub_txt))

        if current_eng is None:
            engaged[next_school] = current_student
            free_students.pop(0)
            msg = f"✅ {next_school} accepte temporairement {current_student}"
            with steps_container:
                st.success(msg)
            history.append(("success", msg))
        else:
            rank_new = pref_school[next_school].index(current_student)
            rank_old = pref_school[next_school].index(current_eng)
            if rank_new < rank_old:
                engaged[next_school] = current_student
                free_students.pop(0)
                free_students.append(current_eng)
                msg = f"⚖️ {next_school} préfère {current_student} à {current_eng} → {current_eng} redevient libre"
                with steps_container:
                    st.warning(msg)
                history.append(("warning", msg))
            else:
                msg = f"❌ {next_school} rejette {current_student} (préférence pour {current_eng})"
                with steps_container:
                    st.error(msg)
                history.append(("error", msg))

        with steps_container:
            st.markdown("#### Engagements actuels :")
            df = pd.DataFrame([{"École": e, "Étudiant affecté": engaged[e] or "—"} for e in engaged])
            st.dataframe(df, use_container_width=True)
            st.markdown("---")
        
        history.append(("markdown", "#### Engagements actuels :"))
        history.append(("dataframe", df))
        history.append(("markdown", "---"))

        step += 1
        time.sleep(speed)

    return engaged, history


# ============================================================
# APPEL DE LA MODALE (Si active)
# ============================================================
if st.session_state['bench_viewer_active']:
    show_benchmark_modal()


# ============================================================
# EXÉCUTION DE LA SIMULATION (CALCUL)
# ============================================================
if start_btn:
    st.empty()
    st.info("Simulation en cours...")

    # 1. Génération Instance Unique
    students, schools, prefs_students, prefs_schools = generate_preferences(n_entites, n_entites)
    save_to_csv(students, schools, prefs_students, prefs_schools, "instance_temp.csv")
    
    st.session_state["prefs_students"] = prefs_students
    st.session_state["prefs_schools"] = prefs_schools

    # 2. Animation (s'affiche en direct + enregistre l'historique)
    st.subheader("Déroulement pas à pas")
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(pd.DataFrame([{"Étudiant": s, "Préférences": " → ".join(prefs_students[s])} for s in prefs_students]))
    with col2:
        st.dataframe(pd.DataFrame([{"École": e, "Préférences": " → ".join(prefs_schools[e])} for e in prefs_schools]))
    
    engaged, history = mariage_stable_animated(prefs_students, prefs_schools, speed)
    st.session_state["simulation_history"] = history  # Sauvegarde pour le rechargement
    
    # 3. Calculs finaux
    results = compute_all_measures(prefs_students, prefs_schools, engaged)
    st.session_state["engaged_final"] = engaged
    st.session_state["results"] = results

    # 4. Benchmark
    if os.path.exists("instances_bench_temp.csv"):
        try:
            os.remove("instances_bench_temp.csv")
        except Exception:
            pass

    with st.spinner("Génération des graphiques (Benchmark)..."):
        fig1, fig2, fig3 = test_measures_with_graphs(
            nb_tests=nb_tests,
            n_students=n_entites,
            n_schools=n_entites
        )
        st.session_state["figures"] = (fig1, fig2, fig3)
    
    st.success("✅ Simulation terminée !")


# ============================================================
# AFFICHAGE DES RÉSULTATS (PERSISTANT)
# ============================================================
if st.session_state["engaged_final"] is not None and st.session_state["results"] is not None:
    
    # Si on n'est PAS en train de lancer l'animation (c-à-d au rechargement de page)
    # on réaffiche l'historique pour qu'il ne disparaisse pas.
    if not start_btn:
        render_history_log()

    engaged_final = st.session_state["engaged_final"]
    results = st.session_state["results"]
    
    st.markdown("---")
    st.subheader("Résultat final du mariage stable")
    st.table(pd.DataFrame([{"École": e, "Étudiant affecté": engaged_final[e]} for e in engaged_final]))

    st.markdown("### 📊 Mesures globales de satisfaction")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Rang moyen étudiants", f"{results['avg_rank_students']:.2f}")
    with col2:
        st.metric("Rang moyen écoles", f"{results['avg_rank_schools']:.2f}")

    st.markdown("---")
    col3, col4, col5 = st.columns(3)
    with col3:
        st.metric("Welfare total", f"{results['welfare']:.2f}")
    with col4:
        st.metric("Coût égalitaire", f"{results['egalitarian_cost']}")
    with col5:
        pareto_text = "✅ Oui" if results["pareto_optimal"] else "❌ Non"
        st.metric("Pareto-optimalité", pareto_text)

    if st.session_state["figures"]:
        st.markdown("---")
        st.subheader("📊 Analyse sur plusieurs instances (tests aléatoires)")
        
        fig1, fig2, fig3 = st.session_state["figures"]
        st.pyplot(fig1)
        st.pyplot(fig2)
        st.pyplot(fig3)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for i, (fig, name) in enumerate(zip(
                [fig1, fig2, fig3],
                ["rang_moyen.png", "welfare.png", "cout_egalitaire.png"]
            )):
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
                zip_file.writestr(name, buf.getvalue())
        zip_buffer.seek(0)

        st.write("---")
        st.markdown("#### Exporter les résultats")

        df_result = pd.DataFrame(
            [{"École": e, "Étudiant affecté": engaged_final[e]} for e in engaged_final]
        )
        csv_result = df_result.to_csv(index=False).encode("utf-8")
        b64_csv_result = base64.b64encode(csv_result).decode()
        href_result = (
            f'<a href="data:text/csv;base64,{b64_csv_result}" '
            'download="resultats_mariage_stable.csv" '
            'style="display:inline-block;background-color:#0078ff;color:white;'
            'padding:10px 18px;border-radius:8px;text-decoration:none;margin:6px;">'
            '📥 Télécharger le résultat final (CSV)</a>'
        )

        results_df = pd.DataFrame([results])
        csv_measures = results_df.to_csv(index=False).encode("utf-8")
        b64_csv_measures = base64.b64encode(csv_measures).decode()
        href_measures = (
            f'<a href="data:text/csv;base64,{b64_csv_measures}" '
            'download="mesures_mariage_stable.csv" '
            'style="display:inline-block;background-color:#20bf55;color:white;'
            'padding:10px 18px;border-radius:8px;text-decoration:none;margin:6px;">'
            '📊 Télécharger les mesures globales (CSV)</a>'
        )

        zip_data = zip_buffer.getvalue()
        b64_zip = base64.b64encode(zip_data).decode()
        href_zip = (
            f'<a href="data:application/zip;base64,{b64_zip}" '
            'download="graphiques_mariage_stable.zip" '
            'style="display:inline-block;background-color:#ff7b00;color:white;'
            'padding:10px 18px;border-radius:8px;text-decoration:none;margin:6px;">'
            '📦 Télécharger les 3 graphiques (.zip)</a>'
        )

        html_block = f"""
        <div style="text-align:center;">
            {href_result}
            {href_measures}
            {href_zip}
        </div>
        """
        st.markdown(html_block, unsafe_allow_html=True)

elif not start_btn and not st.session_state.get('bench_viewer_active', False):
    st.info("👉 Choisis les paramètres à gauche puis clique sur **Générer et exécuter l'algorithme**.")