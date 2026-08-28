import os

with open('codegate/engines/analyzers/ruff_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"--format", "json"', '"--output-format", "json"')

with open('codegate/engines/analyzers/ruff_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('tests/codegate/engines/test_analyzers.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('range(20)', 'range(50)')

with open('tests/codegate/engines/test_analyzers.py', 'w', encoding='utf-8') as f:
    f.write(content)
