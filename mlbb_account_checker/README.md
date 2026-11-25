# MLBB Account Checker

Flask web app using the community-maintained Rone Arena API.

## Run on Windows

1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Install dependencies:
   `py -m pip install -r requirements.txt`
4. Run:
   `py app.py`
5. Open http://127.0.0.1:5000.

## How profile lookup works

1. Enter your MLBB Player ID (Role ID) and Server ID (Zone ID).
2. Choose **Send In-Game Code**. The API requests a verification code through the game's in-game mail.
3. Enter the code you requested and choose **Verify & Check Account**.
4. The app requests your profile using the temporary API login token.

The app never asks for your game password. Do not share verification codes or tokens. The token is kept server-side in process memory and is removed when you log out or restart the app.

## Data availability

- Username and level: returned by the authenticated `GET /api/user/info` endpoint.
- Current rank level and highest rank level: shown from the API's numeric `rank_level` and `history_rank_level` fields.
- Account creation date: shown as **Unavailable** because the documented user profile endpoint does not provide it.

## API details

- Provider: Rone Arena, an unofficial community-maintained API; not affiliated with Moonton.
- Base URL: `https://arena.fastapicloud.dev/api`
- Endpoints: `POST /user/auth/send-vc`, `POST /user/auth/login`, `GET /user/info`, and `POST /user/auth/logout`.
- API documentation: https://arena.rone.dev/web/user

For deployment, set a strong `FLASK_SECRET_KEY` environment variable and use HTTPS. This simple project stores active JWTs in memory, so active sessions are cleared when the server restarts.