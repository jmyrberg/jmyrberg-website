# Kesakisa localStorage release checklist

This is the low-cost, static release path for the current localStorage version.

## What this release is

- Static PWA under `https://jmyrberg.com/kesakisa/`.
- Player route: `/kesakisa/`.
- Admin route: `/kesakisa/admin/`.
- A backend-verified code gate protects both routes.
- Data is stored in each browser's `localStorage`.
- No player/admin state is synced between devices yet.
- Admins can create additional player codes locally after logging in.

## Backend code gate

Codes live in the API environment, not in the frontend bundle.

API local setup:

```sh
cd kesakisa/api
cp .env.example .env.local
openssl rand -hex 32
```

Paste the generated value into `KESAKISA_SESSION_SECRET` in `.env.local`.

Run the API locally:

```sh
set -a
source .env.local
set +a
functions-framework --source main.py --target kesakisa_api --host 127.0.0.1 --port 8081 --debug
```

Frontend local setup:

```sh
cd kesakisa/web
cp .env.example .env.local
```

Set:

- `VITE_KESAKISA_API_BASE_URL`: API base URL, for local dev `http://127.0.0.1:8081`.

Example:

```sh
VITE_KESAKISA_API_BASE_URL=http://127.0.0.1:8081
```

Do not commit `.env.local`.

Invite names are configured in the API's `KESAKISA_INVITES_JSON` environment variable:

```sh
KESAKISA_INVITES_JSON=[{"name":"Jesse","label":"Jesse","role":"player"},{"name":"Jenni","label":"Jenni","role":"player"},{"name":"Järjestäjä","label":"Järjestäjä","role":"admin"}]
```

Codes are derived by the backend from `name + KESAKISA_CODE_SALT`, for example `JESSE-1234`. Print generated codes locally with:

```sh
cd kesakisa/api
python generate_codes.py
```

The entered code is checked only by the backend. The signed session includes the invite `label` and optional `teamId`.

Admin-created player codes use the same backend salt plus a random nonce, so they are not inspectable in the frontend. Because this localStorage version has no server-side invite database, regenerating a player code does not revoke older generated codes. Revocation needs a stored invite list or denylist in the backend.

Security note: login codes are no longer bundled into the frontend. The current release still stores game data in browser localStorage, so the next security step is moving shared game state, invite state, and admin mutations into the backend too.

## Local build

From `kesakisa/web`:

```sh
npm run build
```

The build creates:

- `dist/index.html` for `/kesakisa/`
- `dist/admin/index.html` for `/kesakisa/admin/`
- shared static assets under `dist/assets/`

The production build must set `VITE_KESAKISA_API_BASE_URL` to the deployed API URL.

## Static upload shape

Do not run these until release is approved.

```sh
cd kesakisa/web/dist
gcloud storage cp -r ./ gs://jmyrberg.com/kesakisa
gcloud storage objects update --cache-control="no-cache, max-age=0, no-transform" gs://jmyrberg.com/kesakisa/index.html gs://jmyrberg.com/kesakisa/admin/index.html
```

## Cloudflare Access shape

Create Access rules only after explicit approval.

Recommended policies:

- `jmyrberg.com/kesakisa` and `jmyrberg.com/kesakisa/*`: allow invited player and admin emails.
- `jmyrberg.com/kesakisa/admin` and `jmyrberg.com/kesakisa/admin/*`: allow admin emails only.
- Session duration: event length plus buffer, for example 7 days.
- Authentication method: email one-time PIN is likely the easiest for participants.

Important path detail: Cloudflare says a wildcard path like `/alpha/*` does not cover `/alpha`, so protect both the parent path and the wildcard path.

More specific Access paths take precedence over shared roots, so the admin path can be stricter than the player path.

Sources:

- Cloudflare Access self-hosted apps: https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/
- Cloudflare Access application paths: https://developers.cloudflare.com/cloudflare-one/access-controls/policies/app-paths/
- Cloudflare Zero Trust pricing: https://www.cloudflare.com/en-gb/plans/zero-trust-services/
- Google Cloud Storage pricing: https://cloud.google.com/storage/pricing

## Cost guardrails

- Reusing the existing GCS website bucket should keep this tiny, but traffic/storage can still incur normal GCS charges.
- Cloudflare Zero Trust currently advertises a free plan for small teams; verify the current user limit before release.
- The auth API needs a backend endpoint. A Cloud Function deployment can stay tiny, but it should still be approved before release because it is a billable Google Cloud resource.
- No database, Worker, KV, D1, R2, or new bucket is required for this localStorage release.
- The synced multi-device version will require new backend/storage decisions and explicit approval before any resources are created.
