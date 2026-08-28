with open('codegate/config/settings.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'ANALYZER_TIMEOUT_SECONDS' not in content:
    content = content.replace(
        'STATIC_ANALYSIS_ENABLED: bool = True',
        'STATIC_ANALYSIS_ENABLED: bool = True\n    ANALYZER_TIMEOUT_SECONDS: int = 300'
    )
    with open('codegate/config/settings.py', 'w', encoding='utf-8') as f:
        f.write(content)
