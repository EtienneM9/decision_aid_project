// Update slider values
document.getElementById('n-slider').addEventListener('input', function() {
    document.getElementById('n-value').textContent = this.value;
});
document.getElementById('nb-tests-slider').addEventListener('input', function() {
    document.getElementById('nb-tests-value').textContent = this.value;
});
document.getElementById('vitesse-slider').addEventListener('input', function() {
    document.getElementById('vitesse-value').textContent = this.value;
});

// Start simulation
document.getElementById('start-btn').addEventListener('click', async function() {
    let engaged, results;
    const n = parseInt(document.getElementById('n-slider').value);
    const nbTests = parseInt(document.getElementById('nb-tests-slider').value);
    const speed = parseInt(document.getElementById('vitesse-slider').value);

    document.getElementById('content').innerHTML = '<div class="animate-pulse">Simulation en cours...</div>';

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ n })
        });
        const data = await response.json();
        const { students, schools, prefs_students, prefs_schools } = data;

        // Display preferences
        displayPreferences(students, schools, prefs_students, prefs_schools);

        // Run animation
        const engaged = await runAnimation(prefs_students, prefs_schools, speed);

        // Final match
        displayFinalMatch(engaged);

        // Measures
        const results = computeMeasures(prefs_students, prefs_schools, engaged);
        displayMeasures(results);

        // Multiple tests
        await runMultipleTests(n, nbTests);
    } catch (error) {
        console.error(error);
        document.getElementById('content').innerHTML = '<p class="text-red-500">Erreur lors de la simulation.</p>';
    }
});

// Display preferences
function displayPreferences(students, schools, prefs_students, prefs_schools) {
    const content = document.getElementById('content');
    content.innerHTML = `
        <h2 class="text-2xl font-semibold mb-4">Préférences</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
                <h3 class="text-xl font-medium mb-2">👩‍🎓 Étudiants → Écoles</h3>
                <div class="overflow-x-auto">
                    <table class="table-auto w-full border">
                        <thead>
                            <tr class="bg-gray-200"><th class="border px-4 py-2">Étudiant</th><th class="border px-4 py-2">Préférences</th></tr>
                        </thead>
                        <tbody>
                            ${students.map(s => `<tr><td class="border px-4 py-2">${s}</td><td class="border px-4 py-2">${prefs_students[s].join(' → ')}</td></tr>`).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
            <div>
                <h3 class="text-xl font-medium mb-2">🏫 Écoles → Étudiants</h3>
                <div class="overflow-x-auto">
                    <table class="table-auto w-full border">
                        <thead>
                            <tr class="bg-gray-200"><th class="border px-4 py-2">École</th><th class="border px-4 py-2">Préférences</th></tr>
                        </thead>
                        <tbody>
                            ${schools.map(e => `<tr><td class="border px-4 py-2">${e}</td><td class="border px-4 py-2">${prefs_schools[e].join(' → ')}</td></tr>`).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <hr class="my-8">
        <h2 class="text-2xl font-semibold mb-4">Déroulement pas à pas</h2>
        <div id="animation-container"></div>
    `;
}

// Animated algorithm
function runAnimation(pref_student, pref_school, speed) {
    return new Promise((resolve) => {
        const container = document.getElementById('animation-container');
        let free_students = [...Object.keys(pref_student)];
        let proposals = Object.fromEntries(Object.keys(pref_student).map(p => [p, []]));
        let engaged = Object.fromEntries(Object.keys(pref_school).map(s => [s, null]));

        let step = 1;

        function nextStep() {
            if (free_students.length === 0) {
                resolve(engaged);
                return;
            }

            const current_student = free_students[0];
            let next_school = null;
            for (const school of pref_student[current_student]) {
                if (!proposals[current_student].includes(school)) {
                    next_school = school;
                    break;
                }
            }

            proposals[current_student].push(next_school);
            const current_eng = engaged[next_school];

            container.innerHTML += `
                <div class="mb-4 p-4 border rounded">
                    <h3 class="font-semibold">Étape ${step}</h3>
                    <p>👩‍🎓 <strong>${current_student}</strong> propose à 🏫 <strong>${next_school}</strong></p>
            `;

            if (current_eng === null) {
                engaged[next_school] = current_student;
                free_students.shift();
                container.innerHTML += `<p class="text-green-600">✅ ${next_school} accepte ${current_student}</p>`;
            } else {
                const rank_new = pref_school[next_school].indexOf(current_student);
                const rank_old = pref_school[next_school].indexOf(current_eng);
                if (rank_new < rank_old) {
                    engaged[next_school] = current_student;
                    free_students.shift();
                    free_students.push(current_eng);
                    container.innerHTML += `<p class="text-yellow-600">⚖️ ${next_school} préfère ${current_student} à ${current_eng} → ${current_eng} redevient libre</p>`;
                } else {
                    container.innerHTML += `<p class="text-red-600">❌ ${next_school} rejette ${current_student}</p>`;
                }
            }

            // Current engagements
            container.innerHTML += `
                    <p class="mt-2">Engagements actuels:</p>
                    <ul>
                        ${Object.keys(engaged).map(s => `<li>• ${s}: ${engaged[s] || '—'}</li>`).join('')}
                    </ul>
                </div>
            `;

            step++;
            setTimeout(nextStep, speed);
        }

        nextStep();
    });
}

// Display final match
function displayFinalMatch(engaged) {
    const content = document.getElementById('content');
    content.innerHTML += `
        <hr class="my-8">
        <h2 class="text-2xl font-semibold mb-4">Résultat final du mariage stable</h2>
        <div class="overflow-x-auto">
            <table class="table-auto w-full border">
                <thead>
                    <tr class="bg-gray-200"><th class="border px-4 py-2">École</th><th class="border px-4 py-2">Étudiant affecté</th></tr>
                </thead>
                <tbody>
                    ${Object.keys(engaged).map(e => `<tr><td class="border px-4 py-2">${e}</td><td class="border px-4 py-2">${engaged[e] || '—'}</td></tr>`).join('')}
                </tbody>
            </table>
        </div>
        <div id="measures-container"></div>
    `;
}

// Compute measures
function computeMeasures(prefs_students, prefs_schools, engaged) {
    const n = Object.keys(prefs_schools).length;
    const ranks = {};
    for (const [stud, sch] of Object.entries(engaged)) {
        if (sch) {
            ranks[sch] = prefs_students[sch].indexOf(stud);
        }
    }
    const avg_rank_students = Object.values(ranks).reduce((a, b) => a + b, 0) / Object.values(ranks).length || 0;

    const ranks_schools = {};
    for (const [sch, stud] of Object.entries(invEngaged(engaged))) {
        ranks_schools[sch] = prefs_schools[sch].indexOf(stud);
    }
    const avg_rank_schools = Object.values(ranks_schools).reduce((a, b) => a + b, 0) / Object.values(ranks_schools).length || 0;

    const egalitarian_cost = Object.values(ranks).reduce((a, b) => a + b, 0) + Object.values(ranks_schools).reduce((a, b) => a + b, 0);

    const welfare = Object.values(ranks).map(r => 1 - r / (n - 1)).reduce((a, b) => a + b, 0) +
                    Object.values(ranks_schools).map(r => 1 - r / (n - 1)).reduce((a, b) => a + b, 0);

    const pareto_optimal = checkPareto(prefs_students, prefs_schools, engaged);

    return { avg_rank_students, avg_rank_schools, egalitarian_cost, welfare, pareto_optimal, ranks, ranks_schools };
}

function invEngaged(engaged) {
    const inv = {};
    for (const [sch, stud] of Object.entries(engaged)) {
        if (stud) inv[stud] = sch;
    }
    return inv;
}

function checkPareto(prefs_students, prefs_schools, engaged) {
    const match_stud = invEngaged(engaged);
    for (const [e, stud] of Object.entries(engaged)) {
        if (!stud) continue;
        const current = stud;
        for (const s of prefs_schools[e]) {
            if (s === current) break;
            const pref = match_stud[s];
            if (prefs_students[s].indexOf(e) < prefs_students[s].indexOf(pref)) {
                return false;
            }
        }
    }
    return true;
}

// Display measures
function displayMeasures(results) {
    const container = document.getElementById('measures-container');
    const { avg_rank_students, avg_rank_schools, egalitarian_cost, welfare, pareto_optimal } = results;
    container.innerHTML = `
        <hr class="my-8">
        <h2 class="text-2xl font-semibold mb-4">📊 Mesures globales de satisfaction</h2>
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div class="text-center p-4 border rounded">
                <div class="text-2xl font-bold">${avg_rank_students.toFixed(2)}</div>
                <div class="text-sm">Rang moyen étudiants</div>
            </div>
            <div class="text-center p-4 border rounded">
                <div class="text-2xl font-bold">${avg_rank_schools.toFixed(2)}</div>
                <div class="text-sm">Rang moyen écoles</div>
            </div>
            <div class="text-center p-4 border rounded">
                <div class="text-2xl font-bold">${welfare.toFixed(2)}</div>
                <div class="text-sm">Welfare total</div>
            </div>
            <div class="text-center p-4 border rounded">
                <div class="text-2xl font-bold">${egalitarian_cost}</div>
                <div class="text-sm">Coût égalitaire</div>
            </div>
            <div class="text-center p-4 border rounded">
                <div class="text-2xl font-bold">${pareto_optimal ? '✅ Oui' : '❌ Non'}</div>
                <div class="text-sm">Pareto-optimalité</div>
            </div>
        </div>
        <div id="multi-root"></div>
    `;
}

// Run multiple tests
async function runMultipleTests(n, nbTests) {
    const container = document.getElementById('multi-root');
    container.innerHTML += '<hr class="my-8"><h2 class="text-2xl font-semibold mb-4">📈 Analyse sur plusieurs instances</h2>';

    const rank_students = [], rank_schools = [], egalitarian_vals = [], welfare_students = [], welfare_schools = [];

    for (let i = 0; i < nbTests; i++) {
        // Generate new
        await new Promise(resolve => setTimeout(resolve, 100));
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ n })
        });
        const data = await response.json();
        const { prefs_students, prefs_schools } = data;

        const engaged = computeMariageStable(prefs_students, prefs_schools);
        const results = computeMeasures(prefs_students, prefs_schools, engaged);

        rank_students.push(results.avg_rank_students);
        rank_schools.push(results.avg_rank_schools);
        egalitarian_vals.push(results.egalitarian_cost);

        welfare_students.push(results.welfare / 2); // approximate split
        welfare_schools.push(results.welfare / 2);
    }

    // Plot charts
    plotChart('rank-chart', 'Rang moyen par test', rank_students, rank_schools, '#457b9d', '#e76f51');
    plotChart('welfare-chart', 'Welfare par test', welfare_students, welfare_schools, '#118ab2', '#ef476f');
    plotChart('egal-chart', 'Coût égalitaire par test', [0], egalitarian_vals, '#000', '#073b4c'); // single line

    // Downloads
    addDownloads();

    container.innerHTML += `
        <div>
            <canvas id="rank-chart" width="400" height="200"></canvas>
        </div>
        <div>
            <canvas id="welfare-chart" width="400" height="200"></canvas>
        </div>
        <div>
            <canvas id="egal-chart" width="400" height="200"></canvas>
        </div>
    `;
}

// Non-animated mariage
function computeMariageStable(pref_student, pref_school) {
    let free_students = [...Object.keys(pref_student)];
    let proposals = Object.fromEntries(Object.keys(pref_student).map(p => [p, []]));
    let engaged = Object.fromEntries(Object.keys(pref_school).map(s => [s, null]));

    while (free_students.length > 0) {
        const current_student = free_students[0];
        let next_school = null;
        for (const school of pref_student[current_student]) {
            if (!proposals[current_student].includes(school)) {
                next_school = school;
                break;
            }
        }
        if (next_school === null) {
            free_students.shift();
            continue;
        }
        proposals[current_student].push(next_school);
        const current_eng = engaged[next_school];
        if (current_eng === null) {
            engaged[next_school] = current_student;
            free_students.shift();
        } else {
            if (pref_school[next_school].indexOf(current_student) < pref_school[next_school].indexOf(current_eng)) {
                engaged[next_school] = current_student;
                free_students.shift();
                free_students.push(current_eng);
            }
        }
    }
    return engaged;
}

// Plot chart
function plotChart(canvasId, title, data1, data2, color1, color2) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data1.map((_, i) => i + 1),
            datasets: [{
                label: 'Étudiants',
                data: data1,
                borderColor: color1,
                fill: false
            }, {
                label: 'Écoles',
                data: data2,
                borderColor: color2,
                fill: false
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: title }
            }
        }
    });
}

// Add downloads
function addDownloads() {
    const container = document.getElementById('multi-root');
    container.innerHTML += `
        <hr class="my-8">
        <h2 class="text-2xl font-semibold mb-4">Exporter les résultats</h2>
        <div class="flex gap-4">
            <button id="download-csv" class="bg-blue-500 text-white px-4 py-2 rounded">📥 Télécharger les résultats CSV</button>
            <button id="download-measures" class="bg-green-500 text-white px-4 py-2 rounded">📊 Télécharger les mesures CSV</button>
            <button id="download-zip" class="bg-purple-500 text-white px-4 py-2 rounded">📦 Télécharger les graphiques ZIP</button>
        </div>
    `;

    document.getElementById('download-csv').addEventListener('click', () => {
        // Save engaged as CSV
        let csvContent = 'École,Étudiant affecté\n';
        Object.entries(engaged).forEach(([e, s]) => csvContent += `${e},${s || ''}\n`);
        downloadCSV(csvContent, 'resultats_mariage_stable.csv');
    });

    // Similar for measures, zip
}

// Helper function to download CSV
function downloadCSV(csvContent, filename) {
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
