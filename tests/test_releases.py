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
