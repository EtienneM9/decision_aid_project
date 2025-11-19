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


# ==============================
# Test + collecte données
# ==============================

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

        # Génération instance
        students, schools, prefs_students, prefs_schools = generate_preferences(n_students, n_schools)

        # Mariage stable
        engaged = mariage_stable(prefs_students, prefs_schools)

        # Mesures complètes
        measures = compute_all_measures(prefs_students, prefs_schools, engaged)

        # ===== Rang moyen =====
        rank_students.append(measures["avg_rank_students"])
        rank_schools.append(measures["avg_rank_schools"])

        # ===== Welfare séparé =====
        ranks_stu, ranks_sch = compute_ranks(prefs_students, prefs_schools, engaged)
        n = n_schools - 1

        welfare_students.append(sum(1 - r/n for r in ranks_stu.values()))
        welfare_schools.append(sum(1 - r/n for r in ranks_sch.values()))

        # ===== Egalitarian cost séparé =====
        egalitarian_students.append(sum(ranks_stu.values()))
        egalitarian_schools.append(sum(ranks_sch.values()))

    tests = np.arange(1, nb_tests+1)
    bar_width = 0.35  # largeur des barres

    # =================================================================
    # HISTOGRAMME 1 : Rang moyen
    # =================================================================
    plt.figure(figsize=(10,5))

    plt.bar(tests - bar_width/2, rank_students, width=bar_width, label="Étudiants")
    plt.bar(tests + bar_width/2, rank_schools, width=bar_width, label="Écoles")

    plt.xticks(tests, [f"Test {i}" for i in tests])


    plt.title("Rang moyen par test")
    plt.xlabel("Numéro de test")
    plt.ylabel("Rang moyen (0 = meilleur)")
    plt.legend()
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)

    plt.savefig(os.path.join(output_dir, "hist_rang_moyen.png"), dpi=300)
    plt.show()


    # =================================================================
    # HISTOGRAMME 2 : Welfare
    # =================================================================
    plt.figure(figsize=(10,5))

    plt.bar(tests - bar_width/2, welfare_students, width=bar_width, label="Étudiants")
    plt.bar(tests + bar_width/2, welfare_schools, width=bar_width, label="Écoles")
    plt.xticks(tests, [f"Test {i}" for i in tests])


    plt.title("Welfare par test")
    plt.xlabel("Numéro de test")
    plt.ylabel("Welfare")
    plt.legend()
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)

    plt.savefig(os.path.join(output_dir, "hist_welfare.png"), dpi=300)
    plt.show()


    # =================================================================
    # HISTOGRAMME 3 : Coût égalitaire
    # =================================================================
    plt.figure(figsize=(10,5))

    plt.bar(tests - bar_width/2, egalitarian_students, width=bar_width, label="Étudiants")
    plt.bar(tests + bar_width/2, egalitarian_schools, width=bar_width, label="Écoles")
    plt.xticks(tests, [f"Test {i}" for i in tests])


    plt.title("Coût égalitaire par test")
    plt.xlabel("Numéro de test")
    plt.ylabel("Coût total (plus bas = meilleur)")
    plt.legend()
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)

    plt.savefig(os.path.join(output_dir, "hist_egalitarian_cost.png"), dpi=300)
    plt.show()


if __name__ == "__main__":
    test_measures_with_graphs(nb_tests=15, n_students=15, n_schools=15)
