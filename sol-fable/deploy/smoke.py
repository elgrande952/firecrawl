#!/usr/bin/env python3
"""One bounded live scrape; prints proof only when all assertions pass."""
import argparse
import json
from urllib.request import Request, urlopen

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--api-url', default='http://127.0.0.1:3002')
args = parser.parse_args()
base = args.api_url.rstrip('/')
with urlopen(base+'/v0/health/readiness', timeout=5) as response:
    assert response.status == 200
    assert json.load(response)['status'] == 'ok'
request = Request(base+'/v2/scrape', method='POST',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({'url':'https://example.com','formats':['markdown'],'timeout':60000}).encode())
with urlopen(request, timeout=75) as response:
    result = json.load(response)
assert result.get('success') is True, result
data = result.get('data', {})
assert data.get('metadata', {}).get('statusCode') == 200, result
assert isinstance(data.get('markdown'), str) and data['markdown'].strip(), result
# Main-content extraction may omit the page heading; metadata carries the title.
assert data.get('metadata', {}).get('title') == 'Example Domain', result
print(json.dumps({'status':'PASS','live_scrape':True,'url':'https://example.com',
    'page_status':200,'markdown_length':len(data['markdown'])}))
