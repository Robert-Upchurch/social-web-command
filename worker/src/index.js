/**
 * Social & Web Command — Sync Proxy Worker
 *
 * Cloudflare Worker that proxies API calls to providers whose browser-side
 * requests are blocked by CORS (Frame.io, HeyGen). All credentials are passed
 * through from the client per-request and never stored.
 *
 * Endpoints:
 *   GET  /            -> health check
 *   POST /sync/frameio  body: { token, accountId, workspaceId }
 *   POST /sync/heygen   body: { token, limit? }
 *
 * Auth model:
 *   Optional shared HMAC secret via env.HUB_SHARED_SECRET. If set, the hub
 *   must send header `X-Hub-Secret` matching it. This prevents random
 *   internet traffic from using your Worker as a free proxy.
 *
 * CORS:
 *   Allows the GitHub Pages origin by default. Override via env.ALLOWED_ORIGIN.
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
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders(request, env),
    },
  });
}

function errorResponse(message, status, request, env, extra) {
  return jsonResponse({ ok: false, error: message, ...(extra || {}) }, status || 500, request, env);
}

function checkSecret(request, env) {
  if (!env || !env.HUB_SHARED_SECRET) return true; // no secret configured -> open (for local dev)
  const got = request.headers.get("X-Hub-Secret");
  return got && got === env.HUB_SHARED_SECRET;
}

async function readJson(request) {
  try {
    return await request.json();
  } catch (e) {
    return null;
  }
}

// ===== Frame.io v4 =====
async function syncFrameio(payload) {
  const token = payload.token;
  const accountId = payload.accountId;
  const workspaceId = payload.workspaceId;
  if (!token) throw new Error("Missing token");
  if (!accountId) throw new Error("Missing accountId");
  if (!workspaceId) throw new Error("Missing workspaceId");

  const url = `https://api.frame.io/v4/accounts/${encodeURIComponent(accountId)}/workspaces/${encodeURIComponent(workspaceId)}/projects`;
  const res = await fetch(url, {
    headers: {
      "Authorization": "Bearer " + token,
      "Accept": "application/json",
    },
  });
  const text = await res.text();
  if (!res.ok) {
    throw new Error(`Frame.io ${res.status}: ${text.slice(0, 300)}`);
  }
  let data;
  try { data = JSON.parse(text); } catch (e) { throw new Error("Frame.io returned non-JSON"); }
  const list = data.data || data.projects || [];
  return list.map(p => ({
    externalId: p.id,
    title: p.name || "Frame.io Project",
    url: "https://next.frame.io/project/" + p.id,
    duration: "",
    uploaded: (p.inserted_at || p.created_at || "").slice(0, 10),
    thumb: "\uD83C\uDFA5",
  }));
}

// ===== HeyGen =====
async function syncHeygen(payload) {
  const token = payload.token;
  if (!token) throw new Error("Missing token");
  const limit = Math.min(parseInt(payload.limit, 10) || 50, 100);
  const url = `https://api.heygen.com/v1/video.list?limit=${limit}`;
  const res = await fetch(url, {
    headers: {
      "X-Api-Key": token,
      "Accept": "application/json",
    },
  });
  const text = await res.text();
  if (!res.ok) {
    throw new Error(`HeyGen ${res.status}: ${text.slice(0, 300)}`);
  }
  let data;
  try { data = JSON.parse(text); } catch (e) { throw new Error("HeyGen returned non-JSON"); }
  const list = (data.data && data.data.videos) || data.videos || [];
  return list.map(v => ({
    externalId: v.video_id || v.id,
    title: v.video_title || v.title || "HeyGen Video",
    url: v.video_url || ("https://app.heygen.com/videos/" + (v.video_id || v.id)),
    duration: v.duration ? fmtDuration(v.duration) : "",
    uploaded: v.created_at ? new Date(v.created_at * 1000).toISOString().slice(0, 10) : "",
    thumb: "\uD83D\uDC64",
  }));
}

function fmtDuration(sec) {
  sec = Math.round(Number(sec) || 0);
  const m = Math.floor(sec / 60), s = sec % 60;
  return m + ":" + String(s).padStart(2, "0");
}

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
        version: "1.0.0",
        endpoints: ["/sync/frameio", "/sync/heygen"],
        time: new Date().toISOString(),
      }, 200, request, env);
    }

    if (request.method !== "POST") {
      return errorResponse("Method not allowed", 405, request, env);
    }
    if (!checkSecret(request, env)) {
      return errorResponse("Unauthorized (bad or missing X-Hub-Secret header)", 401, request, env);
    }

    const payload = await readJson(request);
    if (!payload || typeof payload !== "object") {
      return errorResponse("Invalid JSON body", 400, request, env);
    }

    try {
      if (url.pathname === "/sync/frameio") {
        const items = await syncFrameio(payload);
        return jsonResponse({ ok: true, provider: "frameio", items, total: items.length }, 200, request, env);
      }
      if (url.pathname === "/sync/heygen") {
        const items = await syncHeygen(payload);
        return jsonResponse({ ok: true, provider: "heygen", items, total: items.length }, 200, request, env);
      }
      return errorResponse("Not found", 404, request, env);
    } catch (e) {
      return errorResponse(e.message || String(e), 502, request, env);
    }
  },
};
