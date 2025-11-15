import csv


# =====================================================================
# 1) Lecture du fichier d'instance
# =====================================================================

def read_instance(filename="instance_vrais_noms.csv"):
    """
    Lit un fichier CSV généré par generate_preference.py
    et retourne deux dictionnaires :
      - prefs_students : {étudiant: [écoles...]}
      - prefs_schools  : {école: [étudiants...]}
    """
    prefs_students = {}
    prefs_schools = {}

    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # sauter l'en-tête

        for row in reader:
            if not row or len(row) < 3:
                continue

            entity_type, name, preferences = row
            prefs_list = [p.strip() for p in preferences.split(" - ")]

            if entity_type == "Etudiant":
                prefs_students[name] = prefs_list
            elif entity_type == "Ecole":
                prefs_schools[name] = prefs_list

    return prefs_students, prefs_schools



# =====================================================================
# 2) Algorithme du mariage stable (Gale–Shapley)
# =====================================================================

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


# =====================================================================
# 3) EXTRAIRE LES RANGS
# =====================================================================

def compute_ranks(prefs_students, prefs_schools, engaged):
    """
    ranks_students[s] = rang de l'école obtenue par s
    ranks_schools[e]  = rang de l'étudiant obtenu par e
    """
    ranks_students = {}
    ranks_schools = {}

    # Matching étudiant -> école
    match_student = {stud: sch for sch, stud in engaged.items()}

    # rangs étudiants
    for s, prefs in prefs_students.items():
        e = match_student[s]
        ranks_students[s] = prefs.index(e)

    # rangs écoles
    for e, prefs in prefs_schools.items():
        s = engaged[e]
        ranks_schools[e] = prefs.index(s)

    return ranks_students, ranks_schools



# =====================================================================
# 4) Mesure 1: Rang moyen (moyenne des positions obtenues)
# =====================================================================

def mean_rank(ranks_dict):
    return sum(ranks_dict.values()) / len(ranks_dict) if ranks_dict else float('nan')



# =====================================================================
# 5) Mesure 2: Coût égalitaire (egalitarian cost)
# =====================================================================

def egalitarian_cost(ranks_students, ranks_schools):
    return sum(ranks_students.values()) + sum(ranks_schools.values())



# =====================================================================
# 6) Mesure 3 : Welfare global (satisfaction agrégée)
# =====================================================================

def compute_welfare(ranks_students, ranks_schools, n_schools):
    """
    satisfaction = 1 - (rang / (n_schools - 1))
    """
    def sat(r):
        return 1 - (r / (n_schools - 1))

    welfare = 0
    for r in ranks_students.values():
        welfare += sat(r)
    for r in ranks_schools.values():
        welfare += sat(r)

    return welfare



# =====================================================================
# 7) Mesure 4: Pareto optimalité
# =====================================================================

def is_pareto_optimal(prefs_students, prefs_schools, engaged):
    """
    Un matching stable étudiant-proposant est toujours Pareto-optimal
    pour les étudiants, mais pas forcément pour les écoles.
    On teste l'existence d'une paire améliorante (blocking-improving pair).
    """
    match_student = {stud: sch for sch, stud in engaged.items()}

    for e, prefE in prefs_schools.items():
        current_s = engaged[e]

        # parcourir les étudiants mieux classés que current_s
        for s in prefE:
            if s == current_s:
                break  # ensuite, ce sont moins préférés

            # vérifier si s préfère cette école à son match actuel
            current_e_for_s = match_student[s]
            if prefs_students[s].index(e) < prefs_students[s].index(current_e_for_s):
                # amélioration bilatérale
                return False

    return True


# =====================================================================
# 8) Fonction globale regroupant toutes les mesures
# =====================================================================

def compute_all_measures(prefs_students, prefs_schools, engaged):
    n = len(prefs_schools)

    ranks_students, ranks_schools = compute_ranks(prefs_students, prefs_schools, engaged)

    return {
        "avg_rank_students": mean_rank(ranks_students),
        "avg_rank_schools": mean_rank(ranks_schools),
        "egalitarian_cost": egalitarian_cost(ranks_students, ranks_schools),
        "welfare": compute_welfare(ranks_students, ranks_schools, n),
        "pareto_optimal": is_pareto_optimal(prefs_students, prefs_schools, engaged)
    }



# =====================================================================
# 9) MAIN
# =====================================================================

if __name__ == "__main__":
    prefs_students, prefs_schools = read_instance("instance_vrais_noms.csv")
    engaged = mariage_stable(prefs_students, prefs_schools)

    results = compute_all_measures(prefs_students, prefs_schools, engaged)

    print("\n=== MESURES ===")
    print(f"Rang moyen étudiants : {results['avg_rank_students']:.3f}")
    print(f"Rang moyen écoles    : {results['avg_rank_schools']:.3f}")
    print(f"Coût égalitaire      : {results['egalitarian_cost']}")
    print(f"Welfare total        : {results['welfare']:.3f}")
    print(f"Pareto optimal ?     : {results['pareto_optimal']}")
