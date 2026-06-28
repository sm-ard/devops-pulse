from dataclasses import dataclass, field


@dataclass
class CveItem:
    cve_id: str
    severity: str  # "HIGH" | "CRITICAL"
    summary: str
    url: str


@dataclass
class ReleaseItem:
    tool: str
    version: str
    url: str


@dataclass
class NewsItem:
    title: str
    source: str
    url: str


@dataclass
class FeedResult:
    """Result of one feed fetch. `items` holds the feed's item type."""
    items: list
    ok: bool = True
    error: str | None = None
