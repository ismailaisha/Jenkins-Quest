from app import app

def test_health():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_report():
    client = app.test_client()
    response = client.get("/report/5")

    assert response.status_code == 200
    assert response.get_json()["result"] == 50