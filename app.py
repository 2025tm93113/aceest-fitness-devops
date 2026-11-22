"""Flask adaptation of the ACEest Fitness application (v2.0)."""
from copy import deepcopy
import os
from flask import Flask, jsonify, render_template, request
from programs import PROGRAMS, SITE_METRICS

APP_VERSION = os.getenv("APP_VERSION", "2.0")
CALORIE_FACTORS = {
    "Fat Loss (FL)": 22,
    "Muscle Gain (MG)": 35,
    "Beginner (BG)": 26,
}


def get_program(name):
    if name not in PROGRAMS:
        raise ValueError("Unknown program")
    return deepcopy(PROGRAMS[name])


def calculate_bmi(weight_kg, height_cm):
    if weight_kg <= 0 or height_cm <= 0:
        raise ValueError("Weight and height must be positive")
    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m * height_m), 1)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return bmi, category


def create_app(test_config=None):
    app = Flask(__name__)
    if test_config:
        app.config.update(test_config)

    @app.get("/")
    def home():
        selected = request.args.get("program", "")
        data = None
        error = None
        if selected:
            try:
                data = get_program(selected)
            except ValueError:
                error = "Unknown program. Please select a listed program."
        return render_template(
            "index.html", programs=PROGRAMS, selected=selected,
            data=data, metrics=SITE_METRICS, error=error,
        ), 400 if error else 200

    @app.get("/health")
    def health():
        return jsonify(status="healthy", version=APP_VERSION)

    @app.get("/api/version")
    def version():
        return jsonify(app="ACEest Fitness & Gym", version=APP_VERSION)

    @app.get("/api/programs")
    def list_programs():
        return jsonify(programs=PROGRAMS)

    @app.get("/api/program")
    def program_detail():
        name = request.args.get("name", "")
        if not name:
            return jsonify(error="name query parameter is required"), 400
        try:
            return jsonify(name=name, **get_program(name))
        except ValueError:
            return jsonify(error="Unknown program"), 404

    @app.get("/api/metrics")
    def metrics():
        return jsonify(SITE_METRICS)

    @app.post("/api/calories")
    def calories():
        payload = request.get_json(silent=True) or {}
        program = payload.get("program", "")
        weight = payload.get("weight")
        if program not in CALORIE_FACTORS or not isinstance(weight, (int, float)) or weight <= 0:
            return jsonify(error="Valid program and positive weight are required"), 400
        estimated = int(weight * CALORIE_FACTORS[program])
        return jsonify(program=program, weight_kg=weight, estimated_calories=estimated)

    @app.post("/api/bmi")
    def bmi():
        payload = request.get_json(silent=True) or {}
        weight = payload.get("weight", 0)
        height = payload.get("height", 0)
        try:
            bmi_val, category = calculate_bmi(float(weight), float(height))
        except (TypeError, ValueError):
            return jsonify(error="Valid positive weight and height are required"), 400
        return jsonify(bmi=bmi_val, category=category)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify(error="Resource not found"), 404

    return app


app = create_app()

if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=5000, debug=False)