from pulse.models import CveItem, ReleaseItem, NewsItem, FeedResult
from pulse import render


def _sample():
    cve = FeedResult(items=[
        CveItem("CVE-2026-1", "CRITICAL", "bad bug in kubelet", "https://nvd/1"),
    ])
    releases = FeedResult(items=[
        ReleaseItem("Kubernetes", "v1.33.0", "https://gh/k8s"),
    ])
    news = FeedResult(items=[
        NewsItem("Cool post", "Kubernetes Blog", "https://k8s/post"),
    ])
    return cve, releases, news


def test_report_has_sections_and_items():
    cve, releases, news = _sample()
    report, _ = render.build("2026-06-28", cve, releases, news, ["2026-06-28"])
    assert "# DevOps Pulse — 2026-06-28" in report
    assert "CVE-2026-1" in report
    assert "CRITICAL" in report
    assert "v1.33.0" in report
    assert "Cool post" in report


def test_quiet_feed_renders_honest_message():
    empty = FeedResult(items=[])
    report, _ = render.build("2026-06-28", empty, empty, empty, ["2026-06-28"])
    assert "No notable CVEs today." in report
    assert "No notable releases today." in report
    assert "No notable news today." in report


def test_failed_feed_renders_warning():
    ok = FeedResult(items=[])
    broken = FeedResult(items=[], ok=False, error="timeout")
    report, _ = render.build("2026-06-28", broken, ok, ok, ["2026-06-28"])
    assert "⚠" in report
    assert "timeout" in report


def test_readme_inlines_latest_and_lists_archive():
    cve, releases, news = _sample()
    archive = ["2026-06-26", "2026-06-27", "2026-06-28"]
    _, readme = render.build("2026-06-28", cve, releases, news, archive)
    assert "# devops-pulse" in readme
    assert "CVE-2026-1" in readme          # latest digest inlined
    assert "reports/2026-06-27.md" in readme  # archive link, reverse-chron
    # newest archived day appears before older one
    assert readme.index("2026-06-27") < readme.index("2026-06-26")
