import re

with open('tests/codegate/api/test_integration_group05.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '        head_sha="abcdef",',
    '        head_sha="abcdef",\n        author_username="testuser",'
)

with open('tests/codegate/api/test_integration_group05.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('tests/codegate/engines/test_analyzers.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = """
        call_count = {"ruff": 0}
        async def mock_wait_for(aw, timeout):
            call_count["ruff"] += 1
            if call_count["ruff"] == 1:
                raise asyncio.TimeoutError()
            return await original_wait_for(aw, timeout)
"""

# replace the mock_wait_for
content = re.sub(
    r'        async def mock_wait_for\(aw, timeout\):.*?(?=\n        with patch)',
    replacement,
    content,
    flags=re.DOTALL
)

with open('tests/codegate/engines/test_analyzers.py', 'w', encoding='utf-8') as f:
    f.write(content)

