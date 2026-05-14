import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "2m", target: 20 },
    { duration: "5m", target: 80 },
    { duration: "3m", target: 80 },
    { duration: "1m", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<350", "p(99)<600"],
    http_req_failed: ["rate<0.005"],
  },
};

export default function () {
  const payload = JSON.stringify({
    customerId: `perf-${__VU}-${__ITER}`,
    phone: "13800000001",
    partySize: 2,
    petNote: "橘猫",
  });
  const res = http.post(`${__ENV.BASE_URL ?? "http://localhost:8080"}/reservations`, payload, {
    headers: { "Content-Type": "application/json", "Idempotency-Key": `${__VU}-${__ITER}` },
  });
  check(res, {
    "status is accepted": (r) => [201, 400, 409].includes(r.status),
    "response has trace id": (r) => Boolean(r.headers["X-Trace-Id"] || r.json("traceId")),
  });
  sleep(1);
}
