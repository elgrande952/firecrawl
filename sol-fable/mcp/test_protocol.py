"""Real official MCP process, simulated local API: transport/routing tests only."""
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('local_mcp_runner', ROOT / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class ContractTest(unittest.TestCase):
    def test_explicit_endpoint_and_credentials(self):
        for url in ('https://api.firecrawl.dev', 'http://example.com', 'https://a:b@example.com',
                    'http://127.0.0.1:3002/?api_key=x'):
            with self.assertRaises(ValueError):
                runner.validate_url(url)
        clean = runner.child_env('http://127.0.0.1:3002', {
            'FIRECRAWL_API_KEY': 'cloud-do-not-forward', 'CLOUD_SERVICE': 'true',
            'OPENAI_API_KEY': 'never-forward', 'HTTP_STREAMABLE_SERVER': 'true', 'PATH': '/bin'})
        self.assertNotIn('FIRECRAWL_API_KEY', clean)
        self.assertNotIn('OPENAI_API_KEY', clean)
        self.assertNotIn('CLOUD_SERVICE', clean)
        self.assertNotIn('HTTP_STREAMABLE_SERVER', clean)

    def test_official_protocol_against_simulated_api(self):
        captured = []
        class API(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def reply(self, payload):
                encoded = json.dumps(payload).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)
            def do_GET(self):
                captured.append({'method': 'GET', 'path': self.path,
                                 'authorization_present': bool(self.headers.get('Authorization'))})
                self.reply({'status': 'ok'})
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                captured.append({'method': 'POST', 'path': self.path, 'body': body,
                                 'authorization_present': bool(self.headers.get('Authorization'))})
                self.reply({'success': True, 'data': {'markdown': '# LOCAL_MOCK_MARKER',
                           'metadata': {'title': 'Local API fixture', 'statusCode': 200,
                                        'sourceURL': 'https://example.com'}}})
        server = ThreadingHTTPServer(('127.0.0.1', 0), API)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        env = dict(os.environ, FIRECRAWL_API_KEY='cloud-do-not-forward', CLOUD_SERVICE='true',
                   OPENAI_API_KEY='never-forward', HTTP_STREAMABLE_SERVER='true')
        env.pop('FIRECRAWL_SELF_HOSTED_API_KEY', None)
        process = subprocess.Popen([sys.executable, str(ROOT/'run.py'), '--api-url',
                         f'http://127.0.0.1:{server.server_port}'], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        messages, errors = queue.Queue(), []
        def read_stdout():
            for line in process.stdout:
                try:
                    messages.put(json.loads(line))
                except json.JSONDecodeError:
                    messages.put({'invalid_stdout': line})
        threading.Thread(target=read_stdout, daemon=True).start()
        threading.Thread(target=lambda: errors.extend(process.stderr.readlines()), daemon=True).start()
        def send(data):
            process.stdin.write(json.dumps(data)+'\n')
            process.stdin.flush()
        def answer(request_id):
            deadline = time.monotonic()+25
            while time.monotonic() < deadline:
                reply = messages.get(timeout=max(.1, deadline-time.monotonic()))
                self.assertNotIn('invalid_stdout', reply)
                if reply.get('id') == request_id:
                    self.assertNotIn('error', reply, reply)
                    return reply['result']
            self.fail('MCP response timed out')
        try:
            send({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {
                'protocolVersion': '2024-11-05', 'capabilities': {},
                'clientInfo': {'name': 'sol-fable-contract-test', 'version': '1.0'}}})
            initialized = answer(1)
            send({'jsonrpc': '2.0', 'method': 'notifications/initialized'})
            send({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}})
            names = sorted(x['name'] for x in answer(2)['tools'])
            self.assertTrue({'firecrawl_scrape', 'firecrawl_map', 'firecrawl_crawl',
                             'firecrawl_search'} <= set(names))
            send({'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {
                'name': 'firecrawl_scrape', 'arguments': {'url': 'https://example.com',
                                                        'formats': ['markdown']}}})
            result = answer(3)
            self.assertFalse(result.get('isError'), result)
            self.assertIn('LOCAL_MOCK_MARKER', json.dumps(result))
            self.assertTrue(any(x['path']=='/v2/scrape' for x in captured), captured)
            self.assertTrue(all(not x['authorization_present'] for x in captured), captured)
            evidence = {'scope': 'Official MCP transport against simulated local API; not a live scrape',
                        'package': 'firecrawl-mcp@3.34.1', 'serverInfo': initialized.get('serverInfo'),
                        'tool_count': len(names), 'tools': names, 'captured_requests': captured,
                        'inherited_cloud_key_forwarded': False, 'status': 'passed',
                        'lock_sha256': hashlib.sha256((ROOT/'package-lock.json').read_bytes()).hexdigest()}
            (ROOT/'protocol-verification.json').write_text(json.dumps(evidence, indent=2)+'\n')
        finally:
            process.stdin.close()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=10)
            server.shutdown()
            server.server_close()
            process.stdout.close()
            process.stderr.close()


if __name__ == '__main__':
    unittest.main()
