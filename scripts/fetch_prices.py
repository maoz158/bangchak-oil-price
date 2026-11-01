"""Fetch Bangchak oil prices and write them under data/.

Run by .github/workflows/update-prices.yml once a day. Standard library only.

Writes:
  data/latest.json   the raw Bangchak payload plus FetchedAt, so index.html renders it unchanged
  data/history.json  appended only when G95 or E20 today's price changes

When ISSUE_BODY_FILE is set and prices changed, a markdown summary is written
there for the workflow to post as a GitHub Issue.
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen

API_URL = 'https://oil-price.bangchak.co.th/ApiOilPrice2/th'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; bangchak-oil-price/1.0)',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://oil-price.bangchak.co.th/th',
}
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
LATEST_PATH = DATA_DIR / 'latest.json'
HISTORY_PATH = DATA_DIR / 'history.json'
HISTORY_LIMIT = 365
BANGKOK = timezone(timedelta(hours=7))

G95_NAMES = ['แก๊สโซฮอล์ 95 S EVO', 'Gasohol 95 S EVO']
G95_KEYWORDS = ['95sevo', 'gasohol95sevo', 'แก๊สโซฮอล์95sevo']
E20_NAMES = ['แก๊สโซฮอล์ E20 S EVO', 'Gasohol E20 S EVO', 'E20 S EVO']
E20_KEYWORDS = ['e20sevo', 'gasohole20', 'แก๊สโซฮอล์e20']


def normalize(name):
    return str(name or '').lower().replace(' ', '').replace('-', '').replace('.', '')


def find_oil(oils, exact_names, keywords):
    exact = {normalize(n) for n in exact_names}
    for item in oils:
        if normalize(item.get('OilName')) in exact:
            return item
    for item in oils:
        name = normalize(item.get('OilName'))
        if any(keyword in name for keyword in map(normalize, keywords)):
            return item
    return None


def fetch_raw():
    req = Request(API_URL, headers=HEADERS)
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def summarize(payload):
    root = payload[0] if isinstance(payload, list) else payload
    oils = root['OilList']
    if isinstance(oils, str):
        oils = json.loads(oils)

    g95 = find_oil(oils, G95_NAMES, G95_KEYWORDS)
    e20 = find_oil(oils, E20_NAMES, E20_KEYWORDS)
    if g95 is None or e20 is None:
        names = [item.get('OilName') for item in oils]
        raise RuntimeError(f'ไม่พบ G95 หรือ E20 ในข้อมูล ชื่อที่มี: {names}')

    g95_today = float(g95['PriceToday'])
    e20_today = float(e20['PriceToday'])
    return {
        'priceDate': root.get('OilPriceDate'),
        'priceTime': root.get('OilPriceTime'),
        'oilDateNow': root.get('OilDateNow'),
        'g95': g95_today,
        'e20': e20_today,
        'spread': round(g95_today - e20_today, 2),
    }


def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def snapshot(payload):
    """Everything the page displays from the price list, for change detection."""
    root = payload[0] if isinstance(payload, list) else payload
    oils = root['OilList']
    if isinstance(oils, str):
        oils = json.loads(oils)
    return {
        'priceDate': root.get('OilPriceDate'),
        'priceTime': root.get('OilPriceTime'),
        'oils': [[item.get('OilName'), item.get('PriceToday'), item.get('PriceYesterday'), item.get('PriceTomorrow')] for item in oils],
    }


def previous_payload():
    return read_json(LATEST_PATH, None)


def previous_summary(previous):
    if not previous:
        return None
    try:
        return summarize(previous)
    except (KeyError, RuntimeError, ValueError, TypeError):
        return None


def build_issue_body(previous, current):
    def line(label, key):
        new = current[key]
        if previous is None:
            return f'- {label}: **{new:.2f} บาท**'
        old = previous[key]
        if round(new - old, 2) == 0:
            return None
        return f'- {label}: **{new:.2f} บาท** (จาก {old:.2f} บาท, เปลี่ยน {new - old:+.2f})'

    changed_lines = [
        line('แก๊สโซฮอล์ 95 S EVO', 'g95'),
        line('แก๊สโซฮอล์ E20 S EVO', 'e20'),
    ]
    return '\n'.join([
        f"ราคาวันที่ {current['priceDate']} เวลา {current['priceTime']} น.",
        '',
        *[item for item in changed_lines if item],
        f"- ส่วนต่าง G95 - E20: **{current['spread']:.2f} บาท**",
        '',
        'ดูหน้าเว็บ: https://maoz158.github.io/bangchak-oil-price/',
    ])


def main():
    payload = fetch_raw()
    current = summarize(payload)
    previous_raw = previous_payload()
    previous = previous_summary(previous_raw)

    # Only write when something the page shows has changed, so unchanged days make no commit.
    displayed_changed = previous_raw is None or snapshot(payload) != snapshot(previous_raw)
    g95_e20_changed = previous is None or previous['g95'] != current['g95'] or previous['e20'] != current['e20']
    price_changed = previous is not None and g95_e20_changed

    DATA_DIR.mkdir(exist_ok=True)
    if displayed_changed:
        root = payload[0] if isinstance(payload, list) else payload
        root['FetchedAt'] = datetime.now(BANGKOK).isoformat(timespec='seconds')
        write_json(LATEST_PATH, payload if isinstance(payload, list) else [payload])

    if g95_e20_changed:
        history = read_json(HISTORY_PATH, [])
        history.append({
            'savedAt': datetime.now(BANGKOK).isoformat(timespec='seconds'),
            'priceDate': current['priceDate'],
            'g95': current['g95'],
            'e20': current['e20'],
            'spread': current['spread'],
        })
        write_json(HISTORY_PATH, history[-HISTORY_LIMIT:])

    print(f"G95={current['g95']} E20={current['e20']} displayed_changed={displayed_changed} price_changed={price_changed}")

    issue_body_file = os.environ.get('ISSUE_BODY_FILE')
    if price_changed and issue_body_file:
        Path(issue_body_file).write_text(build_issue_body(previous, current), encoding='utf-8')

    output = os.environ.get('GITHUB_OUTPUT')
    if output:
        with open(output, 'a', encoding='utf-8') as fh:
            fh.write(f"price_changed={'true' if price_changed else 'false'}\n")


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - the workflow reports any failure
        print(f'fetch failed: {exc}', file=sys.stderr)
        sys.exit(1)
