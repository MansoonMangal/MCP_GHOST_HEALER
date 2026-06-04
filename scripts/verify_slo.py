"""
Simple Render SLO smoke verifier.

Checks:
- health endpoint reachable
- p95 latency under threshold for repeated /health calls
- optional heal call success
"""

from __future__ import annotations

import argparse
import statistics
import time
from typing import Any

import httpx


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    k = int(round((len(ordered) - 1) * p))
    return ordered[k]


def probe_health(client: httpx.Client, base_url: str, samples: int) -> list[float]:
    latencies: list[float] = []
    for _ in range(samples):
        start = time.perf_counter()
        response = client.get(f"{base_url}/health/ready")
        elapsed_ms = (time.perf_counter() - start) * 1000
        if response.status_code != 200:
            raise RuntimeError(f"/health/ready returned {response.status_code}")
        data = response.json()
        if not data.get("ready", False):
            raise RuntimeError("Service is not ready")
        latencies.append(elapsed_ms)
    return latencies


def probe_heal(client: httpx.Client, base_url: str) -> dict[str, Any]:
    dom = '<html><body><button id="ok">OK</button></body></html>'
    payload = {
        "selector": "#ok",
        "action": "click",
        "dom_snapshot": dom,
    }
    response = client.post(f"{base_url}/api/heal-locator", json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"/api/heal-locator returned {response.status_code}")
    body = response.json()
    if "confidence" not in body or "decision" not in body:
        raise RuntimeError("Heal response missing required fields")
    return body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--max-p95-ms", type=float, default=500.0)
    parser.add_argument("--api-key", default="")
    parser.add_argument("--skip-heal", action="store_true")
    args = parser.parse_args()

    headers = {}
    if args.api_key:
        headers["X-API-Key"] = args.api_key

    with httpx.Client(timeout=20.0, headers=headers) as client:
        latencies = probe_health(client, args.base_url.rstrip("/"), args.samples)
        p95 = percentile(latencies, 0.95)
        avg = statistics.mean(latencies)
        print(f"[slo] health avg={avg:.2f}ms p95={p95:.2f}ms samples={len(latencies)}")
        if p95 > args.max_p95_ms:
            raise RuntimeError(
                f"SLO violation: p95 {p95:.2f}ms > max {args.max_p95_ms:.2f}ms"
            )

        if not args.skip_heal:
            heal_data = probe_heal(client, args.base_url.rstrip("/"))
            print(
                "[slo] heal decision="
                f"{heal_data.get('decision')} confidence={heal_data.get('confidence')}"
            )

    print("[slo] checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
