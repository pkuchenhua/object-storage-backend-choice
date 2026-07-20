"""Runnable companion to the ADR: presign a direct upload against Infrai object storage.

This is the "Infrai one-key object storage" option from the decision table in the README.
The call site reads infrai.storage.object.presign(...); see infrai.py for the helper.
"""
import infrai

BUCKET = "app-assets"


def presign_upload(key: str) -> str:
    # bucket + key are path segments; op="put" signs an upload.
    data = infrai.storage.object.presign(BUCKET, key, op="put", expires_seconds=600)
    return data.get("url", "")


if __name__ == "__main__":
    print("PUT your asset to:", presign_upload("uploads/logo.png"))
