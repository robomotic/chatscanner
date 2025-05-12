import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from chatscanner.cli import basic_scan

MOCK_HTML_CASES = [
    # 1. HTML Element Search
    ("<div id='chat-widget'></div>", True),
    ("<span class='livechat'></span>", True),
    ("<div name='supportBot'></div>", True),
    # 2. Script Tag Inspection
    ("<script src='https://cdn.intercom.io/widget.js'></script>", True),
    ("<script src='https://example.com/other.js'></script>", False),
    # 3. Text Pattern Matching
    ("<div>Chat with us now!</div>", True),
    ("<div>Welcome to our website</div>", False),
    # 4. Iframe Detection
    ("<iframe src='https://drift.com/chat'></iframe>", True),
    ("<iframe src='https://example.com/frame'></iframe>", False),
]

class MockResponse:
    def __init__(self, text):
        self.text = text


def mock_requests_get(url, timeout=10):
    # Use the URL as an index to select the mock HTML
    idx = int(url.split("_")[-1])
    return MockResponse(MOCK_HTML_CASES[idx][0])


def test_basic_scan(monkeypatch):
    for idx, (html, expected) in enumerate(MOCK_HTML_CASES):
        monkeypatch.setattr("chatscanner.cli.requests.get", lambda url, timeout=10: MockResponse(html))
        result = basic_scan(f"http://mock_{idx}")
        found = bool(result['chatbot_indicators'])
        assert found == expected, f"Failed for case {idx}: {html}"


MOCK_LANDING_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Welcome to Example</title>
    <script src="https://cdn.intercom.io/widget.js"></script>
    <script src="/static/js/main.js"></script>
</head>
<body>
    <header>
        <h1>Welcome to Example</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
        </nav>
    </header>
    <main>
        <div id="content">
            <p>We offer the best services for your needs.</p>
            <div id="chat-widget" class="livechat">Need help? Chat with us!</div>
            <iframe src="https://drift.com/chat"></iframe>
        </div>
    </main>
    <footer>
        <p>Contact us at support@example.com</p>
    </footer>
</body>
</html>
'''

def test_basic_scan_landing_page(monkeypatch):
    monkeypatch.setattr("chatscanner.cli.requests.get", lambda url, timeout=10: MockResponse(MOCK_LANDING_HTML))
    result = basic_scan("http://mock_landing")
    found = result['chatbot_indicators']
    assert any('element:' in f for f in found)
    assert any('script:' in f for f in found)
    assert any('iframe:' in f for f in found)
    assert any('text:' in f for f in found)


def test_medium_scan(monkeypatch):
    # Mock Playwright and BeautifulSoup for medium_scan
    import types
    from chatscanner import cli as chatscanner_cli

    class MockPage:
        def goto(self, url, timeout=20000):
            pass
        def wait_for_load_state(self, state, timeout=20000):
            pass
        def content(self):
            return MOCK_LANDING_HTML
    class MockBrowser:
        def new_page(self):
            return MockPage()
        def close(self):
            pass
    class MockPlaywright:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        @property
        def chromium(self):
            class Chromium:
                @staticmethod
                def launch(headless=True):
                    return MockBrowser()
            return Chromium()
    monkeypatch.setattr("playwright.sync_api.sync_playwright", lambda: MockPlaywright())
    result = chatscanner_cli.medium_scan("http://mock_landing")
    found = result['chatbot_indicators']
    assert any('element:' in f for f in found)
    assert any('script:' in f for f in found)
    assert any('iframe:' in f for f in found)
    assert any('text:' in f for f in found)
