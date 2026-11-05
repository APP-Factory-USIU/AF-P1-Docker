"""Run against a live, otherwise idle demo: python3 tests/smoke.py."""
import urllib.request

BASE = "http://127.0.0.1:8000"


def value():
    with urllib.request.urlopen(BASE, timeout=5) as response:
        html = response.read().decode()
    return int(html.split('aria-label="Counter value">')[1].split("<")[0])


with urllib.request.urlopen(BASE + "/health", timeout=5) as response:
    assert response.status == 200
before = value()
with urllib.request.urlopen(
    urllib.request.Request(BASE + "/count", data=b"", method="POST"), timeout=5
) as response:
    assert response.status == 200
assert value() == before + 1, "POST should increase the stored counter once"
print("PASS: health, HTML, POST, redirect, and Redis counter")
