from pulse import config


def test_severity_threshold():
    assert config.SEVERITY_MIN == {"HIGH", "CRITICAL"}


def test_keyword_and_tool_lists_nonempty():
    assert len(config.CVE_KEYWORDS) >= 5
    assert all(k == k.lower() for k in config.CVE_KEYWORDS)
    assert len(config.RELEASE_TOOLS) >= 5
    # each tool is (display_name, "owner/repo")
    assert all("/" in repo for _, repo in config.RELEASE_TOOLS)


def test_news_feeds_have_source_and_url():
    assert len(config.NEWS_FEEDS) >= 2
    assert all(url.startswith("http") for _, url in config.NEWS_FEEDS)
    assert config.NEWS_PER_FEED >= 1
    assert config.NEWS_MAX >= config.NEWS_PER_FEED
