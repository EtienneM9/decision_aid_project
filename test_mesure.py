from generate_preference import generate_preferences  # si ton script de génération est séparé
from mariage_stable import mariage_stable
from mariage_mesure import compute_average_scores

def test_multiple_instances(nb_tests=5, n_students=10, n_schools=10):
    """
    Teste le mariage stable sur plusieurs instances aléatoires
    et affiche la satisfaction moyenne des étudiants et des écoles.
    """
    results = []
    for i in range(nb_tests):
        students, schools, prefs_students, prefs_schools = generate_preferences(n_students, n_schools)
        engaged = mariage_stable(prefs_students, prefs_schools)
        avg_students, avg_schools = compute_average_scores(prefs_students, prefs_schools, engaged)
        results.append((avg_students, avg_schools))
        print(f"Test {i+1}: Étudiants={avg_students:.3f}, Écoles={avg_schools:.3f}")

    # Moyenne globale sur tous les tests
    mean_students = sum(s for s, _ in results) / len(results)
    mean_schools  = sum(e for _, e in results) / len(results)

    print("\n=== Moyenne globale sur toutes les instances ===")
    print(f"Satisfaction moyenne des étudiants : {mean_students:.3f}")
    print(f"Satisfaction moyenne des écoles    : {mean_schools:.3f}")

if __name__ == "__main__":
    print("\n=== TESTS MULTIPLES ===")
    test_multiple_instances(nb_tests=10, n_students=10, n_schools=10)
