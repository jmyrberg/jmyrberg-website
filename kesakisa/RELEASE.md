# Kesakisa protected preview release

This release protects entry to the app with the backend auth API. Game state is
stored in a shared JSON object through the same backend API.

## Cost guardrail

Do not run the deploy commands until the new Cloud Function has been approved.
The function is deployed as Gen 2 with `min-instances=0` and `max-instances=1`
and `concurrency=1` to keep idle runtime cost at zero and cap accidental
scale-out.

Expected resources:

- Existing GCS bucket: `gs://jmyrberg.com`
- New Cloud Functions Gen 2 HTTP function: `kesakisa_api` in `europe-west1`
- New object in existing bucket: `gs://jmyrberg.com/kesakisa/state.json`
- Build artifacts in Cloud Build / Artifact Registry from the source deploy

Cloud Functions Gen 2 runs on Cloud Run infrastructure. Runtime should not
charge while unused with `min-instances=0`. The remaining non-traffic cost to
watch is stored build artifacts. Artifact Registry currently has a small free
storage tier, but old revisions/images should be cleaned up if we start
deploying often.

## 1. Create production API env

Create the ignored production env file:

```sh
cp kesakisa/api/.env.production.yaml.example kesakisa/api/.env.production.yaml
openssl rand -hex 16
openssl rand -hex 32
```

Paste the first random value into `KESAKISA_CODE_SALT` and the second into
`KESAKISA_SESSION_SECRET`.

Print the stable configured codes locally:

```sh
cd kesakisa/api
python generate_codes.py .env.production.yaml
```

You can also use the admin app after deploy to create additional player codes.
Codes now use an 8-character hash suffix, so regenerate and hand out fresh
codes after this backend deploy.

## 2. Deploy API

This creates or updates the HTTP Cloud Function:

```sh
bash kesakisa/deploy-api.sh
```

The script prints the deployed API URL. Health check:

```sh
curl https://SERVICE_URL/health
```

## 3. Deploy static frontend

Build with the deployed API URL and upload to the existing website bucket:

```sh
API_URL=https://SERVICE_URL bash kesakisa/deploy-web.sh
```

If `API_URL` is omitted, the script asks `gcloud` for the URL of
`kesakisa_api` in `europe-west1`.

## 4. Smoke test

- Open `https://jmyrberg.com/kesakisa/`.
- Confirm player login accepts a player code.
- Open `https://jmyrberg.com/kesakisa/admin/`.
- Confirm admin login accepts the admin code.
- In admin, create a test player code and verify it logs into the player route.

## Terraform note

Terraform is useful once we want Cloud Functions service config, IAM, Artifact
Registry, and build pipeline state all managed declaratively. For this first
preview, `gcloud functions deploy --gen2` is simpler because it handles the
source build and function update in one command without adding extra Terraform
state or image-management plumbing.
