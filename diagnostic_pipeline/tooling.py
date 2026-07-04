import shutil
import subprocess
from pathlib import Path
from typing import Callable, List, Optional

from .models import ToolResult


class ToolRunner:
    def __init__(self, timeout_seconds: float = 5.0) -> None:
        self.timeout_seconds = timeout_seconds

    def exists(self, executable: str) -> bool:
        return shutil.which(executable) is not None

    def run(
        self,
        command: List[str],
        cwd: Optional[Path] = None,
        timeout_seconds: Optional[float] = None,
        input_data: Optional[str] = None,
        env: Optional[dict] = None,
        preexec_fn: Optional[Callable[[], None]] = None,
    ) -> ToolResult:
        tool_name = command[0]
        if not self.exists(tool_name):
            return ToolResult(tool_name=tool_name, available=False, exit_code=127, stdout="", stderr=f"Tool not found: {tool_name}")
        try:
            completed = subprocess.run(
                command,
                cwd=str(cwd) if cwd else None,
                capture_output=True,
                text=True,
                timeout=timeout_seconds or self.timeout_seconds,
                input=input_data,
                env=env,
                preexec_fn=preexec_fn,
                check=False,
            )
            return ToolResult(
                tool_name=tool_name,
                available=True,
                exit_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
            )
        except subprocess.TimeoutExpired as exc:
            return ToolResult(
                tool_name=tool_name,
                available=True,
                exit_code=124,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                timed_out=True,
            )
