import hmac, hashlib, json, requests
secret = b'my-super-secret'
payload = {
    'action': 'opened',
    'pull_request': {
        'number': 25,
        'html_url': 'https://github.com/NV-DuyManh/codegate-e2e-demo/pull/25',
        'head': {'sha': 'dummy-sha123', 'ref': 'test-pr-1'},
        'base': {'sha': 'dummy-sha456', 'ref': 'main'}
    },
    'repository': {
        'id': 1,
        'full_name': 'NV-DuyManh/codegate-e2e-demo',
        'owner': {'login': 'NV-DuyManh'},
        'name': 'codegate-e2e-demo',
        'html_url': 'https://github.com/NV-DuyManh/codegate-e2e-demo',
        'clone_url': 'https://github.com/NV-DuyManh/codegate-e2e-demo.git'
    },
    'installation': {'id': 158169897}
}
body = json.dumps(payload).encode('utf-8')
signature = 'sha256=' + hmac.new(secret, body, hashlib.sha256).hexdigest()
headers = {
    'X-GitHub-Event': 'pull_request',
    'X-GitHub-Delivery': 'dummy-delivery-5',
    'X-Hub-Signature-256': signature,
    'Content-Type': 'application/json'
}
resp = requests.post('http://127.0.0.1:8000/api/v1/github_webhooks', data=body, headers=headers)
print(resp.status_code, resp.text)
