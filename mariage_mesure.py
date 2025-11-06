import random, csv

import csv

def read_instance(filename="instance_vrais_noms.csv"):
    """
    Lit un fichier CSV généré par generate_instance.py
    et retourne deux dictionnaires :
    - prefs_students : {etudiant: [ecoles...]}
    - prefs_schools  : {ecole: [etudiants...]}
    """
    prefs_students = {}
    prefs_schools = {}

    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # sauter l'en-tête

        for row in reader:
            if not row or len(row) < 3:
                continue  # ignorer lignes vides
            entity_type, name, preferences = row
            prefs_list = [p.strip() for p in preferences.split("-")]

            if entity_type == "Etudiant":
                prefs_students[name] = prefs_list
            elif entity_type == "Ecole":
                prefs_schools[name] = prefs_list

    return prefs_students, prefs_schools


def mariage_stable(pref_student, pref_school):

    free_students = list(pref_student.keys())#all students are free at the start
    proposals = {p: [] for p in pref_student} #track proposals made
    engaged = {s: None for s in pref_school} #track current engagements

    print("\n free student:", free_students)
    print("\n proposals:", proposals)
    print("\n engaged:", engaged)


    while free_students:
        current_student = free_students[0]
        next_school = None

        for school in pref_student[current_student]:
            if school not in proposals[current_student]:
                next_school = school
                break
        
        
        if next_school is None:
            # l'étudiant a proposé à toutes les écoles : on le retire
            free_students.pop(0)

        proposals[current_student].append(next_school)

        current_eng = engaged[next_school]

        if current_eng is None:
            engaged[next_school] = current_student #si l'école n'a pas d'engagement elle le prend temporairement
            free_students.pop(0)
        else:
            if pref_school[next_school].index(current_student) < pref_school[next_school].index(current_eng): #sinon, on les compares dans le classement de l'école
                engaged[next_school] = current_student #on affecte le nouveau si il est mieux classé que l'ancien
                free_students.pop(0)
                free_students.append(current_eng) #l'ancien candidat devient alors libre
            else:
                pass

    print("engaged fin:", engaged)
    return engaged


# ===================== MESURE : SCORE MOYEN (0..1) ======================

def compute_average_scores(prefs_students, prefs_schools, engaged):
    """
    Calcule le score moyen normalisé (0..1) pour :
      - les étudiants
      - les écoles
    Score = 1 - rang/(n-1), où n = nombre d'écoles = nombre d'étudiants.
    Retourne (avg_score_students, avg_score_schools).
    """
    n = len(prefs_schools)  # suppose listes complètes |S|=|E|
    if n <= 1:
        # Cas trivial :score parfait
        return 1.0, 1.0

    # Inverser le matching : étudiant -> école
    matched_school = {student: school for school, student in engaged.items()}

    ranks_students = []
    ranks_schools = []

    for s, lst in prefs_students.items():
        e = matched_school.get(s)
        if e in lst:
            ranks_students.append(lst.index(e)) #lst.index(e) =la position de cette école dans la liste (0 = 1er choix, 1 = 2e choix, etc

    for e, lst in prefs_schools.items():
        s = engaged.get(e)
        if s in lst:
            ranks_schools.append(lst.index(s)) #lst.index(s) = position de cet étudiant dans la liste (0 = préféré, etc

    # Scores normalisés [0,1] convertit un rang en score entre 0 et 1 :
    def norm_score(r):
        return 1.0 - (r / (n - 1))

    #On applique la fonction précédente à chaque rang.
    scores_students = [norm_score(r) for r in ranks_students]
    scores_schools  = [norm_score(r) for r in ranks_schools]

    #On fait la moyenne des scores
    avg_score_students = sum(scores_students) / len(scores_students) if scores_students else float('nan')
    avg_score_schools  = sum(scores_schools)  / len(scores_schools)  if scores_schools  else float('nan')

    return avg_score_students, avg_score_schools


def print_average_scores(avg_students, avg_schools):
    """Afficher le score moyen"""
    print("\n=== Score moyen normalisé===")
    print(f"- etudiants : {avg_students:.3f} (0..1, 1 = premier choix)")
    print(f"- ecoles    : {avg_schools:.3f} (0..1, 1 = premier choix)")


# ===================== MAIN  le meme + ajout de l'appel de la mesure=====================

if __name__ == "__main__":
    prefs_students, prefs_schools = read_instance("instance_vrais_noms.csv")

    print("pref_student", prefs_students)
    #print("Préférences des étudiants :")
    for s, prefs in prefs_students.items():
        print(f"  {s}: {prefs}")

    #print("\nPréférences des écoles :")
    for e, prefs in prefs_schools.items():
        print(f"  {e}: {prefs}")

    print("\n résultat du mariage stable :")
    mar_stable = mariage_stable(prefs_students, prefs_schools)

    avg_students, avg_schools = compute_average_scores(prefs_students, prefs_schools, mar_stable)
    print_average_scores(avg_students, avg_schools)
