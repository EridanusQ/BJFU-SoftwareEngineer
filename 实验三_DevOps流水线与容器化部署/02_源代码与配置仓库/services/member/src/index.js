const http = require("node:http");
const crypto = require("node:crypto");

const serviceName = process.env.SERVICE_NAME || "member";
const port = Number(process.env.PORT || 8080);
const metrics = { requests: 0, errors: 0, durationSum: 0 };

function traceId(req) {
  return req.headers["x-trace-id"] || crypto.randomUUID();
}

function log(level, message, tid, fields = {}) {
  console.log(JSON.stringify({
    time: new Date().toISOString(),
    level,
    service: serviceName,
    traceId: tid,
    message,
    ...fields,
  }));
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = "";
    req.on("data", chunk => { data += chunk; });
    req.on("end", () => {
      if (!data) return resolve({});
      try { resolve(JSON.parse(data)); } catch (error) { reject(error); }
    });
  });
}

function sendJson(res, status, body, tid) {
  const data = Buffer.from(JSON.stringify(body));
  res.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "content-length": data.length,
    "x-trace-id": tid,
  });
  res.end(data);
}

function memberProfile() {
  return {
    id: "m_1001",
    nickname: "NekoFan",
    phoneMasked: "138****2703",
    level: "Gold",
    points: 1280,
    preferenceTags: ["安静区", "布偶猫", "低糖甜品"],
  };
}

function normalizeConsent(payload) {
  if (!payload.type) throw new Error("type is required");
  return {
    type: payload.type,
    granted: Boolean(payload.granted),
    updatedAt: new Date().toISOString(),
  };
}

function createServer() {
  return http.createServer(async (req, res) => {
    const started = Date.now();
    const tid = traceId(req);
    const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
    let status = 200;
    try {
      if (req.method === "GET" && url.pathname === "/healthz") {
        sendJson(res, 200, { status: "ok", service: serviceName }, tid);
      } else if (req.method === "GET" && url.pathname === "/readyz") {
        sendJson(res, 200, { status: "ready" }, tid);
      } else if (req.method === "GET" && url.pathname === "/members/me") {
        sendJson(res, 200, { ...memberProfile(), traceId: tid }, tid);
      } else if (req.method === "PUT" && url.pathname === "/members/me/consents") {
        const consent = normalizeConsent(await readBody(req));
        sendJson(res, 200, { ...consent, traceId: tid }, tid);
      } else if (req.method === "GET" && url.pathname === "/metrics") {
        const body = [
          "# HELP nekocafe_http_requests_total Total HTTP requests",
          "# TYPE nekocafe_http_requests_total counter",
          `nekocafe_http_requests_total{service="${serviceName}"} ${metrics.requests}`,
          "# HELP nekocafe_http_request_errors_total Total HTTP 5xx errors",
          "# TYPE nekocafe_http_request_errors_total counter",
          `nekocafe_http_request_errors_total{service="${serviceName}"} ${metrics.errors}`,
          "# HELP nekocafe_http_request_duration_seconds_sum Request duration sum",
          "# TYPE nekocafe_http_request_duration_seconds_sum counter",
          `nekocafe_http_request_duration_seconds_sum{service="${serviceName}"} ${(metrics.durationSum / 1000).toFixed(6)}`,
          "",
        ].join("\n");
        res.writeHead(200, { "content-type": "text/plain; version=0.0.4" });
        res.end(body);
      } else {
        status = 404;
        sendJson(res, 404, { error: "NOT_FOUND", traceId: tid }, tid);
      }
    } catch (error) {
      status = 400;
      log("error", "request failed", tid, { error: error.message, path: url.pathname });
      sendJson(res, 400, { error: "BAD_REQUEST", message: error.message, traceId: tid }, tid);
    } finally {
      metrics.requests += 1;
      if (status >= 500) metrics.errors += 1;
      metrics.durationSum += Date.now() - started;
      log("info", "request completed", tid, { method: req.method, path: url.pathname, status, latency_ms: Date.now() - started });
    }
  });
}

if (require.main === module) {
  createServer().listen(port, "0.0.0.0", () => {
    console.log(JSON.stringify({ service: serviceName, event: "startup", port }));
  });
}

module.exports = { createServer, memberProfile, normalizeConsent };
