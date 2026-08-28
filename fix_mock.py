import re

with open('tests/codegate/engines/test_analyzers.py', 'r', encoding='utf-8') as f:
    content = f.read()

def replacer(match):
    return """        call_count = {"ruff": 0}
        async def mock_wait_for(aw, timeout):
            call_count["ruff"] += 1
            if call_count["ruff"] == 1:
                raise asyncio.TimeoutError()
            return await original_wait_for(aw, timeout)
"""

content = re.sub(
    r'        async def mock_wait_for\(aw, timeout\):.*?return await original_wait_for\(aw, timeout\)\n',
    replacer,
    content,
    flags=re.DOTALL
)

with open('tests/codegate/engines/test_analyzers.py', 'w', encoding='utf-8') as f:
    f.write(content)
