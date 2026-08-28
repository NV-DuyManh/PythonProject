with open('codegate/database/models/analysis.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('    FAILED = "FAILED"', '    FAILED = "FAILED"\n    TIMEOUT = "TIMEOUT"\n    SUCCESS = "SUCCESS"\n    SKIPPED = "SKIPPED"\n    NOT_APPLICABLE = "NOT_APPLICABLE"')

with open('codegate/database/models/analysis.py', 'w', encoding='utf-8') as f:
    f.write(content)
