import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import pytest
from chatscanner.cli import basic_scan, medium_scan

LIVE_CHAT_URLS = [
    "https://www.intercom.com/",
    "https://www.drift.com/",
    "https://www.tawk.to/",
    "https://www.zendesk.com/",
    "https://www.livechat.com/",
    "https://www.hubspot.com/",
    #"https://freshchat.com/", -> no chatbot this is broken
    "https://www.chatwoot.com/",
    "https://crisp.chat/",
    "https://www.olark.com/",
]

NON_CHAT_URLS = [
    "https://www.thetimes.com/",
    "https://www.google.com/"
]

@pytest.mark.parametrize("url", LIVE_CHAT_URLS)
def test_basic_scan_live(url):
    result = basic_scan(url)
    assert 'chatbot_indicators' in result
    assert isinstance(result['chatbot_indicators'], list)
    assert len(result['chatbot_indicators'])>0

@pytest.mark.parametrize("url", NON_CHAT_URLS)
def test_basic_scan_neg_live(url):
    result = basic_scan(url)
    assert 'chatbot_indicators' in result
    assert isinstance(result['chatbot_indicators'], list)
    assert len(result['chatbot_indicators'])==0

@pytest.mark.parametrize("url", LIVE_CHAT_URLS)
def test_medium_scan_live(url):
    result = medium_scan(url)
    assert 'chatbot_indicators' in result or 'error' in result
    # If playwright is not installed, skip
    if 'error' in result and 'playwright not installed' in result['error']:
        pytest.skip("Playwright not installed")
    assert isinstance(result['chatbot_indicators'], list)
