from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict
import asyncio
import os
import sys

class TestExecutor(ABC):
    """Protocol for safely executing tests."""
    
    @abstractmethod
    async def execute(self, 
                      command: List[str], 
                      working_directory: str, 
                      env: Optional[Dict[str, str]] = None,
                      timeout_seconds: int = 900) -> Tuple[int, str, str, bool]:
        """
        Executes the given command safely.
        Returns:
            (exit_code, stdout, stderr, is_timeout)
        """
        pass


class DisabledExecutor(TestExecutor):
    """Default executor that simply rejects execution for safety."""
    
    async def execute(self, 
                      command: List[str], 
                      working_directory: str, 
                      env: Optional[Dict[str, str]] = None,
                      timeout_seconds: int = 900) -> Tuple[int, str, str, bool]:
        return -1, "Test execution is DISABLED by policy.", "", False


class LocalTrustedExecutor(TestExecutor):
    """
    Executes tests locally via safe subprocess. 
    WARNING: THIS IS NOT A SANDBOX. It executes arbitrary repository code.
    Use ONLY for trusted environments.
    """
    
    def _sanitize_env(self, provided_env: Optional[Dict[str, str]]) -> Dict[str, str]:
        safe_env = {}
        # Allow basic system paths and variables
        for key in ["PATH", "SYSTEMROOT", "USERPROFILE", "HOME", "LANG", "LC_ALL"]:
            if key in os.environ:
                safe_env[key] = os.environ[key]
        
        if provided_env:
            for k, v in provided_env.items():
                safe_env[k] = v
        return safe_env

    def _validate_path(self, working_directory: str) -> bool:
        # Prevent traversal and absolute path injection.
        if ".." in working_directory:
            return False
            
        # Reject absolute paths (Linux/macOS)
        if working_directory.startswith("/"):
            return False
            
        # Reject Windows drive escapes (e.g. C:\)
        if len(working_directory) >= 2 and working_directory[1] == ":" and working_directory[0].isalpha():
            return False
            
        # Reject Windows UNC paths
        if working_directory.startswith("\\\\"):
            return False
            
        return True

    async def execute(self, 
                      command: List[str], 
                      working_directory: str, 
                      env: Optional[Dict[str, str]] = None,
                      timeout_seconds: int = 900) -> Tuple[int, str, str, bool]:
        
        if not self._validate_path(working_directory):
            return -1, "", "Path traversal detected in working directory.", False
            
        safe_env = self._sanitize_env(env)
        
        try:
            # We enforce shell=False inherently by passing a list to create_subprocess_exec
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=working_directory,
                env=safe_env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=timeout_seconds)
                is_timeout = False
            except asyncio.TimeoutError:
                process.kill()
                await process.communicate()  # drain
                return -1, "", f"Execution timed out after {timeout_seconds} seconds.", True
                
            stdout = stdout_bytes.decode('utf-8', errors='replace')
            stderr = stderr_bytes.decode('utf-8', errors='replace')
            
            # Truncate output to prevent unbounded memory/db consumption
            max_len = 64 * 1024
            if len(stdout) > max_len:
                stdout = stdout[:max_len] + "\n...[TRUNCATED]"
            if len(stderr) > max_len:
                stderr = stderr[:max_len] + "\n...[TRUNCATED]"
                
            exit_code = process.returncode if process.returncode is not None else -1
            return exit_code, stdout, stderr, is_timeout
            
        except Exception as e:
            return -1, "", f"Executor exception: {str(e)}", False


class DockerTestExecutor(TestExecutor):
    """
    Executes tests via a Docker container for isolation.
    Stub implementation for production architecture blueprint.
    """
    
    def __init__(self, docker_image: str):
        self.docker_image = docker_image
        
    async def execute(self, 
                      command: List[str], 
                      working_directory: str, 
                      env: Optional[Dict[str, str]] = None,
                      timeout_seconds: int = 900) -> Tuple[int, str, str, bool]:
        # Implement safe docker run building
        docker_cmd = [
            "docker", "run", 
            "--rm", 
            "--network", "none", # strict isolation
            "-v", f"{working_directory}:/workspace",
            "-w", "/workspace",
            self.docker_image
        ]
        docker_cmd.extend(command)
        
        # Uses standard safe argv construction internally (shell=False)
        process = await asyncio.create_subprocess_exec(
            *docker_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=timeout_seconds)
            is_timeout = False
        except asyncio.TimeoutError:
            process.kill()
            return -1, "", f"Docker execution timed out after {timeout_seconds} seconds.", True
            
        return process.returncode or -1, stdout_bytes.decode('utf-8', errors='replace'), stderr_bytes.decode('utf-8', errors='replace'), is_timeout
