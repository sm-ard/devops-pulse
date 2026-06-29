import feedparser

from pulse.models import NewsItem, FeedResult


def fetch(cfg, *, parse=feedparser.parse) -> FeedResult:
    items = []
    # v1: any single feed/entry failure discards all collected items (whole-fetch failure).
    try:
        for source, url in cfg.NEWS_FEEDS:
            parsed = parse(url)
            for entry in parsed.entries[: cfg.NEWS_PER_FEED]:
                items.append(NewsItem(
                    title=entry.title,
                    source=source,
                    url=entry.link,
                ))
    except Exception as e:  # noqa: BLE001 - feed isolation
        return FeedResult(items=[], ok=False, error=str(e))
    return FeedResult(items=items[: cfg.NEWS_MAX])
