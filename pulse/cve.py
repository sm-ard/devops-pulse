import datetime as dt

from pulse.models import CveItem, FeedResult

NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
_MAX_SUMMARY = 200


def _english_desc(cve: dict) -> str:
    for d in cve.get("descriptions", []):
        if d.get("lang") == "en":
            return d.get("value", "")
    return ""


def _severity(cve: dict) -> str:
    metrics = cve.get("metrics", {})
    for key in ("cvssMetricV31", "cvssMetricV30"):
        entries = metrics.get(key) or []
        if entries:
            return entries[0].get("cvssData", {}).get("baseSeverity", "").upper()
    return ""


def _matches(desc: str, keywords) -> bool:
    low = desc.lower()
    return any(k in low for k in keywords)


def _truncate(text: str) -> str:
    return text if len(text) <= _MAX_SUMMARY else text[: _MAX_SUMMARY - 1] + "…"


def fetch(cfg, client) -> FeedResult:
    end = dt.datetime.now(dt.timezone.utc)
    start = end - dt.timedelta(days=1)
    params = {
        "pubStartDate": start.strftime("%Y-%m-%dT%H:%M:%S.000") + "Z",
        "pubEndDate": end.strftime("%Y-%m-%dT%H:%M:%S.000") + "Z",
        "resultsPerPage": 2000,
    }
    try:
        resp = client.get(NVD_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:  # noqa: BLE001 - feed isolation by design
        return FeedResult(items=[], ok=False, error=str(e))

    items = []
    for entry in data.get("vulnerabilities", []):
        c = entry.get("cve") or {}
        sev = _severity(c)
        if sev not in cfg.SEVERITY_MIN:
            continue
        desc = _english_desc(c)
        if not _matches(desc, cfg.CVE_KEYWORDS):
            continue
        cid = c.get("id", "")
        items.append(CveItem(
            cve_id=cid,
            severity=sev,
            summary=_truncate(desc),
            url=f"https://nvd.nist.gov/vuln/detail/{cid}",
        ))
    return FeedResult(items=items)
