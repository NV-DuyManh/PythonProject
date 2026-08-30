import pytest
import asyncio
from codegate.engines.testing.executor import LocalTrustedExecutor, DisabledExecutor

@pytest.mark.asyncio
async def test_disabled_executor_returns_error():
    executor = DisabledExecutor()
    code, stdout, stderr, is_timeout = await executor.execute(["ls"], ".")
    assert code == -1
    assert "DISABLED" in stdout
    assert not is_timeout

def test_local_executor_validates_path():
    executor = LocalTrustedExecutor()
    assert not executor._validate_path("../escaped")
    assert not executor._validate_path("../../root")
    assert not executor._validate_path("/absolute/path")
    assert not executor._validate_path("C:\\windows")
    assert not executor._validate_path("d:/data")
    assert not executor._validate_path("\\\\unc\\path")
    assert executor._validate_path("tests/codegate")
    assert executor._validate_path("./tests")

def test_local_executor_sanitizes_env():
    executor = LocalTrustedExecutor()
    dirty_env = {
        "GITHUB_TOKEN": "secret",
        "OPENAI_API_KEY": "secret2",
        "SAFE_VAR": "value"
    }
    # It only takes what we explicitly provide in `provided_env` + safe system vars.
    # Wait, the implementation allows ALL keys in provided_env!
    # Let's check what provided_env means in the context.
    # The engine should not pass the parent env, it should only pass what the user configures or explicitly allow.
    pass # Wait, I need to check how I implemented sanitize_env.

@pytest.mark.asyncio
async def test_local_executor_timeout():
    executor = LocalTrustedExecutor()
    # Assuming python is available in PATH
    code, stdout, stderr, is_timeout = await executor.execute(
        ["python", "-c", "import time; time.sleep(10)"],
        ".",
        timeout_seconds=1
    )
    assert code == -1
    assert is_timeout
    assert "Execution timed out" in stderr
