# Contributing to token-router

Thank you for helping improve `token-router`.

This project is a lossless local line router for large logs, source files, and routeable agent-context references. Contributions are most useful when they preserve that design: the local model should route line coordinates, not summarize or rewrite evidence.

## Good Contribution Areas

- Routing quality improvements for `error_log`, `heavy_code`, or `agent_context`.
- Better deterministic prefilters and fallback behavior.
- Model compatibility notes for Ollama models.
- Regression fixtures for malformed JSON, unusual logs, long `CLAUDE.md` / `AGENTS.md` files, or non-English content.
- Documentation for Codex, Claude Code, and terminal-agent workflows.

## Model Reliability Notes

The default model is optimized for low local resource usage:

```bash
OLLAMA_MODEL=gemma4:e2b-it-q4_K_M
```

Very small local models can occasionally emit invalid JSON, especially with complex logs, unusual symbols, or dense instruction files. If you see JSON parsing failures, please try a larger routing model before filing a routing-quality bug:

```bash
OLLAMA_MODEL=qwen2.5-coder:7b python3 scripts/router.py error_log path/to/file.log --query "timeout"
```

Other users have reported lower JSON error rates with larger coder-oriented models such as `qwen2.5-coder:7b` or 4B-class Gemma variants when VRAM is available. Please include the exact `OLLAMA_MODEL`, quantization tag, and command output when reporting model-specific behavior.

## Local Validation

Run these before opening a pull request:

```bash
python3 -m py_compile scripts/router.py scripts/run_router_tests.py
python3 scripts/run_router_tests.py tests/router-tests.json
```

If you are changing the Codex skill metadata, also run:

```bash
python3 /path/to/quick_validate.py .
```

If `quick_validate.py` cannot import `yaml`, install or expose `PyYAML` in your local Python environment and rerun it.

## Pull Request Guidelines

- Keep changes focused.
- Add or update tests for routing behavior changes.
- Do not add secrets, private logs, customer data, or proprietary source code to fixtures.
- Prefer small synthetic fixtures that reproduce the behavior.
- Document any new environment variables in `README.md` and `SKILL.md`.
- Preserve backward compatibility for:

```bash
python3 scripts/router.py error_log <file>
python3 scripts/router.py heavy_code <file>
python3 scripts/router.py agent_context <file>
```

## Reporting Bugs

Please use the bug report issue template and include:

- Mode: `error_log`, `heavy_code`, or `agent_context`
- `OLLAMA_MODEL`
- `OLLAMA_NUM_CTX`
- `OLLAMA_KEEP_ALIVE`
- Whether the failure is invalid JSON, poor line selection, fallback behavior, or output-cap behavior
- A minimal sanitized fixture or reproduction command

Do not paste private production logs or credentials into public issues.
