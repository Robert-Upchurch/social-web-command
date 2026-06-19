/**
 * Social & Web Command — Sync Proxy Worker (v1.3.1)
 *
 * Cloudflare Worker that proxies API calls to providers whose browser-side
 * requests are blocked by CORS (Frame.io v3, HeyGen). All credentials are
 * passed through from the client per-request and never stored.
 *
 * Endpoints:
 *   GET  /                  -> health check
 *   POST /sync/frameio      body: { token } (accountId/workspaceId ignored in v3)
 *   POST /sync/heygen       body: { token, limit? }
 *   POST /discover/frameio  body: { token }
 *
 * Auth model:
 *   Optional shared HMAC secret via env.HUB_SHARED_SECRET. If set, the hub
 *   must send header `X-Hub-Secret` matching it.
 *
 * CORS:
 *   Allows origins via env.ALLOWED_ORIGIN (comma-separated supported).
 *   Defaults to https://robert-upchurch.github.io.
 *
 * Frame.io note:
 *   v3 tokens (prefix `fio-u-`) hit the legacy API at api.frame.io/v2.
 *   v3 schema is account -> team -> project. We expose teams as "workspaces"
 *   to the hub so the UI stays the same.
 */

const DEFAULT_ALLOWED_ORIGIN = "https://robert-upchurch.github.io";

function pickAllowedOrigin(request, env) {
  const raw = (env && env.ALLOWED_ORIGIN) || DEFAULT_ALLOWED_ORIGIN;
  const reqOrigin = request.headers.get("Origin") || "";
  if (raw === "*") return reqOrigin || "*";
  const list = raw.split(",").map(s => s.trim()).filter(Boolean);
  if (list.includes(reqOrigin)) return reqOrigin;
  return list[0] || DEFAULT_ALLOWED_ORIGIN;
}

function corsHeaders(request, env) {
  return {
    "Access-Control-Allow-Origin": pickAllowedOrigin(request, env),
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-Hub-Secret",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}

function jsonResponse(body, status, request, env) {
  return new Response(JSON.stringify(body), {
    status: status || 200,
    headers: { "Content-Type": "application/json", ...corsHeaders(request, env) },
  });
}

function errorResponse(message, status, request, env, extra) {
  return jsonResponse({ ok: false, error: message, ...(extra || {}) }, status || 500, request, env);
}

function checkSecret(request, env) {
  if (!env || !env.HUB_SHARED_SECRET) return true;
  const got = request.headers.get("X-Hub-Secret");
  return got && got === env.HUB_SHARED_SECRET;
}

async function readJson(request) {
  try { return await request.json(); } catch (e) { return null; }
}

// ============= Frame.io v3 =============
// v3 base: https://api.frame.io/v2
// Account -> teams -> projects. Auth: Bearer <token>.

async function syncFrameio(payload) {
  const token = payload.token;
  if (!token) throw new Error("Missing token");
  const headers = { "Authorization": "Bearer " + token, "Accept": "application/json" };

  const teamsRes = await fetch("https://api.frame.io/v2/teams", { headers });
  const teamsText = await teamsRes.text();
  if (!teamsRes.ok) throw new Error(`Frame.io ${teamsRes.status}: ${teamsText.slice(0, 300)}`);
  let teams;
  try { teams = JSON.parse(teamsText); } catch (e) { throw new Error("Frame.io returned non-JSON"); }
  if (!Array.isArray(teams)) teams = teams.data || teams.teams || [];

  // Optional filter: if hub passes workspaceId (which is a team id in our v3 mapping), use only that team.
  const filterTeamId = payload.workspaceId || null;
  const usedTeams = filterTeamId ? teams.filter(t => t.id === filterTeamId) : teams;

  const all = [];
  for (const t of usedTeams) {
    if (!t.id) continue;
    try {
      const pRes = await fetch(`https://api.frame.io/v2/teams/${encodeURIComponent(t.id)}/projects`, { headers });
      if (!pRes.ok) continue;
      const pData = await pRes.json();
      const list = Array.isArray(pData) ? pData : (pData.data || pData.projects || []);
      list.forEach(p => all.push({ project: p, team: t }));
    } catch (e) { /* per-team failure is non-fatal */ }
  }

  return all.map(({ project: p, team }) => ({
    externalId: p.id,
    title: (team.name ? team.name + " / " : "") + (p.name || "Frame.io Project"),
    url: "https://app.frame.io/projects/" + p.id,
    duration: "",
    uploaded: (p.inserted_at || p.updated_at || p.created_at || "").slice(0, 10),
    thumb: "\uD83C\uDFA5",
  }));
}

async function discoverFrameio(payload) {
  const token = payload.token;
  if (!token) throw new Error("Missing token");
  const headers = { "Authorization": "Bearer " + token, "Accept": "application/json" };
  const diag = { probed: [] };

  async function probe(path) {
    try {
      const r = await fetch("https://api.frame.io" + path, { headers });
      const t = await r.text();
      diag.probed.push({ path, status: r.status, bytes: t.length, sample: r.ok ? undefined : t.slice(0, 200) });
      let parsed = null;
      if (r.ok) { try { parsed = JSON.parse(t); } catch (_) {} }
      return { ok: r.ok, status: r.status, json: parsed };
    } catch (e) {
      diag.probed.push({ path, error: String(e) });
      return { ok: false, status: 0, json: null };
    }
  }

  const meRes = await probe("/v2/me");
  const me = meRes.json || {};
  const acctRes = await probe("/v2/accounts");
  let accountsList = [];
  if (acctRes.json) accountsList = Array.isArray(acctRes.json) ? acctRes.json : (acctRes.json.data || acctRes.json.accounts || []);

  const teamRes = await probe("/v2/teams");
  let teams = [];
  if (teamRes.json) teams = Array.isArray(teamRes.json) ? teamRes.json : (teamRes.json.data || teamRes.json.teams || []);

  // Try account-scoped teams if top-level returned nothing
  if (teams.length === 0 && accountsList.length > 0) {
    for (const a of accountsList) {
      const aid = a.id || a.account_id;
      if (!aid) continue;
      const r = await probe(`/v2/accounts/${encodeURIComponent(aid)}/teams`);
      if (r.json) {
        const arr = Array.isArray(r.json) ? r.json : (r.json.data || r.json.teams || []);
        for (const team of arr) { if (!team.account_id) team.account_id = aid; teams.push(team); }
      }
    }
  }

  // Group teams by account_id; seed with /accounts so accounts show even without teams
  const byAcct = new Map();
  for (const a of accountsList) {
    const aid = a.id || a.account_id;
    if (!aid) continue;
    byAcct.set(aid, { accountId: aid, accountName: a.display_name || a.name || "", workspaces: [] });
  }
  for (const t of teams) {
    const aid = t.account_id || (t.account && t.account.id) || (accountsList[0] && (accountsList[0].id || accountsList[0].account_id)) || "_default";
    const aname = (t.account && (t.account.display_name || t.account.name)) ||
                  (me && me.account && (me.account.display_name || me.account.name)) || "";
    if (!byAcct.has(aid)) byAcct.set(aid, { accountId: aid, accountName: aname, workspaces: [] });
    byAcct.get(aid).workspaces.push({ id: t.id, name: t.name || "" });
  }

  return {
    accounts: Array.from(byAcct.values()),
    _diag: diag,
    _me: { id: me.id || "", name: me.name || me.display_name || "", email: me.email || "" },
  };
}

// ============= HeyGen =============
// Fixes for chronic sync issues:
//   1) Paginates via next_token so we get ALL videos, not just first 50
//   2) Refreshes signed thumbnail URLs on every sync (they expire ~16 days)
//   3) Filters out failed/processing videos so the library only shows finished work
async function syncHeygen(payload) {
  const token = payload.token;
  if (!token) throw new Error("Missing token");
  const pageSize = Math.min(parseInt(payload.limit, 10) || 100, 100);
  const maxPages = Math.min(parseInt(payload.maxPages, 10) || 20, 50); // cap at 20 pages = 2000 videos
  const all = [];
  let nextToken = null;
  let pages = 0;
  do {
    let url = `https://api.heygen.com/v2/videos?limit=${pageSize}`;
    if (nextToken) url += `&token=${encodeURIComponent(nextToken)}`;
    const res = await fetch(url, {
      headers: { "X-Api-Key": token, "Accept": "application/json" },
    });
    const text = await res.text();
    if (!res.ok) throw new Error(`HeyGen ${res.status}: ${text.slice(0, 300)}`);
    let data; try { data = JSON.parse(text); } catch (e) { throw new Error("HeyGen returned non-JSON"); }
    let list = [];
    if (Array.isArray(data.data)) list = data.data;
    else if (data.data && Array.isArray(data.data.videos)) list = data.data.videos;
    else if (Array.isArray(data.videos)) list = data.videos;
    all.push(...list);
    nextToken = data.next_token || (data.data && data.data.next_token) || null;
    pages++;
    if (!data.has_more && !nextToken) break;
  } while (nextToken && pages < maxPages);

  return all
    .filter(v => !v.status || v.status === "completed") // hide failed/processing
    .map(v => ({
      externalId: v.id || v.video_id,
      title: v.title || v.video_title || "HeyGen Video",
      url: v.video_page_url || v.video_url || ("https://app.heygen.com/videos/" + (v.id || v.video_id)),
      duration: v.duration ? fmtDuration(v.duration) : "",
      uploaded: v.created_at ? new Date(v.created_at * 1000).toISOString().slice(0, 10) : "",
      // thumbnail_url is a signed URL that expires — fresh on every sync
      thumb: v.thumbnail_url || v.gif_url || "\uD83D\uDC64",
      syncedAt: Date.now(),
    }));
}

function fmtDuration(sec) {
  sec = Math.round(Number(sec) || 0);
  const m = Math.floor(sec / 60), s = sec % 60;
  return m + ":" + String(s).padStart(2, "0");
}

// ============= Router =============
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(request, env) });
    }

    if (request.method === "GET" && (url.pathname === "/" || url.pathname === "/health")) {
      return jsonResponse({
        ok: true,
        service: "social-web-command-sync",
        version: "1.4.0",
        endpoints: ["/sync/frameio", "/sync/heygen", "/discover/frameio"],
        notes: "Frame.io uses v3 API (token prefix fio-u-...). Teams are exposed to the hub as 'workspaces'.",
        time: new Date().toISOString(),
      }, 200, request, env);
    }

    if (request.method !== "POST") return errorResponse("Method not allowed", 405, request, env);
    if (!checkSecret(request, env)) return errorResponse("Unauthorized (bad or missing X-Hub-Secret header)", 401, request, env);

    const payload = await readJson(request);
    if (!payload || typeof payload !== "object") return errorResponse("Invalid JSON body", 400, request, env);

    try {
      if (url.pathname === "/sync/frameio") {
        const items = await syncFrameio(payload);
        return jsonResponse({ ok: true, provider: "frameio", items, total: items.length }, 200, request, env);
      }
      if (url.pathname === "/sync/heygen") {
        const items = await syncHeygen(payload);
        return jsonResponse({ ok: true, provider: "heygen", items, total: items.length }, 200, request, env);
      }
      if (url.pathname === "/discover/frameio") {
        const result = await discoverFrameio(payload);
        return jsonResponse({ ok: true, provider: "frameio", accounts: result.accounts, _diag: result._diag, _me: result._me }, 200, request, env);
      }
      return errorResponse("Not found", 404, request, env);
    } catch (e) {
      return errorResponse(e.message || String(e), 502, request, env);
    }
  },
};
