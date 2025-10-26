# Stable Marriage Algorithm - Student-School Matching

This project implements the **Gale-Shapley stable marriage algorithm** to match students with schools based on mutual preferences. The implementation includes tools to generate random preference instances and solve the matching problem.

## 📁 Project Files

- **`generate_preference.py`** - Generates random preference instances
- **`instance.csv`** - Contains the preference data (generated or manually created)
- **`mariage_stable`** - Implements the stable marriage algorithm and solves the matching problem

---

## 🚀 Quick Start

### 1. Generate a Preference Instance

Use `generate_preference.py` to create a random preference file:

```bash
python generate_preference.py <number_of_students> <number_of_schools>
```

**Example:**
```bash
python3 generate_preference.py 3 3
```

This creates an `instance.csv` file with 3 students and 3 schools, each with random preference rankings.

### 2. Run the Stable Marriage Algorithm

Execute the matching algorithm:

```bash
python3 mariage_stable
```

This reads `instance.csv` and computes a stable matching between students and schools.

---

## 📊 CSV File Structure

The `instance.csv` file has the following format:

### Header Row
```csv
Type,Nom,Préférences
```

### Data Format

**Students Section:**
```csv
Etudiant,Etudiant1,Ecole1 - Ecole2 - Ecole3
Etudiant,Etudiant2,Ecole1 - Ecole2 - Ecole3
Etudiant,Etudiant3,Ecole2 - Ecole1 - Ecole3
```

**Empty Row** (separator between students and schools)

**Schools Section:**
```csv
Ecole,Ecole1,Etudiant2 - Etudiant1 - Etudiant3
Ecole,Ecole2,Etudiant3 - Etudiant1 - Etudiant2
Ecole,Ecole3,Etudiant1 - Etudiant2 - Etudiant3
```

### Structure Details

Each row contains three fields:

1. **Type**: Either `Etudiant` (Student) or `Ecole` (School)
2. **Nom**: The name/identifier of the entity
3. **Préférences**: Ranked preferences separated by ` - ` (space-dash-space)

**Important:**
- Preferences are listed from **most preferred to least preferred** (left to right)
- Preferences are separated by ` - ` (with spaces around the dash)
- An empty row separates students from schools
- Each student must rank all schools, and each school must rank all students

### Example Instance

```csv
Type,Nom,Préférences

Etudiant,Etudiant1,Ecole1 - Ecole2 - Ecole3
Etudiant,Etudiant2,Ecole1 - Ecole2 - Ecole3
Etudiant,Etudiant3,Ecole2 - Ecole1 - Ecole3

Ecole,Ecole1,Etudiant2 - Etudiant1 - Etudiant3
Ecole,Ecole2,Etudiant3 - Etudiant1 - Etudiant2
Ecole,Ecole3,Etudiant1 - Etudiant2 - Etudiant3
```

**Interpretation:**
- Etudiant1 prefers Ecole1 most, then Ecole2, then Ecole3
- Ecole1 prefers Etudiant2 most, then Etudiant1, then Etudiant3

---

## 🎓 The Stable Marriage Algorithm (Gale-Shapley)

### What is a Stable Matching?

A matching between students and schools is **stable** if there is no pair (student, school) where:
- The student prefers that school over their current match, AND
- The school prefers that student over their current match

Such a pair would have an incentive to "break away" from their current matches, making the matching unstable.

### How the Algorithm Works

The algorithm implements the **student-proposing Gale-Shapley algorithm**:

1. **Initialization:**
   - All students start as "free" (unmatched)
   - All schools have no engagements
   - Each student has a list of schools they haven't proposed to yet

2. **Proposal Phase:**
   - A free student proposes to the highest-ranked school on their preference list that they haven't proposed to yet

3. **Acceptance/Rejection:**
   - If the school is unengaged, it temporarily accepts the proposal
   - If the school is already engaged:
     - The school compares the new proposer with their current match
     - The school keeps the more preferred student (according to the school's preference list)
     - The rejected student becomes free again

4. **Iteration:**
   - Steps 2-3 repeat until all students are matched (or have proposed to all schools)

5. **Termination:**
   - The algorithm terminates when no free students remain
   - The final engagements form a stable matching

### Algorithm Properties

- **Guaranteed to find a stable matching** - no blocking pairs exist
- **Student-optimal** - each student gets the best school they can get in any stable matching
- **School-pessimal** - each school gets the worst student they can get in any stable matching
- **Time complexity:** O(n²) where n is the number of students/schools
- **Always terminates** - at most n² proposals are made

### Example Execution

Given the example CSV above:

**Initial State:**
- Free students: [Etudiant1, Etudiant2, Etudiant3]
- All schools unengaged

**Round 1:**
- Etudiant1 → Ecole1 (accepted, Ecole1 engaged to Etudiant1)
- Etudiant2 → Ecole1 (Ecole1 prefers Etudiant2, so Etudiant1 becomes free)
- Etudiant3 → Ecole2 (accepted, Ecole2 engaged to Etudiant3)

**Round 2:**
- Etudiant1 → Ecole2 (Ecole2 prefers Etudiant1 over Etudiant3, Etudiant3 becomes free)

**Round 3:**
- Etudiant3 → Ecole1 (Ecole1 prefers Etudiant2, rejected)
- Etudiant3 → Ecole3 (accepted, Ecole3 engaged to Etudiant3)

**Final Matching:**
```
Ecole1 ← Etudiant2
Ecole2 ← Etudiant1
Ecole3 ← Etudiant3
```

This matching is stable - no student-school pair would both prefer each other over their current matches.

---

## 💻 Code Structure

### `generate_preference.py`

**Functions:**
- `generate_preferences(n_students, n_schools)` - Creates random preference lists
- `save_to_csv(students, schools, prefs_students, prefs_schools, filename)` - Saves preferences to CSV

**Usage from command line:**
```bash
python generate_preference.py 5 4  # 5 students, 4 schools
```

### `mariage_stable`

**Functions:**
- `read_instance(filename)` - Reads the CSV file and returns preference dictionaries
- `mariage_stable(pref_student, pref_school)` - Implements the Gale-Shapley algorithm

**Key Data Structures:**
- `free_students` - List of students currently unmatched
- `proposals` - Dictionary tracking which schools each student has proposed to
- `engaged` - Dictionary mapping each school to their current match (or None)

**Algorithm Flow:**
```python
while free_students:
    current_student = free_students[0]
    # Find next school to propose to
    # Make proposal
    # School accepts/rejects based on preferences
    # Update free_students and engaged accordingly
```

---

## 📝 Creating Custom Instances

You can manually create an `instance.csv` file following the structure described above. 

**Tips:**
- Ensure each student ranks all schools
- Ensure each school ranks all students
- Use consistent naming (e.g., Etudiant1, Etudiant2, etc.)
- Separate preferences with ` - ` (space-dash-space)
- Include an empty row between students and schools sections

---

## 🔍 Example Output

When running `python mariage_stable`, you'll see:

```
pref_student {'Etudiant1': ['Ecole1', 'Ecole2', 'Ecole3'], ...}

free student: ['Etudiant1', 'Etudiant2', 'Etudiant3']

proposals: {'Etudiant1': [], 'Etudiant2': [], 'Etudiant3': []}

engaged: {'Ecole1': None, 'Ecole2': None, 'Ecole3': None}

engaged fin: {'Ecole1': 'Etudiant2', 'Ecole2': 'Etudiant1', 'Ecole3': 'Etudiant3'}

résultat du mariage stable :
```

The final `engaged` dictionary shows the stable matching.

---

## 📚 References

- Gale, D. and Shapley, L.S. (1962). "College Admissions and the Stability of Marriage"
- The algorithm is also known as the deferred-acceptance algorithm
- This algorithm won the 2012 Nobel Prize in Economics

---

## 🛠️ Requirements

- Python 3.x
- Standard library modules: `csv`, `random`, `sys`

No external dependencies required!
