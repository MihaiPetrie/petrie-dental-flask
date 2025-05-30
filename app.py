from flask import Flask, render_template_string, request, send_from_directory
import os

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
    {"id": 23, "description": "Mentnatoare de spatiu mobile", "price": 656},
    {"id": 24, "description": "Sigilare /dinte/", "price": 108},
    {"id": 25, "description": "Fluorizare", "price": 94},
    {"id": 26, "description": "Detartraj cu ultrasunete si periaj profesional/arcada", "price": 79}
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <title>Selector combinații tratamente</title>
    <link rel="icon" href="/favicon.ico">
    <style>
        body { font-family: Arial, sans-serif; background: #f7f8fc; margin: 0; padding: 0 0 80px 0; }
        .container { max-width: 680px; background: #fff; margin: 40px auto 0 auto; border-radius: 10px; box-shadow: 0 0 12px #ddd; padding: 40px; }
        h1 { color: #1d4b96; }
        .credit { color: #bbb; font-size: 13px; text-align: right; margin-top: 70px;}
        .estella { font-weight: bold; color: #2d7a53; font-size: 1.14em; letter-spacing:1px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Selector combinații tratamente</h1>
        <div class="estella">Dr. Breban Estella</div>
        <form method="post">
            <label>Introduceți bugetul dorit (lei): <input type="number" name="budget" value="{{budget or ''}}" required></label>
            <br><br>
            <b>1. Selectați tratamente OBLIGATORII:</b><br>
            {% for t in treatments %}
                <input type="checkbox" name="prioritized" value="{{t['id']}}" {% if prioritized and t['id'] in prioritized %}checked{% endif %}> {{t['description']}} ({{t['price']}} lei)<br>
            {% endfor %}
            <br>
            <b>2. Selectați tratamente de EXCLUS:</b><br>
            {% for t in treatments %}
                <input type="checkbox" name="excluded" value="{{t['id']}}" {% if excluded and t['id'] in excluded %}checked{% endif %}> {{t['description']}} ({{t['price']}} lei)<br>
            {% endfor %}
            <br>
            <button type="submit">Caută combinații</button>
        </form>
        <hr>
        {{result|safe}}
        <div class="credit">Produs de Mihai Petrie &copy; 2025 Petrie Dental Solution</div>
    </div>
</body>
</html>
'''

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.png', mimetype='image/png')

def find_combinations_with_priorities_and_exclude(items, budget, prioritized, excluded):
    allowed = [t for t in items if t['id'] not in prioritized and t['id'] not in excluded]
    combos = []
    for i in range(2, 5): # Combinații de 2, 3 sau 4 tratamente
        for combo in combinations(allowed, i):
            total = sum(t['price'] for t in combo) + sum(t['price'] for t in items if t['id'] in prioritized)
            if total == budget:
                combos.append(list(combo))
    return combos

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    budget = None
    prioritized = []
    excluded = []

    if request.method == "POST":
        try:
            budget = int(request.form.get("budget", 0))
            prioritized = list(map(float, request.form.getlist("prioritized")))
            excluded = list(map(float, request.form.getlist("excluded")))

            # nu poți bifa același tratament la prioritizat și exclus
            if any(t in prioritized for t in excluded):
                result = '<span style="color:#a00;">Nu poți bifa același tratament ca prioritar și exclus.</span>'
            else:
                combos = find_combinations_with_priorities_and_exclude(treatments, budget, prioritized, excluded)
                if not combos:
                    result = "<span style='color:#a00;'>Nu există nicio combinație cu aceste priorități/excluderi și buget.</span>"
                else:
                    for idx, combo in enumerate(combos, 1):
                        res = f"<b>Combinația {idx}:</b><br>"
                        for t in combo:
                            res += f"{t['description']} ({t['price']} lei)<br>"
                        for t in treatments:
                            if t['id'] in prioritized:
                                res += f"{t['description']} (prioritar, {t['price']} lei)<br>"
                        total = sum(t['price'] for t in combo) + sum(t['price'] for t in treatments if t['id'] in prioritized)
                        res += f"<b>Total: {total} lei</b><br><br>"
                        result += res
        except Exception as e:
            result = f"<span style='color:#a00;'>Eroare: {str(e)}</span>"

    return render_template_string(
        HTML_TEMPLATE,
        treatments=treatments,
        prioritized=prioritized,
        excluded=excluded,
        result=result,
        budget=budget
    )

if __name__ == "__main__":
    app.run(debug=True)
