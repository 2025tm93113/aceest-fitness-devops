"""Flask adaptation of the ACEest version 1.0 desktop application."""
from copy import deepcopy
from flask import Flask, jsonify, render_template, request
from programs import PROGRAMS, SITE_METRICS


def get_program(name):
    if name not in PROGRAMS:
        raise ValueError("Unknown program")
    return deepcopy(PROGRAMS[name])


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
        return jsonify(status="healthy")

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

    @app.errorhandler(404)
    def not_found(error):
        return jsonify(error="Resource not found"), 404

    return app


app = create_app()

if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=5000, debug=False)
