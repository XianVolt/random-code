from flask import Flask, render_template, request, jsonify, session
import os
import re
import secrets
import time
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

# Rone Arena is an unofficial, community-maintained MLBB API.
API_BASE = "https://arena.fastapicloud.dev/api"
HTTP = requests.Session()
AUTH_TOKENS = {}  # Keep JWTs server-side; only an opaque session key goes in the browser cookie.
TOKEN_TTL_SECONDS = 60 * 60


def api_error(response):
    try:
        body = response.json()
        return str(body.get("msg") or body.get("message") or body.get("detail") or "The API rejected the request.")
    except (ValueError, AttributeError):
        return "The API returned an unreadable response."


def get_session_key():
    key = session.get("profile_key")
    if not key:
        key = secrets.token_urlsafe(32)
        session["profile_key"] = key
    return key


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/send-code")
def send_code():
    data = request.get_json(silent=True) or {}
    role_id = str(data.get("player_id", "")).strip()
    zone_id = str(data.get("server_id", "")).strip()

    if not re.fullmatch(r"\d{5,15}", role_id):
        return jsonify(success=False, error="Enter a valid numeric Player ID."), 400
    if not re.fullmatch(r"\d{1,8}", zone_id):
        return jsonify(success=False, error="Enter a valid numeric Server ID."), 400

    try:
        response = HTTP.post(
            f"{API_BASE}/user/auth/send-vc",
            json={"role_id": int(role_id), "zone_id": int(zone_id)},
            headers={"Accept": "application/json"},
            timeout=15,
        )
        if not response.ok:
            return jsonify(success=False, error=api_error(response)), response.status_code
        payload = response.json()
        if payload.get("code") != 0:
            return jsonify(success=False, error=api_error(response)), 502

        key = get_session_key()
        AUTH_TOKENS.pop(key, None)
        session["pending_role_id"] = role_id
        session["pending_zone_id"] = zone_id
        return jsonify(success=True, message="Verification code sent to the game's in-game mail. It expires after 5 minutes.")
    except requests.Timeout:
        return jsonify(success=False, error="The API timed out. Please try again."), 504
    except (requests.RequestException, ValueError):
        return jsonify(success=False, error="Could not contact the MLBB API. Please try again later."), 502


@app.post("/api/verify")
def verify_code():
    data = request.get_json(silent=True) or {}
    vc = str(data.get("verification_code", "")).strip()
    role_id = session.get("pending_role_id")
    zone_id = session.get("pending_zone_id")

    if not role_id or not zone_id:
        return jsonify(success=False, error="Send a verification code first."), 400
    if not re.fullmatch(r"\d{4,8}", vc):
        return jsonify(success=False, error="Enter the verification code from your in-game mail."), 400

    try:
        login = HTTP.post(
            f"{API_BASE}/user/auth/login",
            json={"role_id": int(role_id), "zone_id": int(zone_id), "vc": int(vc)},
            headers={"Accept": "application/json"},
            timeout=15,
        )
        if not login.ok:
            return jsonify(success=False, error=api_error(login)), login.status_code

        login_data = (login.json().get("data") or {})
        jwt = login_data.get("jwt")
        if not jwt:
            return jsonify(success=False, error="Login succeeded but the API did not return a session token."), 502

        key = get_session_key()
        AUTH_TOKENS[key] = {"jwt": jwt, "expires": time.time() + TOKEN_TTL_SECONDS}

        profile = HTTP.get(
            f"{API_BASE}/user/info",
            params={"lang": "en"},
            headers={"Authorization": f"Bearer {jwt}", "Accept": "application/json"},
            timeout=15,
        )
        if not profile.ok:
            AUTH_TOKENS.pop(key, None)
            return jsonify(success=False, error=api_error(profile)), profile.status_code

        profile_payload = profile.json()
        if profile_payload.get("code") != 0 or not isinstance(profile_payload.get("data"), dict):
            AUTH_TOKENS.pop(key, None)
            return jsonify(success=False, error=api_error(profile)), 502

        info = profile_payload["data"]
        rank_level = info.get("rank_level")
        history_rank_level = info.get("history_rank_level")
        session.pop("pending_role_id", None)
        session.pop("pending_zone_id", None)

        return jsonify(
            success=True,
            username=info.get("name") or "Unavailable",
            level=info.get("level") if info.get("level") is not None else "Unavailable",
            rank=rank_level if rank_level is not None else "Unavailable",
            highest_rank=history_rank_level if history_rank_level is not None else "Unavailable",
            created="Unavailable",
            note="The API does not provide an account creation date. Rank is shown as the API's rank_level value."
        )
    except requests.Timeout:
        return jsonify(success=False, error="The API timed out. Please try again."), 504
    except (requests.RequestException, ValueError):
        return jsonify(success=False, error="Could not retrieve the profile. Check the API status and try again."), 502


@app.post("/api/logout")
def logout():
    key = session.get("profile_key")
    if key:
        token_info = AUTH_TOKENS.pop(key, None)
        if token_info:
            try:
                HTTP.post(
                    f"{API_BASE}/user/auth/logout",
                    headers={"Authorization": f"Bearer {token_info['jwt']}"},
                    timeout=8,
                )
            except requests.RequestException:
                pass
    session.clear()
    return jsonify(success=True)


if __name__ == "__main__":
    app.run(debug=False)
