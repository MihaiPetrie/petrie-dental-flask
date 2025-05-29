from flask import Flask, render_template_string, request, send_from_directory
import os
from itertools import combinations, product

app = Flask(__name__)

# Servire favicon
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
    {"id": 23, "description": "Mentinatoare de spatiu mobile", "price": 656},
    {"id": 24, "description": "Sigilare /dinte", "price": 108},
    {"id": 25, "description": "Fluorizare", "price": 94},
    {"id": 26, "description": "Detartraj cu ultrasunete si periaj profesional/arcada", "price": 120},
]

# Functie pentru generarea combinatiilor (maxim 4 tipuri, suma exacta, cu repetitii, prioritizand tratamente scumpe)
def find_combinations_max4_types_exact_sum(treatments, budget, max_types=4, max_solutions=20):
    results = []
    # Sorteaza tratamentele descrescator dupa pret
    treatments_sorted = sorted(treatments, key=lambda x: -x['price'])
    n = len(treatments_sorted)
    for k in range(1, max_types+1):
        # Pentru fiecare submultime de k tipuri de tratamente
        for subset in combinations(treatments_sorted, k):
            # Max nr de fiecare tratament = buget // pret
            max_counts = [budget // t['price'] for t in subset]
            # Genereaza toate variantele posibile de repetiții
            for counts in product(*(range(c+1) for c in max_counts)):
                if sum(counts) == 0:
                    continue
                total = sum(t['price'] * cnt for t, cnt in zip(subset, counts))
                if total == budget:
                    combo = []
                    for t, cnt in zip(subset, counts):
                        if cnt > 0:
                            combo.append({"description": t['description'], "price": t['price'], "count": cnt})
                    # Pentru unicitate
                    if combo not in results:
                        results.append(combo)
                if len(results) >= max_solutions:
                    return results
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    result_html = ''
    budget = None
    if request.method == 'POST':
        try:
            budget = int(request.form.get('budget', 0))
            if budget <= 0:
                raise ValueError
        except ValueError:
            result_html = '<div class="error">Introduceți o sumă validă!</div>'
        else:
            solutions = find_combinations_max4_types_exact_sum(treatments, budget)
            if not solutions:
                result_html = '<div class="error">Nu există combinații posibile pentru acest buget.</div>'
            else:
                for idx, combo in enumerate(solutions, 1):
                    result_html += f"<strong>Combinația {idx}:</strong><br>"
                    for t in combo:
                        result_html += f"{t['description']} ({t['price']} lei) × {t['count']} = <b>{t['price']*t['count']} lei</b><br>"
                    result_html += f"<b style='color:#218721'>Total: {budget} lei</b><br><br>"

    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Selector Tratamente | Petrie Dental Solutions</title>
        <link rel="icon" href="/favicon.ico" type="image/png">
        <style>
            body { font-family: Segoe UI, Arial, sans-serif; background: #f7fafd; padding: 30px; }
            h2 { color: #174080; }
            .error { color: #bb1313; font-weight: bold; }
            input[type="number"] { font-size: 1.2em; width: 120px;}
            input[type="submit"] { background: #2176bd; color: white; border: none; font-size: 1.1em; padding: 7px 18px; border-radius: 7px;}
            input[type="submit"]:hover { background: #2482a1;}
            hr {margin: 20px 0;}
        </style>
    </head>
    <body>
        <h2>Selector combinații tratamente<br>
        <span style="font-size:18px;color:#2482a1">(maxim 4 tipuri distincte, suma exactă)</span></h2>
        <form method="post">
            <label for="budget"><b>Introduceți bugetul dorit (lei):</b></label>
            <input type="number" name="budget" required>
            <input type="submit" value="Caută combinații">
        </form>
        <hr>
        <div>{{result|safe}}</div>
    </body>
    </html>
    """

    return render_template_string(HTML_TEMPLATE, result=result_html)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
