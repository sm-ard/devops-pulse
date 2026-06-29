from types import SimpleNamespace

from pulse import news
from pulse.models import FeedResult


class Cfg:
    NEWS_FEEDS = [
        ("Kubernetes Blog", "https://k8s/feed"),
        ("AWS What's New", "https://aws/feed"),
    ]
    NEWS_PER_FEED = 2
    NEWS_MAX = 3


def _feed(*titles):
    return SimpleNamespace(
        entries=[SimpleNamespace(title=t, link=f"https://x/{t}") for t in titles]
    )


def test_takes_per_feed_limit_and_overall_cap():
    feeds = {
        "https://k8s/feed": _feed("k1", "k2", "k3"),   # per-feed cap -> k1,k2
        "https://aws/feed": _feed("a1", "a2"),         # per-feed cap -> a1,a2
    }
    r = news.fetch(Cfg, parse=lambda url: feeds[url])
    assert r.ok
    # 2 + 2 = 4 collected, overall cap 3
    assert len(r.items) == 3
    assert r.items[0].title == "k1"
    assert r.items[0].source == "Kubernetes Blog"


def test_parse_error_returns_not_ok():
    def boom(url):
        raise RuntimeError("rss down")

    r = news.fetch(Cfg, parse=boom)
    assert r.ok is False
    assert "rss down" in r.error
    assert r.items == []
