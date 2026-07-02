import datetime as dt
from pathlib import Path
from types import SimpleNamespace

from pulse import main


class FakeResp:
    def __init__(self, payload):
        self._p = payload
        self.status_code = 200

    def raise_for_status(self):
        pass

    def json(self):
        return self._p


class FakeClient:
    """Returns NVD-shaped payload for NVD url, release payload otherwise."""
    def get(self, url, params=None, timeout=None):
        if "nvd.nist.gov" in url:
            return FakeResp({"vulnerabilities": [{"cve": {
                "id": "CVE-9",
                "descriptions": [{"lang": "en", "value": "kubernetes bug"}],
                "metrics": {"cvssMetricV31": [{"cvssData": {"baseSeverity": "HIGH"}}]},
            }}]})
        # any GitHub release lookup -> old release (filtered out), keeps test simple
        return FakeResp({"tag_name": "v0", "html_url": "u",
                         "published_at": "2000-01-01T00:00:00Z"})


def _empty_rss(url):
    return SimpleNamespace(entries=[])


def test_run_writes_report_and_readme(tmp_path):
    now = dt.datetime(2026, 6, 28, 6, 0, tzinfo=dt.timezone.utc)
    fake = FakeClient()
    main.run(tmp_path, nvd_client=fake, gh_client=fake,
             news_parse=_empty_rss, now=now)

    report = tmp_path / "reports" / "2026-06-28.md"
    readme = tmp_path / "README.md"
    assert report.exists()
    assert "CVE-9" in report.read_text()
    assert readme.exists()
    assert "CVE-9" in readme.read_text()           # latest inlined
    assert "reports/2026-06-28.md" in readme.read_text()  # archive index


def test_run_archive_index_includes_prior_reports(tmp_path):
    (tmp_path / "reports").mkdir()
    (tmp_path / "reports" / "2026-06-27.md").write_text("old")
    now = dt.datetime(2026, 6, 28, 6, 0, tzinfo=dt.timezone.utc)
    fake = FakeClient()
    main.run(tmp_path, nvd_client=fake, gh_client=fake,
             news_parse=_empty_rss, now=now)
    readme = (tmp_path / "README.md").read_text()
    assert "reports/2026-06-27.md" in readme
    assert "reports/2026-06-28.md" in readme


class FailingClient:
    def get(self, url, params=None, timeout=None):
        if "nvd.nist.gov" in url:
            raise RuntimeError("nvd down")
        return FakeResp({"tag_name": "v0", "html_url": "u",
                         "published_at": "2000-01-01T00:00:00Z"})


def test_run_with_failed_feed_still_writes(tmp_path):
    now = dt.datetime(2026, 6, 28, 6, 0, tzinfo=dt.timezone.utc)
    failing = FailingClient()
    main.run(tmp_path, nvd_client=failing, gh_client=failing,
             news_parse=_empty_rss, now=now)
    report = tmp_path / "reports" / "2026-06-28.md"
    assert report.exists()
    assert "Feed unavailable" in report.read_text()
