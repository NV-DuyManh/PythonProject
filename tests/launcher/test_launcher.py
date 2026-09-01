import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from tools.codegate_launcher.launcher import CodeGateLauncher

class DummyLauncher(CodeGateLauncher):
    def __init__(self):
        # Prevent tkinter from actually starting a GUI window during tests if possible
        # We can just mock the __init__ but we want the methods.
        pass

@patch("tkinter.Tk.__init__")
def test_redact_secrets(mock_tk):
    launcher = DummyLauncher()
    launcher.statuses = {}
    
    text = """
    Here is a gh_token: ghp_1234567890abcdef
    And a groq key: gsk_abcdef1234567890
    And an openai key: sk-abcdef1234567890
    Bearer token123-abc.def
    DATABASE_URL=postgresql+psycopg2://user:secretpass@localhost/db
    PASSWORD=mysecret
    """
    
    redacted = launcher._redact_secrets(text)
    
    assert "ghp_1234567890abcdef" not in redacted
    assert "[REDACTED_GITHUB_TOKEN]" in redacted
    
    assert "gsk_abcdef1234567890" not in redacted
    assert "[REDACTED_GROQ_KEY]" in redacted
    
    assert "sk-abcdef1234567890" not in redacted
    assert "[REDACTED_API_KEY]" in redacted
    
    assert "token123-abc.def" not in redacted
    assert "Bearer [REDACTED]" in redacted
    
    assert "secretpass" not in redacted
    assert "postgresql+psycopg2://[USER]:[REDACTED]@" in redacted
    
    assert "mysecret" not in redacted
    assert "password=[REDACTED]" in redacted

@patch("tkinter.Tk.__init__")
def test_status_logic_ready(mock_tk):
    launcher = DummyLauncher()
    launcher.docker_running = True
    launcher.statuses = {
        "postgres": "READY",
        "redis": "READY",
        "migrate": "SUCCESS",
        "backend": "READY",
        "worker": "READY",
        "frontend": "READY"
    }
    
    # Mock UI updates
    launcher.status_labels = {k: MagicMock() for k in launcher.statuses}
    launcher.lbl_overall = MagicMock()
    launcher.btn_start = MagicMock()
    launcher.btn_stop = MagicMock()
    launcher.btn_restart = MagicMock()
    launcher.btn_open = MagicMock()
    
    launcher._update_ui_state()
    
    assert launcher.overall_state == "READY"

@patch("tkinter.Tk.__init__")
def test_status_logic_degraded(mock_tk):
    launcher = DummyLauncher()
    launcher.docker_running = True
    launcher.statuses = {
        "postgres": "READY",
        "redis": "READY",
        "migrate": "SUCCESS",
        "backend": "READY",
        "worker": "STOPPED", # Worker offline
        "frontend": "READY"
    }
    
    launcher.status_labels = {k: MagicMock() for k in launcher.statuses}
    launcher.lbl_overall = MagicMock()
    launcher.btn_start = MagicMock()
    launcher.btn_stop = MagicMock()
    launcher.btn_restart = MagicMock()
    launcher.btn_open = MagicMock()
    
    launcher._update_ui_state()
    
    assert launcher.overall_state == "DEGRADED (Worker Offline)"

@patch("tkinter.Tk.__init__")
def test_status_logic_starting(mock_tk):
    launcher = DummyLauncher()
    launcher.docker_running = True
    launcher.statuses = {
        "postgres": "READY",
        "redis": "READY",
        "migrate": "SUCCESS",
        "backend": "STARTING", 
        "worker": "READY",
        "frontend": "READY"
    }
    
    launcher.status_labels = {k: MagicMock() for k in launcher.statuses}
    launcher.lbl_overall = MagicMock()
    launcher.btn_start = MagicMock()
    launcher.btn_stop = MagicMock()
    launcher.btn_restart = MagicMock()
    launcher.btn_open = MagicMock()
    
    launcher._update_ui_state()
    
    assert launcher.overall_state == "STARTING"
    launcher.btn_start.state.assert_called_with(['disabled'])
