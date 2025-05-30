from flask import Flask, render_template_string, request, send_from_directory
import os
from itertools import combinations, product

app = Flask(__name__)

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
    {"id": 23, "description": "Mentinatoare de spatiu mobile", "price": 656},
    {"id": 24, "description": "Sigilare /dinte", "price": 108},
    {"id": 25, "description": "Fluorizare", "price": 94},
    {"id": 26, "description": "Detartraj cu ultrasunete si periaj profesional/arcada", "price": 109},
    # Adaugă restul după nevoie
]

# Funcția cu excludere și combinații 2, 3, 4 tipuri
def find_exact_combinations(items, budget, excluded_ids=[], min_types=2, max_types=4):
    results = []
    filtered_items = [item for item in items if str(item['id']) not in excluded_ids]
    for n_types in range(min_types, max_types + 1):  # 2, 3, 4 tipuri
        for combo in combinations(filtered_items, n_types):
            prices = [item['price'] for item in combo]
            max_counts = [budget // p if p else 0 for p in prices]
            # Enumerăm toate combinațiile posibile de număr de bucăți pentru fiecare tip
            for counts in product(*[range(1, m + 1) for m in max_counts]):
                total = sum(c * p for c, p in zip(counts, prices))
                if total == budget:
                    # Construim combinația rezultat
                    result = []
                    for i, item in enumerate(combo):
                        result.append({
                            "description": item['description'],
                            "price": item['price'],
                            "count": counts[i]
                        })
                    results.append(result)
    return results

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <title>Selector combinații tratamente – Dr. Breban Estella</title>
    <link rel="icon" type="image/png" href="{{ url_for('faviCon') }}">
    <style>
        body { font-family: Segoe UI, Arial, sans-serif; background: #f4f8fc; margin: 0; }
        .container { max-width: 700px; margin: 32px auto; background: #fff; border-radius: 10px; box-shadow: 0 2px 8px #9ec7d3a0; padding: 32px 36px 60px 36px; }
        h1 { color: #256293; font-size: 2.2em; margin-bottom: 0; }
        h2 { color: #3572b2; margin: 8px 0 18px 0; }
        label { font-weight: bold; }
        .combi { background: #f1f8ff; border-left: 4px solid #45a1c6; margin-bottom: 20px; padding: 13px 16px 7px 16px; border-radius: 6px; }
        .combi strong { color: #257697; }
        .total { font-weight: bold; color: #2c8d2a; font-size: 1.1em; }
        .footer { color: #768799; font-size: 0.98em; text-align: right; position: fixed; left: 0; right: 0; bottom: 5px; padding: 6px 34px 6px 0; }
        .by { color: #1d446b; font-weight: 500; letter-spacing: 0.5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Selector combinații tratamente</h1>
        <h2 style="margin-bottom:28px;">Dr. Breban Estella</h2>
        <form method="POST">
            <label for="budget">Introduceți bugetul dorit (lei):</label>
            <input type="number" name="budget" min="1" required style="margin-left:8px;width:90px;" value="{{ budget or '' }}">
            <br><br>
            <label>Excludeți tratamente (opțional):</label><br>
            {% for t in treatments %}
                <label style="font-weight:normal;">
                    <input type="checkbox" name="excluded" value="{{t['id']}}"
                        {% if excluded and t['id']|string in excluded %} checked {% endif %}>
                    {{t['description']}} <span style="color:#aaa;">({{t['price']}} lei)</span>
                </label><br>
            {% endfor %}
            <br>
            <button type="submit" style="padding:6px 24px;background:#1d446b;color:#fff;border-radius:5px;font-size:1em;border:none;">Caută combinații</button>
        </form>
        <hr style="margin:28px 0;">
        {% if results is defined %}
            {% if results %}
                {% for idx, combo in enumerate(results, 1) %}
                    <div class="combi">
                        <strong>Combinatia {{idx}}:</strong><br>
                        {% for t in combo %}
                            {{ t['description'] }} ({{t['price']}} lei) × {{t['count']}}
                            = <strong>{{ t['price'] * t['count'] }} lei</strong> <br>
                        {% endfor %}
                        <div class="total">Total: {{ combo | sum(attribute='price', attribute2='count') }} lei</div>
                    </div>
                {% endfor %}
            {% else %}
                <div style="color:#c21c3e;margin:18px 0 10px 0;font-weight:bold;">
                    Nu există combinații pentru bugetul ales, cu aceste excluderi.
                </div>
            {% endif %}
        {% endif %}
    </div>
    <div class="footer">
        <span class="by">&copy;2025 Petrie Dental Solution</span>
    </div>
</body>
</html>
"""

# Helper pentru sum în template (cu două atribute)
@app.template_filter('sum')
def sum_combo(combo, attribute=None, attribute2=None):
    if attribute and attribute2:
        return sum(t[attribute]*t[attribute2] for t in combo)
    elif attribute:
        return sum(t[attribute] for t in combo)
    else:
        return sum(combo)

# Favicon endpoint (asigură-te că ai favicon.png în /static)
@app.route('/favicon.ico')
def faviCon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.png', mimetype='image/png')

@app.route("/", methods=["GET", "POST"])
def index():
    budget = None
    results = None
    excluded = []
    if request.method == "POST":
        budget = request.form.get("budget")
        excluded = request.form.getlist("excluded")
        if budget and budget.isdigit():
            results = find_exact_combinations(treatments, int(budget), excluded_ids=excluded)
    return render_template_string(HTML_TEMPLATE, treatments=treatments, results=results, budget=budget, excluded=excluded)

if __name__ == "__main__":
    app.run(debug=True)
