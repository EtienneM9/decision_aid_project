const express = require('express');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const csv = require('csv-parser');

const app = express();
const port = 3000;

app.use(express.json());
app.use(express.static('.'));

// API to generate preferences
app.post('/generate', (req, res) => {
    const { n } = req.body;
    try {
        // Change to parent directory and run python
        const output = execSync(`cd ../ && python3 generate_preference.py ${n}`, { encoding: 'utf-8' });
        console.log(output);
        // Read the generated CSV
        const prefs_students = {};
        const prefs_schools = {};
        let students = [], schools = [];
        const data = [];
        fs.createReadStream(path.join(__dirname, '../instance_vrais_noms.csv'))
            .pipe(csv())
            .on('data', (row) => {
                data.push(row);
            })
            .on('end', () => {
                for (const row of data) {
                    if (row.Type === 'Etudiant') {
                        prefs_students[row.Nom] = row['Préférences'].split(' - ');
                        students.push(row.Nom);
                    } else if (row.Type === 'Ecole') {
                        prefs_schools[row.Nom] = row['Préférences'].split(' - ');
                        schools.push(row.Nom);
                    }
                }
                res.json({ students, schools, prefs_students, prefs_schools });
            })
            .on('error', (err) => {
                res.status(500).json({ error: err.message });
            });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// For CSV download, return the file
app.get('/download/csv', (req, res) => {
    res.download(path.join(__dirname, 'results.csv'));
});

// For ZIP download, but for now, just send something
// Will implement later in front

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
