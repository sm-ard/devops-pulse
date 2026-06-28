from pulse.models import CveItem, ReleaseItem, NewsItem, FeedResult


def test_feedresult_defaults_to_ok():
    r = FeedResult(items=[])
    assert r.ok is True
    assert r.error is None
    assert r.items == []


def test_feedresult_can_carry_error():
    r = FeedResult(items=[], ok=False, error="boom")
    assert r.ok is False
    assert r.error == "boom"


def test_item_types_hold_fields():
    cve = CveItem(cve_id="CVE-2026-1", severity="HIGH", summary="x", url="u")
    rel = ReleaseItem(tool="kubernetes", version="v1.33.0", url="u")
    news = NewsItem(title="t", source="Kubernetes Blog", url="u")
    assert cve.severity == "HIGH"
    assert rel.version == "v1.33.0"
    assert news.source == "Kubernetes Blog"
