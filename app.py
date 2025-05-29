from flask import Flask, render_template_string, request, send_from_directory
import os

app = Flask(__name__)

# Endpoint pentru favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.png',  # Nume exact fișier PNG din /static
        mimetype='image/png'
    )

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
    {"id": 26, "description": "Detartraj cu ultrasunete si periaj profesional/arcada", "price": 120},
    # Adaugă restul tratamentelor după nevoie
]

def find_combinations_with_priorities_and_exclude(items, budget, prioritized, exclude):
    base_sum = sum(item['price'] for item in prioritized)
    if base_sum > budget:
        return []
    combos = []
    for item in items:
        if item in prioritized or item in exclude:
            continue
        new_combo = prioritized + [item]
        new_sum = sum(x['price'] for x in new_combo)
        if new_sum <= budget:
            combos.append(new_combo)
    return combos

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ''
    budget = None
    prioritize_ids = []
    exclude_ids = []

    if request.method == 'POST':
        budget = int(request.form.get('budget', 0))
        prioritize_ids = [int(x) for x in request.form.getlist('prioritize')]
        exclude_ids = [int(x) for x in request.form.getlist('exclude')]

        prioritized = [t for t in treatments if t['id'] in prioritize_ids]
        excluded = [t for t in treatments if t['id'] in exclude_ids]
        allowed = [t for t in treatments if t not in excluded]

        combos = find_combinations_with_priorities_and_exclude(allowed, budget, prioritized, excluded)
        if not combos:
            result = '<span class="error">Nu există nicio combinație exactă cu aceste priorități/excluderi și buget.</span>'
        else:
            for idx, combo in enumerate(combos, 1):
                result += f"<strong>Combinația {idx}</strong>:<br>"
                for t in combo:
                    result += f"&nbsp;&nbsp;{t['description']} ({t['price']} lei)<br>"
                total = sum(t['price'] for t in combo)
                result += f'<b style="color:#2482a1;font-weight:bold;">Total: {total} lei</b><br><br>'

    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Selector Tratamente | Petrie Dental Solutions</title>
        <link rel="icon" href="/favicon.ico" type="image/png">
        <style>
            body { font-family: Arial, sans-serif; background: #f7fafd; padding: 40px; }
            h2 { color: #1d4675; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <h2>Selector combinații tratamente<br>
        <span style="font-size:18px;color:#2482a1">(prioritizare și excludere)</span></h2>
        <form method="post">
            <label for="budget"><b>Introduceți bugetul dorit (lei):</b></label>
            <input type="number" name="budget" required>
            <br><br>
            <b>1. Selectați tratamentele OBLIGATORII în combinație:</b><br>
            {% for t in treatments %}
                <input type="checkbox" name="prioritize" value="{{t['id']}}"> {{t['description']}} ({{t['price']}} lei)<br>
            {% endfor %}
            <br>
            <b>2. Selectați tratamentele de EXCLUS:</b><br>
            {% for t in treatments %}
                <input type="checkbox" name="exclude" value="{{t['id']}}"> {{t['description']}}<br>
            {% endfor %}
            <br>
            <input type="submit" value="Calculează combinații">
        </form>
        <hr>
        <div>{{result|safe}}</div>
    </body>
    </html>
    """

    return render_template_string(
        HTML_TEMPLATE,
        treatments=treatments,
        result=result,
        budget=budget,
        prioritize_ids=prioritize_ids,
        exclude_ids=exclude_ids
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
