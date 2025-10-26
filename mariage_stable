import random, csv

import csv

def read_instance(filename="instance.csv"):
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


if __name__ == "__main__":
    prefs_students, prefs_schools = read_instance("instance.csv")

    print("pref_student", prefs_students)
    #print("Préférences des étudiants :")
    for s, prefs in prefs_students.items():
        print(f"  {s}: {prefs}")

    #print("\nPréférences des écoles :")
    for e, prefs in prefs_schools.items():
        print(f"  {e}: {prefs}")

    print("\n résultat du mariage stable :")
    mar_stable = mariage_stable(prefs_students, prefs_schools)

    