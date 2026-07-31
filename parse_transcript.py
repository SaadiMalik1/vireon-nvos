import json

with open('/home/ronin/.gemini/antigravity-ide/brain/96ca1dde-2ae2-4f70-9eb5-c6e687407dc2/.system_generated/logs/transcript.jsonl', 'r') as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get('type') == 'USER_INPUT' and 'Phase B' in data.get('content', ''):
                print(data['content'])
        except Exception as e:
            pass
