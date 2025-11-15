import matplotlib.pyplot as plt
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

    welfare_vals_students = []
    welfare_vals_schools = []

    egalitarian_vals = []

    for _ in range(nb_tests):

        # Génération instance
        students, schools, prefs_students, prefs_schools = generate_preferences(n_students, n_schools)

        # Mariage stable
        engaged = mariage_stable(prefs_students, prefs_schools)

        # Mesures complètes
        measures = compute_all_measures(prefs_students, prefs_schools, engaged)

        # ===== 1) rang moyen =====
        rank_students.append(measures["avg_rank_students"])
        rank_schools.append(measures["avg_rank_schools"])

        # ===== 2) welfare étudiant / école =====
        n = n_schools - 1
        ranks_students, ranks_schools = compute_ranks(prefs_students, prefs_schools, engaged)

        welfare_student = sum(1 - r/n for r in ranks_students.values())
        welfare_school  = sum(1 - r/n for r in ranks_schools.values())

        welfare_vals_students.append(welfare_student)
        welfare_vals_schools.append(welfare_school)

        # ===== 3) egalitarian cost =====
        egalitarian_vals.append(measures["egalitarian_cost"])

    x = list(range(1, nb_tests+1))

    # =================================================================
    # GRAPHIQUE 1 : Rang moyen
    # =================================================================
    plt.figure(figsize=(9,5))
    plt.plot(x, rank_students, label="Étudiants")
    plt.plot(x, rank_schools, label="Écoles")
    plt.title("Rang moyen par test")
    plt.xlabel("Numéro du test")
    plt.ylabel("Rang moyen (0 = meilleur)")
    plt.legend()
    plt.grid(True)

    plt.savefig(os.path.join(output_dir, "rang_moyen.png"), dpi=300)
    plt.show()

    # =================================================================
    # GRAPHIQUE 2 : Welfare
    # =================================================================
    plt.figure(figsize=(9,5))
    plt.plot(x, welfare_vals_students, label="Étudiants")
    plt.plot(x, welfare_vals_schools, label="Écoles")
    plt.title("Welfare par test")
    plt.xlabel("Numéro du test")
    plt.ylabel("Welfare")
    plt.legend()
    plt.grid(True)

    plt.savefig(os.path.join(output_dir, "welfare.png"), dpi=300)
    plt.show()

    # =================================================================
    # GRAPHIQUE 3 : Coût égalitaire
    # =================================================================
    plt.figure(figsize=(9,5))
    plt.plot(x, egalitarian_vals)
    plt.title("Coût égalitaire par test")
    plt.xlabel("Numéro du test")
    plt.ylabel("Coût total (plus bas = meilleur)")
    plt.grid(True)

    plt.savefig(os.path.join(output_dir, "egalitarian_cost.png"), dpi=300)
    plt.show()


if __name__ == "__main__":
    test_measures_with_graphs(nb_tests=15, n_students=15, n_schools=15)
