import ast
from pathlib import Path
import pytest
from markupsafe import escape
from app import create_app, get_program
from programs import PROGRAMS, SITE_METRICS


def test_baseline_program_content_is_preserved():
    source = Path("original/Aceestver-1.0.py").read_text(encoding="utf-8")
    original = None
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute) and target.attr == "programs":
                    original = ast.literal_eval(node.value)
    assert original is not None
    assert PROGRAMS == original


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.content_type.startswith("text/html")
    text = response.get_data(as_text=True)
    assert "ACEest FUNCTIONAL FITNESS" in text
    assert "Select a profile to view workout" in text
    assert "Select a profile to view diet" in text
    assert "150 Users" in text
    assert "10,000 sq ft" in text
    assert "250 Members" in text
    for name in PROGRAMS:
        assert name in text


@pytest.mark.parametrize("name", list(PROGRAMS))
def test_web_program_selection(client, name):
    response = client.get("/", query_string={"program": name})
    assert response.status_code == 200

    text = response.get_data(as_text=True)

    expected_workout = str(escape(PROGRAMS[name]["workout"]))
    expected_diet = str(escape(PROGRAMS[name]["diet"]))

    assert expected_workout in text
    assert expected_diet in text
    assert PROGRAMS[name]["color"] in text


def test_bad_web_selection(client):
    response = client.get("/", query_string={"program": "not-a-program"})
    assert response.status_code == 400
    assert "Unknown program" in response.get_data(as_text=True)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "healthy"}


def test_list_programs(client):
    response = client.get("/api/programs")
    assert response.status_code == 200
    assert response.json == {"programs": PROGRAMS}


@pytest.mark.parametrize("name", list(PROGRAMS))
def test_program_api(client, name):
    response = client.get("/api/program", query_string={"name": name})
    assert response.status_code == 200
    assert response.json == {"name": name, **PROGRAMS[name]}


@pytest.mark.parametrize("query", [{}, {"name": ""}])
def test_missing_program_name(client, query):
    response = client.get("/api/program", query_string=query)
    assert response.status_code == 400
    assert "required" in response.json["error"]


@pytest.mark.parametrize("name", ["Unknown", "fat loss (fl)", " ", "<script>alert(1)</script>"])
def test_unknown_program(client, name):
    response = client.get("/api/program", query_string={"name": name})
    assert response.status_code == 404
    assert response.json == {"error": "Unknown program"}


def test_metrics(client):
    response = client.get("/api/metrics")
    assert response.status_code == 200
    assert response.json == SITE_METRICS
    assert SITE_METRICS == {
        "capacity_users": 150, "area_sq_ft": 10000, "break_even_members": 250,
    }


def test_missing_route(client):
    response = client.get("/missing")
    assert response.status_code == 404
    assert response.json == {"error": "Resource not found"}


def test_method_not_allowed(client):
    assert client.post("/api/programs").status_code == 405


@pytest.mark.parametrize("name", list(PROGRAMS))
def test_lookup_logic(name):
    assert get_program(name) == PROGRAMS[name]


def test_lookup_unknown():
    with pytest.raises(ValueError, match="Unknown program"):
        get_program("missing")


def test_lookup_does_not_expose_mutable_data():
    name = "Beginner (BG)"
    result = get_program(name)
    result["diet"] = "changed"
    assert get_program(name)["diet"] == PROGRAMS[name]["diet"]
    assert get_program(name)["diet"] != "changed"


def test_factory_config():
    assert create_app({"TESTING": True}).testing is True
    assert create_app().testing is False
