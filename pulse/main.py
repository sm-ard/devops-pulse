import datetime as dt
import os
from pathlib import Path

import feedparser
import httpx

from pulse import config, cve, releases, news, render


def _existing_report_dates(reports_dir: Path) -> list[str]:
    if not reports_dir.exists():
        return []
    return [p.stem for p in reports_dir.glob("*.md")]


def run(repo_root: Path, *, client, news_parse, now=None) -> None:
    now = now or dt.datetime.now(dt.timezone.utc)
    date = now.strftime("%Y-%m-%d")

    cve_res = cve.fetch(config, client)
    rel_res = releases.fetch(config, client, now=now)
    news_res = news.fetch(config, parse=news_parse)

    reports_dir = repo_root / "reports"
    archive = _existing_report_dates(reports_dir) + [date]
    report_md, readme_md = render.build(date, cve_res, rel_res, news_res, archive)

    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / f"{date}.md").write_text(report_md, encoding="utf-8")
    (repo_root / "README.md").write_text(readme_md, encoding="utf-8")


def main() -> None:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with httpx.Client(headers=headers) as client:
        run(Path.cwd(), client=client, news_parse=feedparser.parse)


if __name__ == "__main__":
    main()
