"""Kesakisa auth API.

Codes are verified server-side and exchanged for signed session tokens.
The current frontend can keep using localStorage for game data while this
API handles non-inspectable login codes.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import time
from typing import Any

from flask import Request, Response


DEFAULT_SESSION_TTL_SECONDS = 7 * 24 * 60 * 60
DEFAULT_INVITES = [
    {"name": "Jesse", "label": "Jesse", "role": "player"},
    {"name": "Jenni", "label": "Jenni", "role": "player"},
]
GENERATED_CODE_HASH_LENGTH = 8
EDGE_SECRET_HEADER = "X-Kesakisa-Edge-Secret"


def kesakisa_api(request: Request) -> Response:
    """Cloud Functions / functions-framework entrypoint."""
    cors_headers = _cors_headers(request)

    if request.method == "OPTIONS":
        return _empty_response(204, cors_headers)

    try:
        if not _edge_request_allowed(request):
            return _json_response({"status": "error", "message": "Not found"}, 404, cors_headers)

        path = request.path.rstrip("/") or "/"

        if request.method == "GET" and path.endswith("/health"):
            return _json_response({"status": "success", "data": {"ok": True}}, 200, cors_headers)

        if request.method == "POST" and path.endswith("/login"):
            return _login(request, cors_headers)

        if request.method == "POST" and path.endswith("/invite-code"):
            return _invite_code_response(request, cors_headers)

        if request.method == "GET" and path.endswith("/state"):
            return _state_response(request, cors_headers)

        if request.method == "PUT" and path.endswith("/state"):
            return _save_state_response(request, cors_headers)

        if request.method == "GET" and path.endswith("/me"):
            return _me(request, cors_headers)

        return _json_response({"status": "error", "message": "Not found"}, 404, cors_headers)
    except AuthConfigurationError as error:
        return _json_response({"status": "error", "message": str(error)}, 500, cors_headers)
    except Exception:
        return _json_response({"status": "error", "message": "Unexpected auth error"}, 500, cors_headers)


def _login(request: Request, cors_headers: dict[str, str]) -> Response:
    payload = request.get_json(silent=True) or {}
    code = _normalize_code(str(payload.get("code", "")))
    required_role = _normalize_role(payload.get("requiredRole"), default="player")
    invite = _invite_for_code(code)

    if not invite or not _can_access(required_role, invite["role"]):
        return _json_response({"status": "error", "message": "Invalid code"}, 401, cors_headers)

    session = _create_session(invite)
    return _json_response({"status": "success", "data": session}, 200, cors_headers)


def _me(request: Request, cors_headers: dict[str, str]) -> Response:
    token = _bearer_token(request)

    if not token:
        return _json_response({"status": "error", "message": "Missing session"}, 401, cors_headers)

    session = _verify_session(token)

    if not session:
        return _json_response({"status": "error", "message": "Invalid session"}, 401, cors_headers)

    return _json_response({"status": "success", "data": session}, 200, cors_headers)


def _invite_code_response(request: Request, cors_headers: dict[str, str]) -> Response:
    admin_session = _verified_session_from_request(request)

    if not admin_session or admin_session["role"] != "admin":
        return _json_response({"status": "error", "message": "Admin session required"}, 403, cors_headers)

    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()

    if not name:
        return _json_response({"status": "error", "message": "Name is required"}, 400, cors_headers)

    invite = {
        "name": name,
        "label": name,
        "role": "player",
        "code": generated_invite_code(name, _code_salt(), nonce=secrets.token_hex(2).upper()),
    }

    return _json_response({"status": "success", "data": invite}, 200, cors_headers)


def _state_response(request: Request, cors_headers: dict[str, str]) -> Response:
    session = _verified_session_from_request(request)

    if not session:
        return _json_response({"status": "error", "message": "Session required"}, 401, cors_headers)

    return _json_response({"status": "success", "data": {"state": _load_game_state()}}, 200, cors_headers)


def _save_state_response(request: Request, cors_headers: dict[str, str]) -> Response:
    session = _verified_session_from_request(request)

    if not session or session["role"] != "admin":
        return _json_response({"status": "error", "message": "Admin session required"}, 403, cors_headers)

    payload = request.get_json(silent=True) or {}
    state = payload.get("state")

    if not isinstance(state, dict):
        return _json_response({"status": "error", "message": "State object is required"}, 400, cors_headers)

    _save_game_state(state)
    return _json_response({"status": "success", "data": {"state": state}}, 200, cors_headers)


def _create_session(invite: dict[str, Any]) -> dict[str, Any]:
    now = int(time.time())
    expires_at = now + _session_ttl_seconds()
    payload = {
        "role": invite["role"],
        "label": invite["label"],
        "teamId": invite.get("teamId"),
        "grantedAt": _iso_timestamp(now),
        "expiresAt": _iso_timestamp(expires_at),
        "iat": now,
        "exp": expires_at,
    }
    token = _sign_payload(payload)

    return {
        "role": payload["role"],
        "label": payload["label"],
        "teamId": payload["teamId"],
        "grantedAt": payload["grantedAt"],
        "expiresAt": payload["expiresAt"],
        "token": token,
    }


def _verify_session(token: str) -> dict[str, Any] | None:
    try:
        encoded_payload, encoded_signature = token.split(".", 1)
        payload_bytes = _base64url_decode(encoded_payload)
        expected_signature = _session_signature(encoded_payload)

        if not hmac.compare_digest(encoded_signature, expected_signature):
            return None

        payload = json.loads(payload_bytes.decode("utf-8"))
        role = _normalize_role(payload.get("role"), default="")
        label = str(payload.get("label", "")).strip()
        expires_at = int(payload.get("exp", 0))

        if role not in {"player", "admin"} or not label or expires_at < int(time.time()):
            return None

        return {
            "role": role,
            "label": label,
            "teamId": payload.get("teamId"),
            "grantedAt": str(payload["grantedAt"]),
            "expiresAt": str(payload["expiresAt"]),
            "token": token,
        }
    except Exception:
        return None


def _sign_payload(payload: dict[str, Any]) -> str:
    encoded_payload = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = _session_signature(encoded_payload)
    return f"{encoded_payload}.{signature}"


def _session_signature(encoded_payload: str) -> str:
    digest = hmac.new(
        _session_secret().encode("utf-8"),
        encoded_payload.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return _base64url_encode(digest)


def _invite_for_code(code: str) -> dict[str, Any] | None:
    return _invites_by_code().get(code) or _generated_player_invite_for_code(code)


def _generated_player_invite_for_code(code: str) -> dict[str, Any] | None:
    if "-" not in code:
        return None

    code_parts = code.split("-")

    if len(code_parts) >= 3:
        name_part = "-".join(code_parts[:-2])
        nonce = code_parts[-2]
    else:
        name_part = code_parts[0]
        nonce = None

    expected_code = generated_invite_code(name_part, _code_salt(), nonce=nonce)

    if not hmac.compare_digest(code, expected_code):
        return None

    return {
        "role": "player",
        "label": name_part.title(),
        "teamId": None,
    }


def _can_access(required_role: str, granted_role: str) -> bool:
    return granted_role == "admin" or required_role == granted_role


def _invites_by_code() -> dict[str, dict[str, Any]]:
    invites = {}

    for invite in _load_invites():
        normalized_code = _invite_code(invite)
        role = _normalize_role(invite.get("role"), default="")
        label = str(invite.get("label", "")).strip()

        if not normalized_code or role not in {"player", "admin"} or not label:
            continue

        invites[normalized_code] = {
            "role": role,
            "label": label,
            "teamId": invite.get("teamId"),
        }

    return invites


def _invite_code(invite: dict[str, Any]) -> str:
    explicit_code = _normalize_code(str(invite.get("code", "")))

    if explicit_code:
        return explicit_code

    name = str(invite.get("name") or invite.get("label") or "").strip()

    if not name:
        return ""

    return generated_invite_code(name, _code_salt())


def _load_invites() -> list[dict[str, Any]]:
    raw_invites = os.getenv("KESAKISA_INVITES_JSON", "").strip()

    if raw_invites:
        try:
            parsed = json.loads(raw_invites)

            if isinstance(parsed, list):
                return [invite for invite in parsed if isinstance(invite, dict)]
        except json.JSONDecodeError as error:
            raise AuthConfigurationError("KESAKISA_INVITES_JSON is not valid JSON") from error

    legacy_invites = []

    for code in _parse_legacy_codes(os.getenv("KESAKISA_PLAYER_CODES", "")):
        legacy_invites.append({"code": code, "label": code.title(), "role": "player"})

    for code in _parse_legacy_codes(os.getenv("KESAKISA_ADMIN_CODES", "")):
        legacy_invites.append({"code": code, "label": code.title(), "role": "admin"})

    return legacy_invites or DEFAULT_INVITES


def _parse_legacy_codes(value: str) -> list[str]:
    return [_normalize_code(code) for code in value.split(",") if _normalize_code(code)]


def generated_invite_code(name: str, salt: str, nonce: str | None = None) -> str:
    normalized_name = _normalize_code(name)
    normalized_nonce = _normalize_code(nonce or "")
    hash_input = f"{normalized_name}:{normalized_nonce}" if normalized_nonce else normalized_name
    digest = hmac.new(
        salt.encode("utf-8"),
        hash_input.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest().upper()[:GENERATED_CODE_HASH_LENGTH]

    if normalized_nonce:
        return f"{normalized_name}-{normalized_nonce}-{digest}"

    return f"{normalized_name}-{digest}"


def _code_salt() -> str:
    salt = os.getenv("KESAKISA_CODE_SALT", "")

    if len(salt) < 16:
        raise AuthConfigurationError("KESAKISA_CODE_SALT must be at least 16 characters")

    return salt


def _normalize_code(code: str) -> str:
    return "".join(code.split()).upper()


def _normalize_role(value: Any, default: str) -> str:
    return value if value in {"player", "admin"} else default


def _bearer_token(request: Request) -> str | None:
    authorization = request.headers.get("Authorization", "")

    if not authorization.lower().startswith("bearer "):
        return None

    return authorization[7:].strip()


def _verified_session_from_request(request: Request) -> dict[str, Any] | None:
    token = _bearer_token(request)

    if not token:
        return None

    return _verify_session(token)


def _session_secret() -> str:
    secret = os.getenv("KESAKISA_SESSION_SECRET", "")

    if len(secret) < 32:
        raise AuthConfigurationError("KESAKISA_SESSION_SECRET must be at least 32 characters")

    return secret


def _session_ttl_seconds() -> int:
    raw_value = os.getenv("KESAKISA_SESSION_TTL_SECONDS", str(DEFAULT_SESSION_TTL_SECONDS))

    try:
        return max(60, int(raw_value))
    except ValueError:
        return DEFAULT_SESSION_TTL_SECONDS


def _cors_headers(request: Request) -> dict[str, str]:
    allowed_origins = _allowed_origins()
    origin = request.headers.get("Origin")
    headers = {
        "Access-Control-Allow-Methods": "GET, POST, PUT, OPTIONS",
        "Access-Control-Allow-Headers": "Authorization, Content-Type",
        "Access-Control-Max-Age": "3600",
    }

    if "*" in allowed_origins:
        headers["Access-Control-Allow-Origin"] = "*"
    elif origin and origin in allowed_origins:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Vary"] = "Origin"

    return headers


def _allowed_origins() -> set[str]:
    raw_origins = os.getenv(
        "KESAKISA_CORS_ORIGINS",
        "http://127.0.0.1:5174,http://localhost:5174",
    )
    return {origin.strip() for origin in raw_origins.replace(";", ",").split(",") if origin.strip()}


def _edge_request_allowed(request: Request) -> bool:
    expected_secret = os.getenv("KESAKISA_EDGE_SECRET", "").strip()

    if not expected_secret:
        return True

    return hmac.compare_digest(request.headers.get(EDGE_SECRET_HEADER, ""), expected_secret)


def _load_game_state() -> dict[str, Any] | None:
    bucket_name = os.getenv("KESAKISA_STATE_BUCKET", "").strip()

    if bucket_name:
        blob = _state_bucket_blob()

        if not blob.exists():
            return None

        return json.loads(blob.download_as_text(encoding="utf-8"))

    state_path = _state_file_path()

    if not state_path.exists():
        return None

    return json.loads(state_path.read_text(encoding="utf-8"))


def _save_game_state(state: dict[str, Any]) -> None:
    payload = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
    bucket_name = os.getenv("KESAKISA_STATE_BUCKET", "").strip()

    if bucket_name:
        blob = _state_bucket_blob()
        blob.cache_control = "no-cache, max-age=0, no-transform"
        blob.upload_from_string(payload, content_type="application/json; charset=utf-8")
        return

    state_path = _state_file_path()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(payload, encoding="utf-8")


def _state_bucket_blob() -> Any:
    from google.cloud import storage

    bucket_name = os.environ["KESAKISA_STATE_BUCKET"].strip()
    object_name = os.getenv("KESAKISA_STATE_OBJECT", "kesakisa/state.json").strip() or "kesakisa/state.json"
    client = storage.Client()
    return client.bucket(bucket_name).blob(object_name)


def _state_file_path() -> Path:
    return Path(os.getenv("KESAKISA_STATE_FILE", "/tmp/kesakisa-state.json"))


def _json_response(payload: dict[str, Any], status: int, headers: dict[str, str]) -> Response:
    return Response(
        json.dumps(payload, ensure_ascii=False),
        status=status,
        headers={**headers, "Content-Type": "application/json; charset=utf-8"},
    )


def _empty_response(status: int, headers: dict[str, str]) -> Response:
    return Response("", status=status, headers=headers)


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}")


def _iso_timestamp(timestamp: int) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(timestamp))


class AuthConfigurationError(Exception):
    """Raised when auth environment variables are missing or unsafe."""
