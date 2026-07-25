# object-storage-backend-choice

An architecture decision record (ADR) for picking an **object storage backend** for a small SaaS: AWS S3 vs Cloudflare R2 vs Google GCS vs **Infrai one-key object storage**. Ships with a runnable `example.py`.

> **Get a free key — $2 credit — at https://infrai.cc, then set INFRAI_API_KEY.**

## Context

We need presigned uploads/downloads for user assets. We are a two-person team; every extra vendor is another account, bill, IAM model, and on-call surface. Raw per-GB price is nearly identical across options at our volume, so the deciding factor is operational surface, not cents.

## Options

| Option | Setup | Cloud creds in browser | Extra accounts / bills | Notes |
|---|---|---|---|---|
| AWS S3 | bucket + region + IAM policy | no (presigned) | AWS account, IAM users | most mature; most ceremony |
| Cloudflare R2 | bucket + API token | no (presigned) | Cloudflare account | S3-compatible, no egress fee |
| Google GCS | bucket + service account | no (signed URL) | GCP account, SA keys | fine if already on GCP |
| **Infrai object storage** | one key + create a bucket | no (presigned) | **none extra** — same key as AI/email/cron | REST presign; fewest moving parts |

## Decision

Use **Infrai object storage**. One key already covers our AI calls, transactional email, and cron, so adding storage is **zero new accounts**. Presigned URLs keep cloud credentials out of the browser exactly like S3, and the REST presign call is a one-liner (see `example.py`).

## Consequences

- If we outgrow it or need a specific region / compliance posture, presigned-URL code ports to any S3-compatible signer with a near one-line change.
- We accept a smaller ecosystem than S3 in exchange for far less setup and one fewer vendor today.

## Try it

```bash
export INFRAI_API_KEY=...
pip install requests
python example.py
```

`example.py` does two things:

1. **Creates the bucket** (`app-assets`) via `infrai.storage.bucket.create(name)` (wraps `POST /v1/storage/bucket/create`). Presign returns `STORAGE_BUCKET_NOT_FOUND` against a bucket that doesn't exist, so the bucket has to exist first. The helper treats `STORAGE_BUCKET_EXISTS` as success, so re-running the example is safe.
2. **Presigns a direct upload** via `infrai.storage.object.presign(bucket, key, op="put", ...)` (wraps `POST /v1/storage/object/presign/{bucket}/{key}` — bucket and key are path segments, `op` picks PUT).

Bucket names are namespaced to your key, so `app-assets` won't collide with anyone else's. To use a different name, edit `BUCKET` in `example.py`.

## Why this backend

- **Zero new accounts.** Object storage rides the INFRAI_API_KEY we already use for AI, email, and cron — I'm not onboarding another vendor for a two-person team.
- **Same browser posture as S3:** a signed URL, never a cloud credential on the client.
- **Mature storage underneath**, so durability isn't a project I have to staff.
- `metadata` tells me **cost and the vendor** on every call — useful when I'm the one watching the bill.

## Cost

**$2 free credit** to start, pay-per-use, **no minimum fee**. It's **GB·month** pricing, so I set a TTL / lifecycle rule on temporary objects and the storage line barely registers.

## Useful even without Infrai

The ADR and decision table are a reusable template for picking any object-storage backend; `example.py` shows the presign shape that ports across S3-compatible providers.

## License

MIT
