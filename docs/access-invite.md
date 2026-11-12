# Access-service change for independent invitations

The Fire Door App keeps each phone’s company profile, surveys and reports on that phone. Nothing in the shared app files is white-labelled per customer.

Invitations are different from sharing an access code. The owner asks the access service (Cloudflare Worker `fda-access`, URL in `BRAND.accessApi`) for a **new** code. The link only carries a one-time invite token. It must not contain the owner’s access code, the admin key, or any survey or company data.

This repository does not include the worker. As of this change, `POST /api/invite` on the live service responds `404` with `{"ok":false,"reason":"not_found"}` (the same body unknown routes already return). The app treats that as “invitations are not available yet”, shows an explanation, and does **not** create a link and does **not** read or send local surveys or the company profile.

Until the routes below exist, an invited person cannot be given their own code from the app. They can still be issued a code manually in the worker admin, and their install is still a blank phone (no owner data is stored in the app binary).

## `POST /api/invite`

Caller: a phone that is already unlocked.

```json
{ "deviceId": "<sbs_device_id>", "token": "<sbs_unlock device token>" }
```

Verify `token` the same way as `POST /api/check` (the `v1.` device token). Do not accept the raw access code here.

Success `200`:

```json
{ "ok": true, "invite": "<url-safe token, 12–200 chars of A–Z a–z 0–9 _ ->" }
```

The worker must create a **new** access code with its own device limit (1 is enough) and store `invite` as a single-use claim for that new code. The response must not include the owner’s code or the new code’s secret. Deactivating the owner’s code must not deactivate the new code, and the reverse.

Errors, JSON `{ "ok": false, "reason": "..." }`:

| Status | reason | Meaning |
| --- | --- | --- |
| 401 | `unauthorised` or `bad_token` | Caller token is not a current device token |
| 404 | `not_found` | Route not deployed (what the service returns today) |

## `POST /api/invite/redeem`

Caller: the invited phone, only when it is **not** already unlocked and has no company profile and no real survey. The app enforces that itself and will not call redeem otherwise, so a phone that already has someone else’s work never swaps its unlock token.

```json
{ "invite": "<token from the link>", "deviceId": "<this phone’s sbs_device_id>" }
```

Success `200`:

```json
{ "ok": true, "token": "<v1. device token>" }
```

Same `token` shape as a successful `POST /api/unlock`. Bind this `deviceId` to the **new** code and count it against that code’s device limit. Invalidate the invite token (single use).

Errors:

| Status | reason | Meaning |
| --- | --- | --- |
| 404 | `invite_not_found` | Unknown invite. Do **not** use `not_found` for this — the app treats `not_found` as “route not deployed” and keeps the token to retry. |
| 410 | `used` | Invite already redeemed |
| 410 | `expired` | Invite past its expiry, if you set one |

No admin key, access code, pepper or other secret is required in the app, the invite URL, or this document. Codes stay in the worker admin only.
