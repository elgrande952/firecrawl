#!/usr/bin/env python3
"""One real scrape through the official MCP and independent local Firecrawl API."""
import json
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parent
process = subprocess.Popen([sys.executable, str(ROOT/'run.py'), '--api-url',
                            'http://127.0.0.1:3002'], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
messages, stderr = queue.Queue(), []

def reader():
    for line in process.stdout:
        try:
            messages.put(json.loads(line))
        except json.JSONDecodeError:
            messages.put({'invalid_stdout': True})

threading.Thread(target=reader, daemon=True).start()
threading.Thread(target=lambda: stderr.extend(process.stderr.readlines()), daemon=True).start()

def send(data):
    process.stdin.write(json.dumps(data)+'\n')
    process.stdin.flush()

def answer(request_id):
    deadline = time.monotonic()+80
    while time.monotonic() < deadline:
        response = messages.get(timeout=max(.1, deadline-time.monotonic()))
        assert not response.get('invalid_stdout'), 'Non-protocol stdout'
        if response.get('id') == request_id:
            assert 'error' not in response, response
            return response['result']
    raise TimeoutError('MCP response timed out')

try:
    send({'jsonrpc':'2.0','id':1,'method':'initialize','params':{
        'protocolVersion':'2024-11-05','capabilities':{},
        'clientInfo':{'name':'sol-fable-live-check','version':'1.0'}}})
    server = answer(1)
    send({'jsonrpc':'2.0','method':'notifications/initialized'})
    send({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{
        'name':'firecrawl_scrape','arguments':{'url':'https://example.com','formats':['markdown']}}})
    result = answer(2)
    assert not result.get('isError'), result
    payload = result.get('structuredContent')
    if payload is None:
        payload = json.loads(next(c['text'] for c in result['content'] if c.get('type')=='text'))
    if payload.get('success') is False:
        raise AssertionError(payload)
    document = payload.get('data', payload)
    assert document.get('metadata',{}).get('statusCode') == 200, payload
    assert document.get('markdown','').strip(), payload
    print(json.dumps({'status':'PASS','real_mcp_scrape':True,'simulated_api':False,
                      'api_url':'http://127.0.0.1:3002','server':server.get('serverInfo'),
                      'page_status':200,'markdown_length':len(document['markdown'])}))
finally:
    process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.terminate()
        process.wait(timeout=10)
