from flask import Flask, render_template_string, request, send_from_directory
import os
from itertools import combinations

app = Flask(__name__)

# Endpoint pentru favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.png',
        mimetype='image/png'
    )

# Lista tratamentelor
treatments = [
    {"id": 1, "description": "Consultatie", "price": 149},
    {"id": 2, "description": "Tratament Carie simplu", "price": 157},
    {"id": 4, "description": "Pansament Calmant", "price": 78},
    {"id": 7.1, "description": "Tratament afectiuni mucoase bucale", "price": 76},
    {"id": 8, "description": "Extractie dinti temporari cu anestezie", "price": 76},
    {"id": 11, "description": "Decapusonarea", "price": 87},
    {"id": 12, "description": "Reducerea luxatiei articulatiei temporo-mandibulare", "price": 86},
    {"id": 18, "description": "Deconditionarea tulburarilor functionale prin aparate ortodontice", "price": 866},
    {"id": 19, "description": "Reducerea functionala prin exercitii, miogimnastica", "price": 22},
    {"id": 20, "description": "Aparate si dispozitive utilizate in tratamentul malformatiilor congenitale", "price": 1094},
    {"id": 21, "description": "Slefuirea in scop ortodontic/dinte", "price": 28},
    {"id": 22, "description": "Reparatie aparat ortodontic", "price": 583},
    {"id": 23, "description": "Mentnatoare de spatiu mobile", "price": 656},
    {"id": 24, "description": "Sigilare /dinte", "price": 108},
    {"id": 25, "description": "Fluorizare", "price": 94},
    {"id": 26, "description": "Detartraj cu ultrasunete si periaj profesional/arcada", "price": 79},
]

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <title>Selector combinații tratamente</title>
    <link rel="icon" href="/favicon.ico" type="image/png">
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; background: #fafbfe;}
        h1 { color: #273C6D; }
        .footer { margin-top: 2em; color: #555; font-size: 0.95em;}
        .combo-box { border: 1px solid #eee; border-radius: 7px; padding: 1em; margin-bottom: 1em; background: #fff; }
        .total { color: #228b22; font-weight: bold;}
        .error { color: #b00; }
        label { display: block; margin-bottom: 2px; }
    </style>
</head>
<body>
    <h1>Selector combinații tratamente</h1>
    <b>Dr. Breban Estella</b>
    <form method="post">
        <label for="budget">Introduceți bugetul dorit (lei):</label>
        <input type="number" name="budget" id="budget" value="{{budget or ''}}" required>
        <br><br>
        <b>1. Selectați tratamente OBLIGATORII:</b><br>
        {% for t in treatments %}
            <label><input type="checkbox" name="priorities" value="{{t.id}}" {% if t.id|string in priorities %}checked{% endif %}> {{t.description}} ({{t.price}} lei)</label>
        {% endfor %}
        <br>
        <b>2. Selectați tratamente de EXCLUS:</b><br>
        {% for t in treatments %}
            <label><input type="checkbox" name="excluded" value="{{t.id}}" {% if t.id|string in excluded %}checked{% endif %}> {{t.description}} ({{t.price}} lei)</label>
        {% endfor %}
        <br>
        <button type="submit">Caută combinații</button>
    </form>
    <hr>
    {% if result %}
        {{ result|safe }}
    {% endif %}
    <div class="footer">
        &copy; 2025 Petrie Dental Solution
    </div>
</body>
</html>
'''

def find_combinations_with_priorities_and_exclude(items, budget, priorities, excluded, max_types=4):
    # Pregătește seturile
    priorities_set = set(priorities)
    excluded_set = set(excluded)
    # Verifică să nu fie vreo prioritate și exclusă simultan!
    if priorities_set & excluded_set:
        return '<div class="error">Nu poți selecta același tratament ca prioritar și exclus!</div>'
    # Creează lista de tratamente disponibile (exclus exclușii)
    available = [t for t in items if str(t["id"]) not in excluded_set]
    # Toate combinațiile posibile de 1 până la max_types (fără dubluri)
    combos = []
    for r in range(1, max_types+1):
        for combo in combinations(available, r):
            combo_ids = {str(t["id"]) for t in combo}
            # Include doar dacă TOATE prioritățile sunt prezente
            if priorities_set and not priorities_set.issubset(combo_ids):
                continue
            # Nu permite să aibă și priorități și excluderi simultan
            if combo_ids & excluded_set:
                continue
            # Suma exactă
            total = sum(t["price"] for t in combo)
            if total == budget:
                combos.append(combo)
    if not combos:
        return '<div class="error">Nu există nicio combinație cu aceste priorități, excluderi și buget exact!</div>'
    # Construiește HTML pentru combinații găsite
    html = ""
    for idx, combo in enumerate(combos, 1):
        html += f'<div class="combo-box"><b>Combinația {idx}:</b><ul>'
        for t in combo:
            html += f'<li>{t["description"]} ({t["price"]} lei)</li>'
        html += f'</ul><span class="total">Total: {sum(t["price"] for t in combo)} lei</span></div>'
    return html

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    priorities = []
    excluded = []
    budget = None
    if request.method == "POST":
        priorities = request.form.getlist("priorities")
        excluded = request.form.getlist("excluded")
        try:
            budget = int(request.form.get("budget"))
        except:
            result = '<div class="error">Introduceți o sumă validă!</div>'
        if budget and not result:
            result = find_combinations_with_priorities_and_exclude(
                treatments, budget, priorities, excluded, max_types=4
            )
    return render_template_string(HTML_TEMPLATE,
                                  treatments=treatments,
                                  priorities=priorities,
                                  excluded=excluded,
                                  budget=budget,
                                  result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
