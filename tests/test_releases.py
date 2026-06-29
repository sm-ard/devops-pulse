import datetime as dt

from pulse import releases
from pulse.models import FeedResult


class FakeResp:
    def __init__(self, payload, status=200):
        self._p = payload
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._p


class FakeClient:
    """Maps repo path -> FakeResp, by substring match on the URL."""
    def __init__(self, by_repo):
        self._by_repo = by_repo

    def get(self, url, params=None, timeout=None):
        for repo, resp in self._by_repo.items():
            if repo in url:
                return resp
        return FakeResp({}, status=404)


class Cfg:
    RELEASE_TOOLS = [
        ("Kubernetes", "kubernetes/kubernetes"),
        ("Helm", "helm/helm"),
    ]


NOW = dt.datetime(2026, 6, 28, 6, 0, tzinfo=dt.timezone.utc)


def _rel(tag, published):
    return FakeResp({"tag_name": tag, "html_url": f"https://gh/{tag}",
                     "published_at": published})


def test_keeps_only_releases_within_24h():
    client = FakeClient({
        "kubernetes/kubernetes": _rel("v1.33.0", "2026-06-28T01:00:00Z"),  # fresh
        "helm/helm": _rel("v3.20.0", "2026-06-01T00:00:00Z"),              # old
    })
    r = releases.fetch(Cfg, client, now=NOW)
    assert r.ok
    assert [i.tool for i in r.items] == ["Kubernetes"]
    assert r.items[0].version == "v1.33.0"


def test_missing_release_404_is_skipped_not_error():
    client = FakeClient({
        "kubernetes/kubernetes": _rel("v1.33.0", "2026-06-28T01:00:00Z"),
        # helm returns 404 (no releases)
    })
    r = releases.fetch(Cfg, client, now=NOW)
    assert r.ok
    assert len(r.items) == 1


def test_missing_published_at_is_caught_per_tool():
    client = FakeClient({
        # Kubernetes payload lacks published_at -> KeyError, isolated
        "kubernetes/kubernetes": FakeResp(
            {"tag_name": "v1.33.0", "html_url": "https://gh/v1.33.0"}),
        "helm/helm": _rel("v3.20.0", "2026-06-28T02:00:00Z"),  # fresh
    })
    r = releases.fetch(Cfg, client, now=NOW)
    assert not r.ok
    assert "Kubernetes" in r.error
    assert len(r.items) == 1  # Helm still returned


def test_one_tool_errors_other_succeeds_partial_result():
    class FlakyClient:
        def get(self, url, params=None, timeout=None):
            if "kubernetes/kubernetes" in url:
                raise RuntimeError("timeout")
            return _rel("v3.20.0", "2026-06-28T02:00:00Z")  # fresh

    r = releases.fetch(Cfg, FlakyClient(), now=NOW)
    assert not r.ok
    assert "Kubernetes" in r.error
    assert [i.tool for i in r.items] == ["Helm"]


def test_release_exactly_24h_ago_is_kept():
    client = FakeClient({
        # published exactly at NOW - 24h -> inclusive lower bound
        "kubernetes/kubernetes": _rel("v1.33.0", "2026-06-27T06:00:00Z"),
    })
    r = releases.fetch(Cfg, client, now=NOW)
    assert r.ok
    assert [i.tool for i in r.items] == ["Kubernetes"]
