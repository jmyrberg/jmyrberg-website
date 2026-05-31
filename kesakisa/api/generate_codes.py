"""Print Kesakisa invite codes from a local env file."""

from __future__ import annotations

import json
import hmac
import hashlib
import os
import sys
from pathlib import Path

DEFAULT_INVITES = [
    {"name": "Jesse", "label": "Jesse", "role": "player"},
    {"name": "Jenni", "label": "Jenni", "role": "player"},
]
GENERATED_CODE_HASH_LENGTH = 8


def main() -> None:
    env_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".env.local")
    load_env_file(env_path)

    salt = os.environ["KESAKISA_CODE_SALT"]
    invites = json.loads(os.getenv("KESAKISA_INVITES_JSON", json.dumps(DEFAULT_INVITES)))

    for invite in invites:
        name = invite.get("name") or invite.get("label")
        label = invite.get("label") or name
        role = invite.get("role", "player")
        code = invite.get("code") or generated_invite_code(str(name), salt)
        print(f"{label} ({role}): {code}")


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue

        if "=" in line:
            key, value = line.split("=", 1)
        elif ":" in line:
            key, value = line.split(":", 1)
        else:
            continue

        os.environ.setdefault(key, strip_quotes(value))


def strip_quotes(value: str) -> str:
    value = value.strip()

    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]

    return value


def generated_invite_code(name: str, salt: str, nonce: str | None = None) -> str:
    normalized_name = normalize_code(name)
    normalized_nonce = normalize_code(nonce or "")
    hash_input = f"{normalized_name}:{normalized_nonce}" if normalized_nonce else normalized_name
    digest = hmac.new(
        salt.encode("utf-8"),
        hash_input.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest().upper()[:GENERATED_CODE_HASH_LENGTH]

    if normalized_nonce:
        return f"{normalized_name}-{normalized_nonce}-{digest}"

    return f"{normalized_name}-{digest}"


def normalize_code(code: str) -> str:
    return "".join(code.split()).upper()


if __name__ == "__main__":
    main()
