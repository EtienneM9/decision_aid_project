import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import io
import zipfile

from generate_preference import generate_preferences, save_to_csv
from mariage_stable_mesure import (
    read_instance, compute_all_measures, compute_ranks, mariage_stable
)

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
n_students = st.sidebar.slider("Nombre d'étudiants ", 2, 10, 5)
n_schools = st.sidebar.slider("Nombre d'écoles ", 2, 10, 5)
vitesse = st.sidebar.slider("Vitesse de l'animation (sec/étape)", 0.1, 1.0, 0.5)
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
    students, schools, prefs_students, prefs_schools = generate_preferences(n_students, n_schools)
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
    engaged = mariage_stable_animated(prefs_students, prefs_schools, speed=vitesse)

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
    col1, col2, col3 = st.columns(3)
    col1.metric("Rang moyen étudiants", f"{results['avg_rank_students']:.2f}")
    col2.metric("Rang moyen écoles", f"{results['avg_rank_schools']:.2f}")
    col3.metric("Welfare total", f"{results['welfare']:.2f}")

    col4, col5 = st.columns(2)
    col4.metric("Coût égalitaire", f"{results['egalitarian_cost']}")
    pareto_text = "✅ Oui" if results["pareto_optimal"] else "❌ Non"
    col5.metric("Pareto-optimalité", pareto_text)

    # ============================================================
    # VISUALISATION MULTIPLE
    # ============================================================
    st.markdown("---")
    st.subheader("📈 Analyse sur plusieurs instances")

    rank_students, rank_schools = [], []
    welfare_students, welfare_schools, egalitarian_vals = [], [], []

    for i in range(nb_tests):
        students, schools, prefs_students, prefs_schools = generate_preferences(n_students, n_schools)
        engaged = mariage_stable(prefs_students, prefs_schools)
        measures = compute_all_measures(prefs_students, prefs_schools, engaged)

        rank_students.append(measures["avg_rank_students"])
        rank_schools.append(measures["avg_rank_schools"])
        egalitarian_vals.append(measures["egalitarian_cost"])

        n = n_schools - 1
        ranks_students, ranks_schools = compute_ranks(prefs_students, prefs_schools, engaged)
        welfare_students.append(sum(1 - r/n for r in ranks_students.values()))
        welfare_schools.append(sum(1 - r/n for r in ranks_schools.values()))


    x = list(range(1, nb_tests + 1))

    st.markdown("#### Rang moyen par test")
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.plot(x, rank_students, label="Étudiants", color="#457b9d", marker="o")
    ax1.plot(x, rank_schools, label="Écoles", color="#e76f51", marker="s")
    ax1.set_title("Évolution du rang moyen")
    ax1.set_xlabel("Test")
    ax1.set_ylabel("Rang moyen (plus petit = mieux)")
    ax1.legend()
    ax1.grid(True)
    st.pyplot(fig1)

    st.markdown("#### Welfare par test")
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.plot(x, welfare_students, label="Étudiants", color="#118ab2", marker="o")
    ax2.plot(x, welfare_schools, label="Écoles", color="#ef476f", marker="s")
    ax2.set_title("Welfare total par test")
    ax2.set_xlabel("Test")
    ax2.set_ylabel("Score de bien-être (plus haut = mieux)")
    ax2.legend()
    ax2.grid(True)
    st.pyplot(fig2)

    st.markdown("#### Coût égalitaire par test")
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    ax3.plot(x, egalitarian_vals, color="#073b4c", marker="d")
    ax3.set_title("Coût égalitaire global")
    ax3.set_xlabel("Test")
    ax3.set_ylabel("Somme des rangs (plus bas = plus juste)")
    ax3.grid(True)
    st.pyplot(fig3)

    st.success("✅ Graphiques générés avec succès !")


    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        # Graphique Rang moyen
        buf1 = io.BytesIO()
        fig1.savefig(buf1, format="png", dpi=300, bbox_inches="tight")
        zip_file.writestr("rang_moyen.png", buf1.getvalue())

        # Graphique Welfare
        buf2 = io.BytesIO()
        fig2.savefig(buf2, format="png", dpi=300, bbox_inches="tight")
        zip_file.writestr("welfare.png", buf2.getvalue())

        # Graphique Coût égalitaire
        buf3 = io.BytesIO()
        fig3.savefig(buf3, format="png", dpi=300, bbox_inches="tight")
        zip_file.writestr("cout_egalitaire.png", buf3.getvalue())

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
