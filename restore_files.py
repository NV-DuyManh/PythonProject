import json
import os

transcript_path = r'C:\Users\Admin\.gemini\antigravity-ide\brain\1b2c695a-1118-4b73-8b46-6f7570ea4b4c\.system_generated\logs\transcript_full.jsonl'

vfs = {}

with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
        except:
            continue
        if 'tool_calls' in data:
            for call in data['tool_calls']:
                name = call.get('name')
                args = call.get('args', {})
                if name == 'write_to_file':
                    target = args.get('TargetFile', '')
                    
                    keywords = [
                        'integrations', 'engines', 'github_sync_service.py', 
                        'analysis_orchestrator.py', 'webhook', 'sync.py', 
                        'group04', 'GROUP_04', 'group05', 'GROUP_05',
                        'test_analyzers.py', '3f9ea3c19126', '77e29927998f', 'f1017ab69a6a'
                    ]
                    
                    if any(k in target for k in keywords):
                        vfs[target] = args.get('CodeContent', '')

for filename, content in vfs.items():
    print(f'Restoring UNTRACKED: {filename}')
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)
