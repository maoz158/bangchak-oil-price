"""Serve the Bangchak fuel dashboard and proxy the Bangchak price API.

Standard library only, so it runs anywhere Python 3 is installed.

Local:   python3 server.py            -> http://127.0.0.1:8000
Online:  the host sets PORT, and HOST defaults to 0.0.0.0 when PORT is set.
"""

import json
import os
import ssl
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

API_URL = 'https://oil-price.bangchak.co.th/ApiOilPrice2/th'
ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get('PORT', '8000'))
HOST = os.environ.get('HOST', '0.0.0.0' if 'PORT' in os.environ else '127.0.0.1')

# Verified TLS is the default. Set ALLOW_INSECURE_TLS=1 only for local debugging
# when the Mac's Python cannot find the certificate chain.
if os.environ.get('ALLOW_INSECURE_TLS') == '1':
    SSL_CONTEXT = ssl._create_unverified_context()
else:
    SSL_CONTEXT = ssl.create_default_context()

UPSTREAM_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; bangchak-oil-price/1.0)',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://oil-price.bangchak.co.th/th',
}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def do_GET(self):
        if urlparse(self.path).path == '/api/oil':
            self.handle_oil_api()
            return
        super().do_GET()

    def handle_oil_api(self):
        try:
            req = Request(API_URL, headers=UPSTREAM_HEADERS)
            with urlopen(req, timeout=20, context=SSL_CONTEXT) as resp:
                raw = resp.read()
            # Refuse to forward anything that is not JSON.
            json.loads(raw.decode('utf-8'))
            self.send_json(raw, status=200)
        except HTTPError as exc:
            self.send_json_error(502, 'HTTPError', detail=f'{exc.code} {exc.reason}')
        except URLError as exc:
            self.send_json_error(502, 'URLError', detail=str(exc.reason))
        except Exception as exc:  # noqa: BLE001 - report anything unexpected as JSON
            self.send_json_error(500, type(exc).__name__, detail=str(exc))

    def send_json(self, body: bytes, status: int):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_json_error(self, status: int, error: str, detail: str):
        body = json.dumps({'error': error, 'detail': detail}, ensure_ascii=False).encode('utf-8')
        self.send_json(body, status=status)

    def log_message(self, format, *args):
        print('%s - %s' % (self.address_string(), format % args))


if __name__ == '__main__':
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f'Serving on http://{HOST}:{PORT}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
