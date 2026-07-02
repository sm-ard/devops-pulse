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


def run(repo_root: Path, *, nvd_client, gh_client, news_parse, now=None) -> None:
    now = now or dt.datetime.now(dt.timezone.utc)
    date = now.strftime("%Y-%m-%d")

    cve_res = cve.fetch(config, nvd_client)
    rel_res = releases.fetch(config, gh_client, now=now)
    news_res = news.fetch(config, parse=news_parse)

    reports_dir = repo_root / "reports"
    archive = _existing_report_dates(reports_dir) + [date]
    report_md, readme_md = render.build(date, cve_res, rel_res, news_res, archive)

    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / f"{date}.md").write_text(report_md, encoding="utf-8")
    (repo_root / "README.md").write_text(readme_md, encoding="utf-8")


def main() -> None:
    nvd_headers = {"Accept": "application/json", "User-Agent": "devops-pulse/0.1"}
    nvd_key = os.environ.get("NVD_API_KEY")
    if nvd_key:
        nvd_headers["apiKey"] = nvd_key
    gh_headers = {"Accept": "application/vnd.github+json", "User-Agent": "devops-pulse/0.1"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        gh_headers["Authorization"] = f"Bearer {token}"
    with httpx.Client(headers=nvd_headers) as nvd_client, \
         httpx.Client(headers=gh_headers) as gh_client:
        run(Path.cwd(), nvd_client=nvd_client, gh_client=gh_client,
            news_parse=feedparser.parse)


if __name__ == "__main__":
    main()
