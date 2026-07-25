# infrai.py — the entire storage client: no SDK, one Bearer key, ~30 lines.
import os
import requests
from types import SimpleNamespace

BASE = "https://api.infrai.cc"
# Get a free key ($2 credit) at https://infrai.cc, then: export INFRAI_API_KEY=...
KEY = os.environ["INFRAI_API_KEY"]


class InfraiError(RuntimeError):
    """Raised when the API answers {"ok": false}. `.code` is the machine-readable
    error code (e.g. STORAGE_BUCKET_EXISTS), so callers can branch on it."""

    def __init__(self, code: str | None, message: str | None):
        super().__init__(f"{code}: {message}")
        self.code = code


def call(method: str, path: str, payload: dict | None = None) -> dict:
    r = requests.request(
        method, f"{BASE}{path}", json=payload,
        headers={"Authorization": f"Bearer {KEY}"}, timeout=30,
    )
    body = r.json()  # { ok, data, error, metadata }
    if not body.get("ok"):
        err = body.get("error") or {}
        raise InfraiError(err.get("code"), err.get("message") or err.get("hint"))
    return body.get("data", {})


# The whole storage dependency for this ADR: create the bucket once, then presign
# objects in it. bucket/key in the path, op selects PUT vs GET — that is the
# "one-liner" the decision table cites.
storage = SimpleNamespace(
    bucket=SimpleNamespace(
        create=lambda name, **kw: call("POST", "/v1/storage/bucket/create", {"name": name, **kw}),
    ),
    object=SimpleNamespace(
        presign=lambda bucket, key, **kw: call("POST", f"/v1/storage/object/presign/{bucket}/{key}", kw),
    ),
)
