// k6 load test - run with: k6 run k6-load.js
import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 10,
  duration: "30s",
};

export default function () {
  const res = http.get("http://localhost:3000/api/health");
  check(res, { "health ok": (r) => r.status === 200 });
  sleep(1);
}
