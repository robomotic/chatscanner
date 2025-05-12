import click
import requests
from bs4 import BeautifulSoup
import re
import json
import asyncio

CHATBOT_KEYWORDS = [
    'chat', 'bot', 'messenger', 'intercom', 'drift', 'livechat', 'tawk', 'zendesk', 'olark', 'help', 'support', 'talkto', 'chatwoot', 'freshchat', 'snapengage', 'liveagent', 'smartsupp', 'userlike', 'purechat', 'clickdesk', 'crisp', 'comm100', 'chatra', 'gubagoo', 'hubspot', 'whoson', 'zoho', 'conversocial', 'boldchat', 'liveperson', 'kayako', 'acquire', 'genesys', 'salesforce', 'ibm watson', 'google dialogflow', 'meya', 'snatchbot', 'pandorabots', 'botpress', 'rasa', 'microsoft bot', 'azure bot', 'amazon lex', 'facebook messenger', 'telegram', 'slack', 'wechat', 'kik', 'line', 'viber', 'twilio', 'rocket.chat', 'mattermost', 'sendbird', 'socket.io', 'websocket', 'ai', 'virtual assistant'
]

KNOWN_CHATBOT_SCRIPTS = [
    'intercom', 'drift', 'tawk', 'livechat', 'zendesk', 'olark', 'chatwoot', 'freshchat', 'snapengage', 'liveagent', 'smartsupp', 'userlike', 'purechat', 'clickdesk', 'crisp', 'comm100', 'chatra', 'gubagoo', 'hubspot', 'whoson', 'zoho', 'conversocial', 'boldchat', 'liveperson', 'kayako', 'acquire', 'genesys', 'salesforce', 'ibm', 'google', 'meya', 'snatchbot', 'pandorabots', 'botpress', 'rasa', 'microsoft', 'azure', 'amazon', 'facebook', 'telegram', 'slack', 'wechat', 'kik', 'line', 'viber', 'twilio', 'rocket', 'mattermost', 'sendbird', 'socket', 'websocket', 'ai', 'virtual', 'assistant'
]

def basic_scan(url):
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
    except Exception as e:
        return {'url': url, 'error': str(e)}

    found = set()

    # 1. HTML Element Search
    for tag in soup.find_all(True):
        for attr in ['id', 'class', 'name']:
            val = tag.get(attr)
            if val:
                if isinstance(val, list):
                    val = ' '.join(val)
                for kw in CHATBOT_KEYWORDS:
                    if kw in val.lower():
                        found.add(f"element:{attr}={val}")

    # 2. Script Tag Inspection
    for script in soup.find_all('script', src=True):
        src = script['src'].lower()
        for kw in KNOWN_CHATBOT_SCRIPTS:
            if kw in src:
                found.add(f"script:{src}")

    # 3. Text Pattern Matching
    text_patterns = [
        r'chat with us', r'need help', r'ask a question', r'live chat', r'chat now', r'how can i help', r'virtual assistant', r'chatbot', r'let\'s chat', r'help center', r'contact us', r'support agent'
    ]
    for pat in text_patterns:
        if re.search(pat, soup.get_text().lower()):
            found.add(f"text:{pat}")

    # 4. Iframe Detection
    for iframe in soup.find_all('iframe', src=True):
        src = iframe['src'].lower()
        for kw in KNOWN_CHATBOT_SCRIPTS:
            if kw in src:
                found.add(f"iframe:{src}")

    return {'url': url, 'chatbot_indicators': list(found)}

def medium_scan(url):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {'url': url, 'error': 'playwright not installed'}

    found = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=20000)
            page.wait_for_load_state('networkidle', timeout=20000)
            html = page.content()
        except Exception as e:
            browser.close()
            return {'url': url, 'error': str(e)}
        browser.close()
        soup = BeautifulSoup(html, 'html.parser')

        # 1. HTML Element Search
        for tag in soup.find_all(True):
            for attr in ['id', 'class', 'name']:
                val = tag.get(attr)
                if val:
                    if isinstance(val, list):
                        val = ' '.join(val)
                    for kw in CHATBOT_KEYWORDS:
                        if kw in val.lower():
                            found.add(f"element:{attr}={val}")

        # 2. Script Tag Inspection
        for script in soup.find_all('script', src=True):
            src = script['src'].lower()
            for kw in KNOWN_CHATBOT_SCRIPTS:
                if kw in src:
                    found.add(f"script:{src}")

        # 3. Text Pattern Matching
        text_patterns = [
            r'chat with us', r'need help', r'ask a question', r'live chat', r'chat now', r'how can i help', r'virtual assistant', r'chatbot', r'let\'s chat', r'help center', r'contact us', r'support agent'
        ]
        for pat in text_patterns:
            if re.search(pat, soup.get_text().lower()):
                found.add(f"text:{pat}")

        # 4. Iframe Detection
        for iframe in soup.find_all('iframe', src=True):
            src = iframe['src'].lower()
            for kw in KNOWN_CHATBOT_SCRIPTS:
                if kw in src:
                    found.add(f"iframe:{src}")

        return {'url': url, 'chatbot_indicators': list(found)}

@click.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--mode', type=click.Choice(['basic', 'medium', 'advanced'], case_sensitive=False), default='basic', help='Scan mode: basic, medium, or advanced')
@click.option('--output', type=click.Choice(['text', 'json'], case_sensitive=False), default='text', help='Output format: text or json')
def main(urls, mode, output):
    """Scan one or more websites for chatbots."""
    results = []
    for url in urls:
        if not url.startswith('http'):
            url = 'http://' + url
        if mode == 'basic':
            result = basic_scan(url)
            results.append(result)
        elif mode == 'medium':
            result = medium_scan(url)
            results.append(result)
        else:
            results.append({'url': url, 'error': 'Only basic and medium modes implemented.'})

    if output == 'json':
        click.echo(json.dumps(results, indent=2))
    else:
        click.echo("\nChatScanner Report\n==================")
        for res in results:
            url = res['url']
            indicators = res.get('chatbot_indicators')
            if indicators is not None:
                count = len(indicators)
                click.echo(f"\nURL: {url}\nDetections: {count}")
                if count:
                    for ind in indicators:
                        click.echo(f"  - {ind}")
                else:
                    click.echo("  No chatbot indicators found.")
            else:
                click.echo(f"\nURL: {url}\nError: {res.get('error')}")

if __name__ == "__main__":
    main()
