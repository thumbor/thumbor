#!/usr/bin/env bash
# NSXBet Thumbor API smoke test.
# Requires: make run-bg (stack up). Exits non-zero on first failure.
set -euo pipefail

BASE="${THUMBOR_BASE:-http://localhost:8888}"
METRICS="${STATSD_EXPORTER_BASE:-http://localhost:9102}"

# Fixtures served by the local file_loader (docker/fixtures mounted at /fixtures).
GIF_SRC="test.gif"
JPG_SRC="test.jpg"

fail() { echo "FAIL: $1" >&2; exit 1; }

echo "== 1. healthcheck"
curl -fsS "$BASE/healthcheck" | grep -q "WORKING" || fail "healthcheck did not return WORKING"
echo "ok"

echo "== 2. image happy path (resize JPEG)"
CT=$(curl -fsS -o /dev/null -w '%{content_type}' "$BASE/unsafe/300x200/$JPG_SRC")
echo "content-type: $CT"
[[ "$CT" == image/* ]] || fail "expected image/* content-type, got $CT"

echo "== 3. GIF -> animated WebP (filters:format(webp))"
CT=$(curl -fsS -H "Accept: image/webp" -o /dev/null -w '%{content_type}' "$BASE/unsafe/100x100/filters:format(webp)/$GIF_SRC")
echo "content-type: $CT"
[[ "$CT" == "image/webp" ]] || fail "expected image/webp, got $CT"

echo "== 4. GIF -> H264 MP4 (Accept: video/*)"
CT=$(curl -fsS -H "Accept: video/*" -o /dev/null -w '%{content_type}' "$BASE/unsafe/100x100/$GIF_SRC")
echo "content-type: $CT"
[[ "$CT" == "video/mp4" ]] || fail "expected video/mp4, got $CT"

echo "== 5. missing source -> 4xx"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/unsafe/100x100/not-there.gif")
echo "status: $CODE"
[[ "$CODE" =~ ^4 ]] || fail "expected 4xx for missing source, got $CODE"

echo "== 6. statsd metrics exposed via statsd_exporter"
curl -fsS "$METRICS/metrics" | grep -q "^statsd_" || fail "no statsd_ series in exporter metrics"
curl -fsS "$METRICS/metrics" | grep -q "thumbor" || fail "no thumbor statsd series found"
echo "ok"

echo "ALL PASSED"
