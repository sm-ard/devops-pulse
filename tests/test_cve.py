from pulse import config, cve
from pulse.models import FeedResult


class FakeResp:
    def __init__(self, payload):
        self._p = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._p


class FakeClient:
    def __init__(self, payload=None, exc=None):
        self._payload = payload
        self._exc = exc

    def get(self, url, params=None, timeout=None):
        if self._exc:
            raise self._exc
        return FakeResp(self._payload)


def _cve_entry(cid, severity, desc):
    return {"cve": {
        "id": cid,
        "descriptions": [{"lang": "en", "value": desc}],
        "metrics": {"cvssMetricV31": [{"cvssData": {"baseSeverity": severity}}]},
    }}


def test_keeps_high_and_matching_keyword():
    payload = {"vulnerabilities": [
        _cve_entry("CVE-1", "CRITICAL", "flaw in kubernetes kubelet"),
    ]}
    r = cve.fetch(config, FakeClient(payload))
    assert r.ok
    assert len(r.items) == 1
    assert r.items[0].cve_id == "CVE-1"
    assert r.items[0].url == "https://nvd.nist.gov/vuln/detail/CVE-1"


def test_drops_low_severity():
    payload = {"vulnerabilities": [
        _cve_entry("CVE-2", "MEDIUM", "flaw in kubernetes"),
    ]}
    r = cve.fetch(config, FakeClient(payload))
    assert r.items == []


def test_drops_non_matching_keyword():
    payload = {"vulnerabilities": [
        _cve_entry("CVE-3", "HIGH", "flaw in some unrelated desktop app"),
    ]}
    r = cve.fetch(config, FakeClient(payload))
    assert r.items == []


def test_network_error_returns_not_ok():
    r = cve.fetch(config, FakeClient(exc=RuntimeError("timeout")))
    assert r.ok is False
    assert "timeout" in r.error
    assert r.items == []
