import matplotlib.pyplot as plt
import numpy as np
import sys, os

# Ajout du dossier courant au PATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_preference import generate_preferences
from mariage_stable_mesure import (
    mariage_stable,
    compute_all_measures,
    compute_ranks
)


def test_measures_with_graphs(nb_tests=20, n_students=15, n_schools=15):

    # Création du dossier plots/
    output_dir = "plots"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    rank_students = []
    rank_schools = []

    welfare_students = []
    welfare_schools = []

    egalitarian_students = []
    egalitarian_schools = []

    for _ in range(nb_tests):

        students, schools, prefs_students, prefs_schools = generate_preferences(n_students, n_schools)
        # Mariage stable
        engaged = mariage_stable(prefs_students, prefs_schools)

        # recuperation des mesures
        measures = compute_all_measures(prefs_students, prefs_schools, engaged)

        # ===== Rang moyen =====
        rank_students.append(measures["avg_rank_students"])
        rank_schools.append(measures["avg_rank_schools"])

        # ===== Welfare séparé : on decompose le walfare globale pour les etudiants et les etablissements=====
        ranks_stu, ranks_sch = compute_ranks(prefs_students, prefs_schools, engaged)
        n = n_schools - 1

        welfare_students.append(sum(1 - r/n for r in ranks_stu.values()))
        welfare_schools.append(sum(1 - r/n for r in ranks_sch.values()))

        # ===== Egalitarian cost séparé: on separe aussi  =====
        egalitarian_students.append(sum(ranks_stu.values()))
        egalitarian_schools.append(sum(ranks_sch.values()))

    tests = np.arange(1, nb_tests+1)
    bar_width = 0.35  # largeur des barres

    mean_rank_stu = np.mean(rank_students)
    mean_rank_sch = np.mean(rank_schools)

    mean_welfare_stu = np.mean(welfare_students)
    mean_welfare_sch = np.mean(welfare_schools)

    mean_egal_stu = np.mean(egalitarian_students)
    mean_egal_sch = np.mean(egalitarian_schools)


    # =================================================================
    # HISTOGRAMME : Rang moyen (tests + moyenne)
    # =================================================================
    fig1, ax1 = plt.subplots(figsize=(7, 3.5))

    rank_students_extended = rank_students + [mean_rank_stu]
    rank_schools_extended  = rank_schools + [mean_rank_sch]

    labels_rank = [f"Test {i}" for i in tests] + ["Moyenne"]
    pos_rank = np.arange(len(labels_rank))

    bars_rank_students = ax1.bar(pos_rank - bar_width/2, rank_students_extended,
                                 width=bar_width, label="Étudiants")
    bars_rank_schools  = ax1.bar(pos_rank + bar_width/2, rank_schools_extended,
                                 width=bar_width, label="Écoles")

    # COLORATION des deux barres "Moyenne"
    bars_rank_students[-1].set_color("tab:green")   # Étudiants (moyenne)
    bars_rank_schools[-1].set_color("tab:red")    # Écoles (moyenne)

    ax1.set_xticks(pos_rank)
    ax1.set_xticklabels(labels_rank, rotation=45)
    ax1.set_title("Rang moyen par test + moyenne finale")
    ax1.set_xlabel("Tests")
    ax1.set_ylabel("Rang moyen (0 = meilleur)")
    ax1.legend()
    ax1.grid(True, axis="y", linestyle="--", alpha=0.5)
    fig1.tight_layout()
    fig1.savefig(os.path.join(output_dir, "hist_rang_moyen_plus_moyenne.png"), dpi=300)




    # =================================================================
    # HISTOGRAMME : Welfare (tests + moyenne)
    # =================================================================
    fig2, ax2 = plt.subplots(figsize=(7, 3.5))

    # Fusion données
    welfare_students_extended = welfare_students + [mean_welfare_stu]
    welfare_schools_extended  = welfare_schools  + [mean_welfare_sch]

    labels_welfare = [f"Test {i}" for i in tests] + ["Moyenne"]
    pos = np.arange(len(labels_welfare))

    # Barres normales (tests)
    bars_students = ax2.bar(pos - bar_width/2, welfare_students_extended, width=bar_width, label="Étudiants")
    bars_schools  = ax2.bar(pos + bar_width/2, welfare_schools_extended,  width=bar_width, label="Écoles")

    bars_students[-1].set_color("tab:green")   # barres Étudiants moyenne
    bars_schools[-1].set_color("tab:red")      # barres Écoles moyenne

    ax2.set_xticks(pos)
    ax2.set_xticklabels(labels_welfare, rotation=45)
    ax2.set_title("Welfare par test + moyenne finale")
    ax2.set_xlabel("Tests")
    ax2.set_ylabel("Welfare (plus haut = mieux)")
    ax2.legend()
    ax2.grid(True, axis="y", linestyle="--", alpha=0.5)
    fig2.tight_layout()
    fig2.savefig(os.path.join(output_dir, "hist_welfare_plus_moyenne.png"), dpi=300)



        # =================================================================
    # HISTOGRAMME : Coût égalitaire (tests + moyenne)
    # =================================================================
    fig3, ax3 = plt.subplots(figsize=(7, 3.5))

    egalitarian_students_extended = egalitarian_students + [mean_egal_stu]
    egalitarian_schools_extended  = egalitarian_schools  + [mean_egal_sch]

    labels_egal = [f"Test {i}" for i in tests] + ["Moyenne"]
    pos_egal = np.arange(len(labels_egal))

    bars_egal_students = ax3.bar(pos_egal - bar_width/2, egalitarian_students_extended,
                                 width=bar_width, label="Étudiants")
    bars_egal_schools  = ax3.bar(pos_egal + bar_width/2, egalitarian_schools_extended,
                                 width=bar_width, label="Écoles")

    # COLORATION des deux barres "Moyenne"
    bars_egal_students[-1].set_color("tab:green")   # Étudiants (moyenne)
    bars_egal_schools[-1].set_color("tab:red")      # Écoles (moyenne)

    ax3.set_xticks(pos_egal)
    ax3.set_xticklabels(labels_egal, rotation=45)
    ax3.set_title("Coût égalitaire par test + moyenne finale")
    ax3.set_xlabel("Tests")
    ax3.set_ylabel("Coût total (plus bas = meilleur)")
    ax3.legend()
    ax3.grid(True, axis="y", linestyle="--", alpha=0.5)
    fig3.tight_layout()
    fig3.savefig(os.path.join(output_dir, "hist_egalitarian_plus_moyenne.png"), dpi=300)

    return fig1, fig2, fig3




if __name__ == "__main__":
    test_measures_with_graphs(nb_tests=15, n_students=15, n_schools=15)
