import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import io
import zipfile
import numpy as np

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

st.title("Simulation animée de l'algorithme du mariage stable (Gale–Shapley)")
st.markdown(""" 
Ce projet simule pas à pas le processus d'appariement entre étudiants et écoles selon leurs préférences respectives.
Les **étudiants** proposent donc aux **écoles**, qui acceptent ou rejettent selon leurs préférences.
L'algorithme garantit un résultat stable et permet d'analyser la satisfaction moyenne et d'autres mesures globales.
""")

# ============================================================
# PARAMÈTRES UTILISATEUR
# ============================================================
st.sidebar.header("Paramètres")
n_entites = st.sidebar.slider("Nombre d'entités ", 2, 10, 5)
nb_tests = st.sidebar.slider("Nombre d'instances aléatoires", 1, 20, 5)
start_btn = st.sidebar.button("Générer et exécuter l'algorithme")

# ============================================================
# VERSION ANIMÉE DE L'ALGORITHME
# ============================================================

def mariage_stable_animated(pref_student, pref_school, speed=0.5):
    """Version animée de Gale–Shapley avec affichage Streamlit"""
    steps_container = st.container()
    free_students = list(pref_student.keys())
    proposals = {p: [] for p in pref_student}
    engaged = {s: None for s in pref_school}

    step = 1
    while free_students:
        current_student = free_students[0]
        next_school = None

        # trouve la prochaine école à laquelle proposer
        for school in pref_student[current_student]:
            if school not in proposals[current_student]:
                next_school = school
                break

        if next_school is None:
            free_students.pop(0)
            continue

        proposals[current_student].append(next_school)
        current_eng = engaged[next_school]

        # affichage de l'étape
        with steps_container:
            st.markdown(f"### Étape {step}")
            st.markdown(f"👩‍🎓 **{current_student}** propose à 🏫 **{next_school}**")

        # cas 1 : école libre → accepte
        if current_eng is None:
            engaged[next_school] = current_student
            free_students.pop(0)
            with steps_container:
                st.success(f"✅ {next_school} accepte temporairement {current_student}")
        else:
            # compare préférences
            rank_new = pref_school[next_school].index(current_student)
            rank_old = pref_school[next_school].index(current_eng)
            if rank_new < rank_old:
                engaged[next_school] = current_student
                free_students.pop(0)
                free_students.append(current_eng)
                with steps_container:
                    st.warning(f"⚖️ {next_school} préfère {current_student} à {current_eng} → {current_eng} redevient libre")
            else:
                with steps_container:
                    st.error(f"❌ {next_school} rejette {current_student} (préférence pour {current_eng})")

        # état courant
        with steps_container:
            st.markdown("#### Engagements actuels :")
            df = pd.DataFrame([{"École": e, "Étudiant affecté": engaged[e] or "—"} for e in engaged])
            st.dataframe(df, use_container_width=True)
            st.markdown("---")

        step += 1
        time.sleep(speed)

    return engaged


# ============================================================
# EXÉCUTION DE LA SIMULATION
# ============================================================
if start_btn:
    st.empty()  # vide les conteneurs précédents

    st.info("Simulation en cours...")

    # Génération aléatoire
    students, schools, prefs_students, prefs_schools = generate_preferences(n_entites, n_entites)
    save_to_csv(students, schools, prefs_students, prefs_schools, "instance_temp.csv")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 👩‍🎓 Étudiants → Écoles")
        st.dataframe(
            pd.DataFrame([{"Étudiant": s, "Préférences": " → ".join(prefs_students[s])} for s in prefs_students])
        )
    with col2:
        st.markdown("#### 🏫 Écoles → Étudiants")
        st.dataframe(
            pd.DataFrame([{"École": e, "Préférences": " → ".join(prefs_schools[e])} for e in prefs_schools])
        )

    st.markdown("---")
    st.subheader("Déroulement pas à pas")
    engaged = mariage_stable_animated(prefs_students, prefs_schools, speed=1.0)

    # ============================================================
    # MESURES FINALES
    # ============================================================
    st.subheader("Résultat final du mariage stable")
    engaged_final = engaged  
    
    st.table(pd.DataFrame([{"École": e, "Étudiant affecté": engaged_final[e]} for e in engaged_final]))

    results = compute_all_measures(prefs_students, prefs_schools, engaged)

    st.session_state["engaged_final"] = engaged_final
    st.session_state["results"] = results

    st.markdown("### 📊 Mesures globales de satisfaction")

    # Ligne 1 : performance moyenne
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Rang moyen étudiants", f"{results['avg_rank_students']:.2f}")
    with col2:
        st.metric("Rang moyen écoles", f"{results['avg_rank_schools']:.2f}")

    # Ligne 2 : satisfaction globale
    st.markdown("---")
    col3, col4, col5 = st.columns(3)
    with col3:
        st.metric("Welfare total", f"{results['welfare']:.2f}")
    with col4:
        st.metric("Coût égalitaire", f"{results['egalitarian_cost']}")
    with col5:
        pareto_text = "✅ Oui" if results["pareto_optimal"] else "❌ Non"
        st.metric("Pareto-optimalité", pareto_text)


    # ============================================================
    # VISUALISATION MULTIPLE — VERSION HISTOGRAMMES
    # ============================================================
    st.markdown("---")
    st.subheader("📊 Analyse sur plusieurs instances (tests aléatoires)")

    with st.spinner("Génération des graphiques..."):
        fig1, fig2, fig3 = test_measures_with_graphs(
            nb_tests=nb_tests,
            n_students=n_entites,
            n_schools=n_entites
        )

    st.pyplot(fig1)
    st.pyplot(fig2)
    st.pyplot(fig3)

    st.success("✅ Histogrammes générés avec succès !")



    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for i, (fig, name) in enumerate(zip(
            [fig1, fig2, fig3],
            ["rang_moyen.png", "welfare.png", "cout_egalitaire.png"]
        )):
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
            zip_file.writestr(name, buf.getvalue())

    # pour fermer le ZIP et prépare le téléchargement
    zip_buffer.seek(0)

    st.write("---")
    st.markdown("#### Exporter les résultats")

    # Récupère les résultats sauvegardés
    if "engaged_final" in st.session_state:
        engaged_final = st.session_state["engaged_final"]
        results = st.session_state["results"]

        df_result = pd.DataFrame([{"École": e, "Étudiant affecté": engaged_final[e]} for e in engaged_final])
        csv = df_result.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Télécharger le résultat final au format CSV",
            data=csv,
            file_name="resultats_mariage_stable.csv",
            mime="text/csv",
            key="download_results"  # clé unique pour éviter les re-renders
        )

        # Bonus : téléchargement des mesures globales
        results_df = pd.DataFrame([results])
        st.download_button(
            label="📊 Télécharger les mesures globales (CSV)",
            data=results_df.to_csv(index=False).encode("utf-8"),
            file_name="mesures_mariage_stable.csv",
            mime="text/csv",
            key="download_measures"
        )

        st.download_button(
            label="📦 Télécharger les 3 graphiques en PNG (.zip)",
            data=zip_buffer.getvalue(),
            file_name="graphiques_mariage_stable.zip",
            mime="application/zip",
            key="download_zip_plots"
        )

    else:
        st.warning("Aucun résultat disponible. Exécutez d'abord la simulation avant de télécharger.")

        df_result = pd.DataFrame([{"École": e, "Étudiant affecté": engaged_final[e]} for e in engaged_final])
        csv = df_result.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Télécharger les résultats au format CSV",
            data=csv,
            file_name="resultats_mariage_stable.csv",
            mime="text/csv",
            help="Cliquez pour enregistrer les appariements finaux"
        )


else:
    st.info("👉 Choisis les paramètres à gauche puis clique sur **Générer et exécuter l'algorithme**.")
