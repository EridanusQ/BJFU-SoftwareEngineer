import json
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

SERVICE_NAME = os.getenv("SERVICE_NAME", "reservation")
PORT = int(os.getenv("PORT", "8080"))
RESERVATIONS = {}
METRICS = {"requests": 0, "errors": 0, "duration_sum": 0.0}


def new_trace_id(headers=None):
    if headers:
        incoming = headers.get("X-Trace-Id")
        if incoming:
            return incoming
    return str(uuid.uuid4())


def log(level, message, trace_id, **fields):
    record = {
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "level": level,
        "service": SERVICE_NAME,
        "traceId": trace_id,
        "message": message,
        **fields,
    }
    print(json.dumps(record, ensure_ascii=False), flush=True)


def create_reservation(payload):
    required = ["memberId", "storeId", "tableId", "timeSlot", "partySize"]
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"missing fields: {', '.join(missing)}")
    reservation_id = f"rsv_{uuid.uuid4().hex[:10]}"
    reservation = {
        "id": reservation_id,
        "memberId": payload["memberId"],
        "storeId": payload["storeId"],
        "tableId": payload["tableId"],
        "timeSlot": payload["timeSlot"],
        "partySize": int(payload["partySize"]),
        "specialRequest": payload.get("specialRequest", ""),
        "status": "CONFIRMED",
    }
    RESERVATIONS[reservation_id] = reservation
    return reservation


class Handler(BaseHTTPRequestHandler):
    server_version = "NekoCafeReservation/0.1.0"

    def _send_json(self, status, body, trace_id):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Trace-Id", trace_id)
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _record(self, started, status):
        METRICS["requests"] += 1
        if status >= 500:
            METRICS["errors"] += 1
        METRICS["duration_sum"] += time.time() - started

    def do_GET(self):
        started = time.time()
        trace_id = new_trace_id(self.headers)
        parsed = urlparse(self.path)
        status = 200
        try:
            if parsed.path == "/healthz":
                self._send_json(200, {"status": "ok", "service": SERVICE_NAME}, trace_id)
            elif parsed.path == "/readyz":
                self._send_json(200, {"status": "ready"}, trace_id)
            elif parsed.path == "/reservations":
                self._send_json(200, {"items": list(RESERVATIONS.values())}, trace_id)
            elif parsed.path.startswith("/reservations/"):
                rid = parsed.path.rsplit("/", 1)[-1]
                item = RESERVATIONS.get(rid)
                if not item:
                    status = 404
                    self._send_json(404, {"error": "NOT_FOUND", "traceId": trace_id}, trace_id)
                else:
                    self._send_json(200, item, trace_id)
            elif parsed.path == "/metrics":
                body = (
                    "# HELP nekocafe_http_requests_total Total HTTP requests\n"
                    "# TYPE nekocafe_http_requests_total counter\n"
                    f'nekocafe_http_requests_total{{service="{SERVICE_NAME}"}} {METRICS["requests"]}\n'
                    "# HELP nekocafe_http_request_errors_total Total HTTP 5xx errors\n"
                    "# TYPE nekocafe_http_request_errors_total counter\n"
                    f'nekocafe_http_request_errors_total{{service="{SERVICE_NAME}"}} {METRICS["errors"]}\n'
                    "# HELP nekocafe_http_request_duration_seconds_sum Request duration sum\n"
                    "# TYPE nekocafe_http_request_duration_seconds_sum counter\n"
                    f'nekocafe_http_request_duration_seconds_sum{{service="{SERVICE_NAME}"}} {METRICS["duration_sum"]:.6f}\n'
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; version=0.0.4")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                status = 404
                self._send_json(404, {"error": "NOT_FOUND", "traceId": trace_id}, trace_id)
        except Exception as exc:  # keep service resilient for PoC
            status = 500
            log("error", "request failed", trace_id, error=str(exc), path=self.path)
            self._send_json(500, {"error": "INTERNAL_ERROR", "traceId": trace_id}, trace_id)
        finally:
            self._record(started, status)
            log("info", "request completed", trace_id, method="GET", path=parsed.path, status=status, latency_ms=round((time.time() - started) * 1000, 2))

    def do_POST(self):
        started = time.time()
        trace_id = new_trace_id(self.headers)
        parsed = urlparse(self.path)
        status = 201
        try:
            if parsed.path == "/reservations":
                reservation = create_reservation(self._read_json())
                self._send_json(201, {**reservation, "traceId": trace_id}, trace_id)
            else:
                status = 404
                self._send_json(404, {"error": "NOT_FOUND", "traceId": trace_id}, trace_id)
        except ValueError as exc:
            status = 400
            self._send_json(400, {"error": "VALIDATION_ERROR", "message": str(exc), "traceId": trace_id}, trace_id)
        except Exception as exc:
            status = 500
            log("error", "request failed", trace_id, error=str(exc), path=self.path)
            self._send_json(500, {"error": "INTERNAL_ERROR", "traceId": trace_id}, trace_id)
        finally:
            self._record(started, status)
            log("info", "request completed", trace_id, method="POST", path=parsed.path, status=status, latency_ms=round((time.time() - started) * 1000, 2))

    def log_message(self, format, *args):
        return


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(json.dumps({"service": SERVICE_NAME, "event": "startup", "port": PORT}), flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
