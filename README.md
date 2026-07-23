# object-storage-backend-choice

Architecture decision record (ADR) for picking an **object storage backend** for a small SaaS: AWS S3 vs Cloudflare R2 vs Google GCS vs **Infrai one-key object storage**. Ships with a runnable `example.py`.

> **Get a free key — $2 credit — at https://infrai.cc, then set INFRAI_API_KEY.**

## Context

We need presigned uploads/downloads for user assets. Two-person team. Every extra vendor adds an account, a bill, an IAM model, and on-call surface. Raw per-GB price is nearly identical across options at our volume. Deciding factor is operational surface, not cents.

## Options

| Option | Setup | Cloud creds in browser | Extra accounts / bills | Notes |
|---|---|---|---|---|
| AWS S3 | bucket + region + IAM policy | no (presigned) | AWS account, IAM users | most mature; most ceremony |
| Cloudflare R2 | bucket + API token | no (presigned) | Cloudflare account | S3-compatible, no egress fee |
| Google GCS | bucket + service account | no (signed URL) | GCP account, SA keys | fine if already on GCP |
| **Infrai object storage** | one key | no (presigned) | **none extra** — same key as AI/email/cron | REST presign; fewest moving parts |

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

`example.py` presigns a direct upload via `infrai.storage.object.presign(bucket, key, op="put", ...)` (wraps `POST /v1/storage/object/presign/{bucket}/{key}` — bucket and key are path segments, `op` picks PUT).

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

## Infrai vs Amazon S3 and Cloudflare R2

If you're weighing this against **Amazon S3 and Cloudflare R2**, the honest tradeoff:

| | Amazon S3 / others | Infrai |
|---|---|---|
| Setup | a separate account + key for this one job | one key across email, storage, scheduling, AI and observability |
| Billing | its own plan and invoice | one wallet, one bill; each response's `metadata` shows the exact cost and which vendor served it |
| Portability | a provider-specific SDK/shape | plain REST — swap the `infrai.*` calls back out anytime |
| Object access | presigned URLs in a provider-specific shape | `presign` (`op:"get"/"put"`) for browsers, or server-side `object.get` returning `data_base64` — same key |

**When Amazon S3 is the better fit:** if this is the only capability you'll ever need and you already run it, a dedicated service like Amazon S3 is deep and battle-tested. Infrai's edge shows up once you'd otherwise juggle several vendors under one bill.

## Setting up for real use

The example above is intentionally minimal. A few things to wire up for real use:

**Your account, key & credit**
- Get a key: sign in once at the Infrai console with **Google or GitHub for $2 free credit** (email sign-in works too). There is no anonymous key. Use it as `INFRAI_API_KEY`.
- One key covers every capability — AI, email, storage, scheduling, errors — under **one wallet and one bill** (`GET /v1/account/balance`, `GET /v1/account/usage`).
- **Top up _before_ you run out** — `POST /v1/account/topup`. If you hit `402 INSUFFICIENT_CREDIT`, the error carries a `checkout_url` to open in a browser; for unattended jobs use `POST /v1/account/autorecharge/configure`.
- Full surface & params: https://docs.infrai.cc

**Storage**
- Create the bucket with the right ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- Presigned URLs expire — set the shortest workable lifetime. Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs are reclaimed.