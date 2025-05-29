from flask import Flask, render_template_string, request

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
    {"id": 26, "description": "Detartraj cu ultrasunete si periaj profesional/ambele arcade", "price": 150}
]

def find_combinations_with_priorities_and_exclude(items, budget, prioritized, max_solutions=20):
    base_sum = sum(item['price'] for item in prioritized)
    if base_sum > budget:
        return []

    rest_budget = budget - base_sum
    solutions = []

    def backtrack(remaining, combo, start):
        if remaining == 0:
            sol = {}
            for t in prioritized + combo:
                tid = t['id']
                if tid not in sol:
                    sol[tid] = {"description": t["description"], "price": t["price"], "count": 0}
                sol[tid]["count"] += 1
            solutions.append(list(sol.values()))
            return
        if remaining < 0 or len(solutions) >= max_solutions:
            return
        for i in range(start, len(items)):
            backtrack(remaining - items[i]['price'], combo + [items[i]], i)
    if rest_budget == 0:
        sol = [{"description": t["description"], "price": t["price"], "count": 1, "id": t["id"]} for t in prioritized]
        solutions.append(sol)
    else:
        backtrack(rest_budget, [], 0)
    return solutions

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <title>Selector Tratamente | Petrie Dental Solutions</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6fa; margin: 0; padding: 0; }
        .container { max-width: 800px; margin: 0 auto 0 auto; background: #fff; box-shadow: 0 0 15px #ddd; padding: 24px; border-radius: 14px; margin-top: 18px; }
        h1 { color: #1e3a7d; font-size: 1.6em; margin-bottom: 14px; }
        label, .treatment-label { font-size: 1.1em; }
        .section-title { margin-top: 20px; font-weight: bold; color: #144d6e; }
        input[type="number"] { padding: 7px; font-size: 1.2em; width: 120px; border-radius: 6px; border: 1px solid #ccc;}
        .checkbox-group { display: flex; flex-wrap: wrap; gap: 6px 22px; margin-bottom: 10px;}
        .treatment-label { display: flex; align-items: center; padding: 4px 0; }
        .btn { background: #274da4; color: #fff; font-weight: bold; border: none; padding: 10px 22px; font-size: 1.18em; border-radius: 6px; cursor: pointer; margin-top: 18px;}
        .btn:hover { background: #1c366e; }
        .footer { background: #e9e9e9; color: #5a6274; text-align: center; padding: 8px 0; border-radius: 0 0 14px 14px; margin-top: 20px; font-style: italic;}
        .result { background: #f6fbee; border: 1px solid #b8d7a5; margin-top: 18px; padding: 14px 10px 10px 20px; border-radius: 7px; font-size: 1.09em; }
        .error { color: #b8000f; font-weight: bold; }
        @media (max-width: 600px) {
            .container { padding: 10px; border-radius: 7px; margin-top: 2px;}
            h1 { font-size: 1.18em;}
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Selector combinații tratamente <br><span style="font-size:0.78em;color:#415ba8;">(prioritizare și excludere)</span></h1>
        <form method="post">
            <div style="margin-bottom:10px;">
                <label for="budget" style="font-weight:bold;font-size:1.22em;">Introduceți bugetul dorit (lei):</label>
                <input name="budget" type="number" id="budget" min="1" step="1" required value="{{budget if budget else ''}}">
            </div>

            <div class="section-title">1. Selectați tratamentele OBLIGATORII în combinație:</div>
            <div class="checkbox-group">
                {% for t in treatments %}
                    <label class="treatment-label">
                        <input type="checkbox" name="prioritize" value="{{t.id}}" {% if t.id|string in prioritize_ids %}checked{% endif %}>
                        {{t.description}} <span style="color:#555;">({{t.price}} lei)</span>
                    </label>
                {% endfor %}
            </div>

            <div class="section-title">2. Selectați tratamentele pe care doriți să le EXCLUDEȚI:</div>
            <div class="checkbox-group">
                {% for t in treatments %}
                    <label class="treatment-label">
                        <input type="checkbox" name="exclude" value="{{t.id}}" {% if t.id|string in exclude_ids %}checked{% endif %}>
                        {{t.description}} <span style="color:#555;">({{t.price}} lei)</span>
                    </label>
                {% endfor %}
            </div>

            <button class="btn" type="submit">Caută combinațiile exacte</button>
        </form>
        {% if result %}
            <div class="result">{{ result|safe }}</div>
        {% endif %}
    </div>
    <div class="footer">
        Petrie Dental Solutions &copy; 2025
    </div>
</body>
</html>
'''

from markupsafe import escape

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    budget = ""
    prioritize_ids = []
    exclude_ids = []
    if request.method == "POST":
        budget = request.form.get("budget", "")
        try:
            budget_val = int(budget)
            if budget_val <= 0:
                raise ValueError
        except:
            result = '<span class="error">Introduceți o sumă validă și pozitivă!</span>'
            return render_template_string(HTML_TEMPLATE, treatments=treatments, result=result, budget=budget, prioritize_ids=[], exclude_ids=[])
        prioritize_ids = request.form.getlist("prioritize")
        exclude_ids = request.form.getlist("exclude")
        prioritized = [t for t in treatments if str(t["id"]) in prioritize_ids]
        excluded = [t for t in treatments if str(t["id"]) in exclude_ids]
        allowed = [t for t in treatments if t not in excluded]

        if any(t in excluded for t in prioritized):
            result = '<span class="error">Nu poți bifa același tratament ca prioritar și exclus!</span>'
        else:
            combos = find_combinations_with_priorities_and_exclude(allowed, int(budget), prioritized)
            if not combos:
                result = '<span class="error">Nu există nicio combinație exactă cu aceste priorități/excluderi și buget.</span>'
            else:
                for idx, combo in enumerate(combos, 1):
                    result += f"<strong style='color:#2346a8;'>--- Combinația {idx} ---</strong><br>"
                    for t in combo:
                        result += f"<b>{escape(t['description'])}</b> &nbsp;|&nbsp; Preț: {t['price']} lei &times; {t['count']} = <b>{t['price']*t['count']} lei</b><br>"
                    total = sum(t['price']*t['count'] for t in combo)
                    result += f"<span style='color:#248a21;font-weight:bold;'>Total: {total} lei</span><br><br>"
    return render_template_string(
        HTML_TEMPLATE,
        treatments=treatments,
        result=result,
        budget=budget,
        prioritize_ids=prioritize_ids,
        exclude_ids=exclude_ids
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
