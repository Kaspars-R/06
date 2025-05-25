from flask import Flask, request, jsonify, render_template, abort
import json
import os

app = Flask(__name__)

DATA_FILE = 'data.json'
TEACHER_API_KEY = "key"  # vienkāršs piemērs, labāk vides mainīgos izmantot

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route("/")
def index():
    return render_template("index.html")

def require_teacher_key():
    key = request.headers.get("X-API-KEY")
    if key != TEACHER_API_KEY:
        abort(403, description="Nav piekļuves tiesību")

@app.route("/add_grades", methods=["POST"])
def add_grades():
    require_teacher_key()  # pārbauda API atslēgu
    data = request.json
    name = data.get("name")
    grades = data.get("grades")
    if not name or not grades:
        return jsonify({"error": "Trūkst dati"}), 400

    all_data = load_data()
    all_data[name] = grades
    save_data(all_data)
    return jsonify({"message": f"Atzīmes saglabātas priekš {name}"}), 200

@app.route("/get_grades/<name>", methods=["GET"])
def get_grades(name):
    all_data = load_data()
    grades = all_data.get(name)
    if grades:
        return jsonify({"name": name, "grades": grades}), 200
    else:
        return jsonify({"error": "Skolēns nav atrasts"}), 404

@app.route("/get_all_students")
def get_all_students():
    require_teacher_key()
    data = load_data()
    return jsonify({"students": list(data.keys())})

@app.route("/delete_student/<name>", methods=["DELETE"])
def delete_student(name):
    require_teacher_key()
    all_data = load_data()
    if name in all_data:
        del all_data[name]
        save_data(all_data)
        return jsonify({"message": f"{name} ir dzēsts."}), 200
    else:
        return jsonify({"error": "Skolēns nav atrasts"}), 404

if __name__ == "__main__":
    app.run(debug=True)
