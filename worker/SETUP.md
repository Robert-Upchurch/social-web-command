# Social & Web Command — Sync Proxy Worker

A tiny Cloudflare Worker that proxies Frame.io and HeyGen API calls so the hub at
`https://robert-upchurch.github.io/social-web-command/` can sync them without browser
CORS errors.

It is **stateless**: no database, no stored credentials. The hub sends the API key
on every request; the Worker forwards it to the upstream API and normalises the
response.

---

## What you get when this is set up

- Frame.io "Sync now" button works from the browser (no more CORS error)
- HeyGen "Sync now" button works from the browser (no more CORS error)
- Frame.io / HeyGen integration modal shows a green "Server sync ready (via proxy)" banner
- Settings → Sync Proxy shows "● Proxy reachable" when you click *Test Connection*

---

## Deploy in 3 minutes (Cloudflare Dashboard, no terminal needed)

1. Sign in at https://dash.cloudflare.com/
2. Left sidebar → **Workers & Pages** → **Create application** → **Create Worker**
3. Name it `swc-sync-proxy` → **Deploy**
4. After it deploys, click **Edit code**
5. Open `src/index.js` from this folder, copy the full contents
6. In the Cloudflare editor, replace the default code on the left with what you copied
7. Click **Save and deploy** (top right)
8. Copy the URL Cloudflare gives you. It looks like:
   `https://swc-sync-proxy.<your-subdomain>.workers.dev`
9. (Recommended) Add a shared secret so nobody else can use your Worker as a free proxy:
   - In the Worker page → **Settings** → **Variables** → **Add variable**
   - Type: **Encrypted**, name: `HUB_SHARED_SECRET`, value: any long random string (save it)
   - Click **Save and deploy**
10. (Optional, only if you change the hub URL later) add another variable:
    - Type: **Plaintext**, name: `ALLOWED_ORIGIN`, value: `https://robert-upchurch.github.io`

---

## Wire the hub to the Worker

1. Open the hub: https://robert-upchurch.github.io/social-web-command/
2. Go to **Settings** (left nav, bottom)
3. Scroll to **Sync Proxy (Cloudflare Worker)**
4. Paste your Worker URL into **Worker URL**
5. Paste the secret you set in step 9 above into **Shared secret** (leave blank if you skipped that step)
6. Click **Save**
7. Click **Test Connection** — you should see: `● Proxy reachable — social-web-command-sync v1.0.0`

---

## Use it

1. Settings → **Integrations** → click **Connect** next to **Frame.io**
2. Paste your Frame.io API token, Account ID, Workspace ID, click **Save**
3. The status banner should now be green: *Server sync ready (via proxy)*
4. Click **Sync now** — projects will appear in **Library → Videos**

Same flow for HeyGen (just an API key — no extra IDs).

---

## API reference (in case you want to test directly)

```
GET  /
POST /sync/frameio   { token, accountId, workspaceId }
POST /sync/heygen    { token, limit }
```

Headers: `Content-Type: application/json`, optionally `X-Hub-Secret: <your secret>`

All POST endpoints return:
```json
{ "ok": true, "provider": "...", "items": [...], "total": N }
```
or on upstream error:
```json
{ "ok": false, "error": "Frame.io 401: ..." }
```

---

## Costs

Cloudflare Workers free tier covers 100,000 requests/day. Each "Sync now" click =
1 request. You won't come anywhere near the free limit.

---

## Files in this folder

- `src/index.js` — the Worker code (paste this into Cloudflare)
- `wrangler.toml` — config (only used if you deploy via the `wrangler` CLI)
- `package.json` — local dev dependency (wrangler) — not needed for dashboard deploy
- `SETUP.md` — this file

---

Built by Perplexity Computer · for Robert Upchurch / CTI-USA
