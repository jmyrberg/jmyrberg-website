# Kesakisa API

Small auth API for the static Kesakisa app.

The frontend never receives the allowed login codes. It sends a code to `/login`,
and the API returns a signed session token if the code is valid.

## Local setup

```sh
cd kesakisa/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env.local
```

Generate a local session secret:

```sh
openssl rand -hex 32
```

Paste it into `KESAKISA_SESSION_SECRET` in `.env.local`.

Generate a local code salt:

```sh
openssl rand -hex 16
```

Paste it into `KESAKISA_CODE_SALT` in `.env.local`.

Invites are configured as JSON in `KESAKISA_INVITES_JSON`:

```sh
KESAKISA_INVITES_JSON=[{"name":"Jesse","label":"Jesse","role":"player"},{"name":"Jenni","label":"Jenni","role":"player"},{"name":"Järjestäjä","label":"Järjestäjä","role":"admin"}]
```

Codes are derived from `name + KESAKISA_CODE_SALT` and use the format
`NAME-XXXXXXXX`. The `label` is returned in the signed session so the app can
distinguish users later. Optional `teamId` can be added when codes should map
directly to teams.

Print local codes to hand out:

```sh
python generate_codes.py
```

Admins can also create additional player codes through `POST /invite-code`.
Those generated codes use the format `NAME-NONCE-XXXXXXXX`.

Important limitation: generated codes are stateless in this version. Creating a
new code for the same player does not revoke an older generated code. Revoking
old codes requires a stored invite list or denylist in the backend.

## Local run

```sh
set -a
source .env.local
set +a
functions-framework --source main.py --target kesakisa_api --host 127.0.0.1 --port 8081 --debug
```

The frontend should use:

```sh
VITE_KESAKISA_API_BASE_URL=http://127.0.0.1:8081
```

Local game state is stored in `KESAKISA_STATE_FILE`, defaulting to
`/tmp/kesakisa-state.json` if no GCS bucket is configured.

## Endpoints

- `POST /login` with `{ "code": "...", "requiredRole": "player" | "admin" }`
- `GET /me` with `Authorization: Bearer <token>`
- `POST /invite-code` with admin `Authorization: Bearer <token>` and `{ "name": "..." }`
- `GET /state` with player/admin `Authorization: Bearer <token>`
- `PUT /state` with admin `Authorization: Bearer <token>` and `{ "state": {...} }`
- `GET /health`

## Security scope

This removes login codes from the frontend bundle and protects the shared game
state JSON behind signed sessions. Players can read shared state. Admins can
write it. The Cloud Function URL is public, but `/state` is not useful without a
valid session token. Login remains public so players can exchange a code for a
session.
