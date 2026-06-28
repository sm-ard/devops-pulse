import datetime as dt

from pulse.models import ReleaseItem, FeedResult

_API = "https://api.github.com/repos/{repo}/releases/latest"


def _parse_ts(value: str) -> dt.datetime:
    # GitHub timestamps end with 'Z'
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def fetch(cfg, client, *, now=None) -> FeedResult:
    now = now or dt.datetime.now(dt.timezone.utc)
    cutoff = now - dt.timedelta(days=1)
    items, errors = [], []

    for name, repo in cfg.RELEASE_TOOLS:
        try:
            resp = client.get(_API.format(repo=repo), timeout=30)
            if getattr(resp, "status_code", 200) == 404:
                continue  # no releases yet — not an error
            resp.raise_for_status()
            data = resp.json()
            published = _parse_ts(data["published_at"])
            if published >= cutoff:
                items.append(ReleaseItem(
                    tool=name,
                    version=data["tag_name"],
                    url=data["html_url"],
                ))
        except Exception as e:  # noqa: BLE001 - isolate per-tool failures
            errors.append(f"{name}: {e}")

    if errors and not items:
        return FeedResult(items=[], ok=False, error="; ".join(errors))
    return FeedResult(items=items, ok=not errors,
                      error="; ".join(errors) or None)
