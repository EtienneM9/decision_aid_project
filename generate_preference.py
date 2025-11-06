import csv
import random
import sys

from  faker import Faker # il faut faire pip install faker

fake = Faker('fr_FR')

SCHOOLS_FR = [
    "École Polytechnique", "HEC Paris", "Sorbonne Université", "INSA Lyon",
    "ESSEC Business School", "Sciences Po", "Mines ParisTech", "ENSAE Paris",
    "Université de Montpellier", "CentraleSupélec", "Université de Bordeaux",
    "ENS Lyon", "Télécom Paris", "Université Grenoble Alpes", "EM Lyon"
]

def generate_preferences(n_students, n_schools):
    """Génère des préférences aléatoires pour n étudiants et n écoles."""
    students = list({fake.first_name() for _ in range(n_students * 2)})[:n_students]
    schools = random.sample(SCHOOLS_FR, n_schools)

    prefs_students = {
        s: random.sample(schools, len(schools)) for s in students
    }
    prefs_schools = {
        e: random.sample(students, len(students)) for e in schools
    }

    return students, schools, prefs_students, prefs_schools


def save_to_csv(students, schools, prefs_students, prefs_schools, filename="instance_vrais_noms.csv"):
    """Enregistre les préférences dans un fichier CSV."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # En-têtes
        writer.writerow(["Type", "Nom", "Préférences"])

        # Étudiants
        for s in students:
            writer.writerow(["Etudiant", s, " - ".join(prefs_students[s])])

        # Séparateur vide
        writer.writerow([])

        # Écoles
        for e in schools:
            writer.writerow(["Ecole", e, " - ".join(prefs_schools[e])])

    print(f" Fichier '{filename}' généré avec succès !")


if __name__ == "__main__":
    # Récupération des arguments depuis la ligne de commande
    if len(sys.argv) != 3:
        print(" Utilisation : python generate_preference.py <nb_etudiants> <nb_ecoles>")
        sys.exit(1)

    n_students = int(sys.argv[1])
    n_schools = int(sys.argv[2])

    # Génération et sauvegarde
    students, schools, prefs_students, prefs_schools = generate_preferences(n_students, n_schools)
    save_to_csv(students, schools, prefs_students, prefs_schools)
