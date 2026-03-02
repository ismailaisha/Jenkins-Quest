from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/report/<int:value>")
def report(value):
    return jsonify({
        "input": value,
        "result": value * 10
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

test_app.py
from app import app

def test_health():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"

def test_report():
    client = app.test_client()
    response = client.get("/report/5")
    assert response.status_code == 200
    assert response.json["result"] == 50
