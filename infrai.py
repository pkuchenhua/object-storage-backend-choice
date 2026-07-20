# infrai.py — the entire storage client: no SDK, one Bearer key, ~20 lines.
import os
import requests
from types import SimpleNamespace

BASE = "https://api.infrai.cc"
# Get a free key ($2 credit) at https://infrai.cc, then: export INFRAI_API_KEY=...
KEY = os.environ["INFRAI_API_KEY"]


def call(method: str, path: str, payload: dict | None = None) -> dict:
    r = requests.request(
        method, f"{BASE}{path}", json=payload,
        headers={"Authorization": f"Bearer {KEY}"}, timeout=30,
    )
    body = r.json()  # { ok, data, error, metadata }
    if not body.get("ok"):
        err = body.get("error") or {}
        raise RuntimeError(f"{err.get('code')}: {err.get('hint')}")
    return body.get("data", {})


# The whole storage dependency for this ADR: presign one object. bucket/key in the
# path, op selects PUT vs GET — that is the "one-liner" the decision table cites.
storage = SimpleNamespace(
    object=SimpleNamespace(
        presign=lambda bucket, key, **kw: call("POST", f"/v1/storage/object/presign/{bucket}/{key}", kw),
    ),
)
