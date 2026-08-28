with open('tests/codegate/api/test_integration_group05.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '        author_username="testuser",',
    '        author_username="testuser",\n        source_branch="feature",\n        target_branch="main",'
)

with open('tests/codegate/api/test_integration_group05.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('tests/codegate/engines/test_analyzers.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_mock = '''        async def mock_wait_for(aw, timeout):
            if runner.analyzers[0] in [a for a in runner.analyzers if type(a) == TimeoutRuff]:
                raise asyncio.TimeoutError()
            return await original_wait_for(aw, timeout)'''

new_mock = '''        call_count = {"ruff": 0}
        async def mock_wait_for(aw, timeout):
            call_count["ruff"] += 1
            if call_count["ruff"] == 1:
                raise asyncio.TimeoutError()
            return await original_wait_for(aw, timeout)'''

content = content.replace(old_mock, new_mock)

with open('tests/codegate/engines/test_analyzers.py', 'w', encoding='utf-8') as f:
    f.write(content)

