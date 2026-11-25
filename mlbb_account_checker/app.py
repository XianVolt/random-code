from flask import Flask, render_template, request, jsonify
import requests, re

app = Flask(__name__)
API_URL = "https://api.rantey.com/v1/mlbb/{player_id}/{server_id}"

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/api/check")
def check():
    data = request.get_json(silent=True) or {}
    pid = str(data.get("player_id", "")).strip()
    sid = str(data.get("server_id", "")).strip()
    if not re.fullmatch(r"\\d{5,15}", pid):
        return jsonify(success=False, error="Enter a valid numeric Player ID."), 400
    if not re.fullmatch(r"\\d{1,8}", sid):
        return jsonify(success=False, error="Enter a valid numeric Server ID."), 400
    try:
        r = requests.get(API_URL.format(player_id=pid, server_id=sid),
                         headers={"Accept":"application/json"}, timeout=12)
        if r.status_code == 404:
            return jsonify(success=False, error="Account not found by the lookup service."), 404
        r.raise_for_status()
        payload = r.json()

        def find(keys, obj):
            if isinstance(obj, dict):
                for k in keys:
                    if obj.get(k) not in (None, ""):
                        return obj[k]
                for v in obj.values():
                    got = find(keys, v)
                    if got not in (None, ""):
                        return got
            elif isinstance(obj, list):
                for v in obj:
                    got = find(keys, v)
                    if got not in (None, ""):
                        return got
            return None

        username = find(["username","name","nickname","nickName"], payload)
        level = find(["level","account_level","accountLevel"], payload)
        created = find(["created_at","createdAt","register_time","registerTime",
                        "registration_date","registrationDate","create_time","createTime"], payload)
        if username is None and level is None:
            return jsonify(success=False, error="The API returned no recognizable profile data."), 502
        return jsonify(success=True, username=username or "Unavailable",
                       level=level if level is not None else "Unavailable",
                       created=created if created is not None else "Unavailable",
                       note="" if created is not None else "Creation date was not supplied by the API.")
    except requests.Timeout:
        return jsonify(success=False, error="Lookup service timed out. Try again."), 504
    except (requests.RequestException, ValueError):
        return jsonify(success=False, error="Lookup service unavailable or returned invalid data."), 502

if __name__ == "__main__":
    app.run(debug=False)
