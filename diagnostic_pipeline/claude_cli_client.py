"""LLM client that talks to the local `claude` CLI (Claude Code headless mode).

Reuses your existing Claude Code login — no API key needed. Exposes only the
slice of the official OpenAI client the pipeline uses:
``client.responses.create(model=, instructions=, input=).output_text``.

Enable via ``USE_CLAUDE_LOCAL=true``. Tunables (env):
  CLAUDE_LOCAL_BIN      path to the claude binary (default: "claude")
  CLAUDE_LOCAL_MODEL    --model to pass (e.g. claude-haiku-4-5 to cut cost)
  CLAUDE_LOCAL_TIMEOUT  per-call timeout in seconds (default: 120)
"""
import json
import os
import re
import shutil
import subprocess
import tempfile

# Real Claude model ids the CLI accepts, e.g. claude-haiku-4-5, claude-sonnet-5, claude-opus-4-8.
_CLAUDE_MODEL_RE = re.compile(r"^claude-(opus|sonnet|haiku|fable)", re.IGNORECASE)


class _Resp:
    def __init__(self, text: str):
        self.output_text = text


class _Responses:
    def __init__(self, client: "ClaudeCLIClient"):
        self._c = client

    def create(self, model=None, instructions="", input="", **_):
        return self._c._complete(instructions, input, model)


class ClaudeCLIClient:
    def __init__(self, binary=None, model=None, timeout_seconds=None, cwd=None):
        self.binary = binary or os.getenv("CLAUDE_LOCAL_BIN", "claude")
        self.model = model or os.getenv("CLAUDE_LOCAL_MODEL")
        self.timeout_seconds = timeout_seconds or float(os.getenv("CLAUDE_LOCAL_TIMEOUT", "120"))
        # Run outside the repo so a project CLAUDE.md / settings don't bloat the prompt.
        self.cwd = cwd or tempfile.gettempdir()
        if shutil.which(self.binary) is None:
            raise RuntimeError(
                f"claude CLI not found on PATH (looked for '{self.binary}'). "
                "Install Claude Code or set CLAUDE_LOCAL_BIN."
            )
        self.responses = _Responses(self)

    def _complete(self, instructions: str, user_input: str, model=None) -> _Resp:
        # ponytail: skip user/project settings (plugins, hooks) and all MCP servers.
        # Halves cold-start (~11s -> ~5.5s/call); OAuth login is unaffected. --bare would
        # be faster still but forces ANTHROPIC_API_KEY, breaking the reuse-my-login point.
        cmd = [self.binary, "-p", "--output-format", "json",
               "--setting-sources", "", "--strict-mcp-config"]
        if instructions:
            cmd += ["--system-prompt", instructions]
        chosen = model or self.model
        # Only forward genuine claude-* model ids; placeholders (e.g. "claude-local") and
        # non-claude names fall through so the CLI uses its own default model.
        if chosen and _CLAUDE_MODEL_RE.match(str(chosen)):
            cmd += ["--model", str(chosen)]
        try:
            proc = subprocess.run(
                cmd, input=user_input or "", capture_output=True, text=True,
                timeout=self.timeout_seconds, cwd=self.cwd,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"claude CLI timed out after {self.timeout_seconds}s") from exc
        if proc.returncode != 0:
            raise RuntimeError(f"claude CLI failed (exit {proc.returncode}): {proc.stderr[:500]}")
        try:
            envelope = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"claude CLI returned non-JSON stdout: {proc.stdout[:500]}") from exc
        if envelope.get("is_error"):
            raise RuntimeError(f"claude CLI reported error: {str(envelope.get('result'))[:500]}")
        return _Resp(envelope.get("result", "") or "")
