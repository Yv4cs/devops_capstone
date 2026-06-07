from app import app as flask_app


def test_health():
    client = flask_app.test_client()
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_create_and_list_note():
    client = flask_app.test_client()
    res = client.post("/api/notes", json={"content": "ci-test-note"})
    assert res.status_code == 201

    res = client.get("/api/notes")
    assert res.status_code == 200
    contents = [n["content"] for n in res.get_json()]
    assert "ci-test-note" in contents
    