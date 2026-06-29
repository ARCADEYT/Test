import json
import urllib.parse
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler

API_URL = 'https://smmapi.com/api/v2/'
API_KEY = '6e032cb6cb976d5269408d3c6adb6932373a513ee09783b59a4e526c9bb9eef3'
SERVICE_ID = '7356'

class ProxyRequestHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/proxy.php':
            self.send_error(404, 'Not Found')
            return

        content_length = int(self.headers.get('Content-Length', 0))
        raw_body = self.rfile.read(content_length).decode('utf-8')

        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'JSON inválido.'}).encode('utf-8'))
            return

        link = payload.get('link', '').strip()
        quantity = payload.get('quantity', 0)

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 0

        if not link:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Falta el enlace del reel.'}).encode('utf-8'))
            return

        if quantity < 10 or quantity > 50000:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Cantidad inválida. Debe ser entre 10 y 50.000.'}).encode('utf-8'))
            return

        data = urllib.parse.urlencode({
            'key': API_KEY,
            'action': 'add',
            'service': SERVICE_ID,
            'link': link,
            'quantity': quantity,
        }).encode('utf-8')

        req = urllib.request.Request(API_URL, data=data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode('utf-8', errors='replace')
                self.send_response(resp.status)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(body.encode('utf-8'))
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'API HTTP {e.code}', 'body': body}).encode('utf-8'))
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Error de conexión al API', 'details': str(e)}).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=ProxyRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Serving on http://localhost:{port}/')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
