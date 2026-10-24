#!/usr/bin/env python3
"""Run the pinned official MCP against an explicit independent API."""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler


def validate_url(value):
    parsed = urlsplit(value)
    if (parsed.scheme not in {'http', 'https'} or not parsed.hostname
            or parsed.username or parsed.password or parsed.query or parsed.fragment):
        raise ValueError('API URL must be HTTP(S), without credentials, query or fragment')
    if parsed.hostname.lower().rstrip('.') in {'firecrawl.dev', 'api.firecrawl.dev'}:
        raise ValueError('Use your independent API, not the Firecrawl Cloud endpoint')
    if parsed.scheme == 'http' and parsed.hostname not in {'localhost', '127.0.0.1', '::1'}:
        raise ValueError('Remote API connections require HTTPS')
    if parsed.port is not None and not 1 <= parsed.port <= 65535:
        raise ValueError('Invalid port')
    return value.rstrip('/')


def child_env(api_url, source):
    env = {k: source[k] for k in ('PATH', 'HOME', 'TMPDIR', 'TEMP', 'TMP', 'SYSTEMROOT',
                                  'LANG', 'LC_ALL', 'SSL_CERT_FILE', 'SSL_CERT_DIR') if k in source}
    env.update(FIRECRAWL_API_URL=api_url, FIRECRAWL_NO_SEARCH_FEEDBACK='true',
               FIRECRAWL_NO_ENDPOINT_FEEDBACK='true', FIRECRAWL_INTEGRATION='sol-fable-self-hosted')
    # No inherited cloud credentials, HTTP mode, proxies or paid-provider variables.
    if source.get('FIRECRAWL_SELF_HOSTED_API_KEY'):
        env['FIRECRAWL_API_KEY'] = source['FIRECRAWL_SELF_HOSTED_API_KEY']
    return env


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('API readiness redirected; configure the final trusted API URL explicitly')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api-url', required=True)
    args = parser.parse_args()
    api_url = validate_url(args.api_url)
    root = Path(__file__).resolve().parent
    entry = root / 'node_modules/firecrawl-mcp/dist/index.js'
    package = root / 'node_modules/firecrawl-mcp/package.json'
    node = shutil.which('node')
    if not node or not entry.is_file() or not package.is_file():
        raise ValueError('Install Node >=22 and run npm ci --ignore-scripts --no-audit --no-fund in sol-fable/mcp')
    if json.loads(package.read_text())['version'] != '3.34.1':
        raise ValueError('Unexpected MCP version; restore the pinned npm lockfile installation')
    version = subprocess.check_output([node, '--version'], text=True).strip()
    if int(version.lstrip('v').split('.')[0]) < 22:
        raise ValueError('Node >=22 is required')
    env = child_env(api_url, os.environ)
    headers = {}
    if env.get('FIRECRAWL_API_KEY'):
        headers['Authorization'] = 'Bearer ' + env['FIRECRAWL_API_KEY']
    request = Request(api_url + '/v0/health/readiness', headers=headers)
    opener = build_opener(ProxyHandler({}), NoRedirects())
    with opener.open(request, timeout=5) as response:
        health = json.loads(response.read(65537))
        if response.status != 200 or health.get('status') != 'ok':
            raise ValueError('Independent Firecrawl API readiness has not passed')
    # dotenv in the official entry point cannot read a caller's unrelated .env.
    with tempfile.TemporaryDirectory(prefix='sol-fable-firecrawl-mcp-') as cwd:
        child = subprocess.Popen([node, str(entry)], env=env, cwd=cwd)
        previous = {}
        def forward(signum, frame):
            if child.poll() is None:
                child.send_signal(signum)
        try:
            for signum in (signal.SIGINT, signal.SIGTERM):
                previous[signum] = signal.signal(signum, forward)
            return child.wait()
        finally:
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=10)
            for signum, handler in previous.items():
                signal.signal(signum, handler)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        print('Firecrawl local MCP: ' + str(error), file=sys.stderr)
        sys.exit(1)
