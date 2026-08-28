with open('tests/codegate/api/test_integration_group05.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('        name="repo",', '        name="repo",\n        full_name="test/repo",')

with open('tests/codegate/api/test_integration_group05.py', 'w', encoding='utf-8') as f:
    f.write(content)
