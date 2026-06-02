---
name: token-router
description: Route oversized logs and source files through a local Ollama model to identify relevant line ranges before analysis. Use when Codex needs to analyze massive error logs, stack traces, or source files over roughly 300 lines while preserving token budget; trigger on requests such as "optimize tokens for this log", "look at this big file and fix errors using local router", "router analyze file", "로컬 라우터로 분석해줘", or "토큰 최적화 라우터로 봐줘".
---

# Token Router

## Overview

Use this skill to reduce cloud context load for large logs or source files. A local Ollama model selects likely line ranges, and `scripts/router.py` returns raw, unedited slices from the original file.

## Workflow

1. For large logs, stack traces, or source files, run the router before loading the whole file:

```bash
python3 scripts/router.py <mode> <PATH_TO_TARGET_FILE>
```

Pass the user question when it contains useful domain terms:

```bash
python3 scripts/router.py heavy_code path/to/file.py --query "token expiration"
```

The router tokenizes multi-word queries and shows both the full query and individual query terms to the local model.

2. Choose `error_log` for logs or stack traces. This mode first narrows the local-model prompt to keyword-matched candidate windows while preserving original line numbers. Large logs use a streaming keyword/tail scan before calling Ollama. Choose `heavy_code` for long source files; this mode prioritizes `--query` matches, then code keyword windows, then a head/tail plus structural-line preview.
3. Analyze only the returned raw slices. The local model is a line-number router, not a summarizer.
4. If the returned slice is too narrow, rerun the router or inspect a larger nearby range directly.
5. Do not assume unseen surrounding code. Ask for or retrieve more context before making claims that depend on omitted lines.

## Script Configuration

The router defaults to the locally installed `gemma4:e2b-it-q4_K_M` model at `http://localhost:11434/api/generate`.

- `OLLAMA_MODEL`: override the model name.
- `OLLAMA_URL`: override the Ollama generate endpoint.
- `ROUTER_TIMEOUT`: request timeout in seconds; defaults to `120` for the local `gemma4:e2b-it-q4_K_M` model.
- `ROUTER_MAX_CHARS`: maximum line-numbered content sent to the local model.
- `ROUTER_STREAM_THRESHOLD_BYTES`: file-size threshold where `error_log` switches to streaming keyword/tail prefiltering.
- `ROUTER_LOG_CONTEXT_LINES`: surrounding lines included around each log keyword hit in `error_log` mode.
- `ROUTER_LOG_TAIL_LINES`: tail lines included for large `error_log` files.
- `ROUTER_CODE_CONTEXT_LINES`: surrounding lines included around each code keyword hit in `heavy_code` mode.
- `ROUTER_MAX_OUTPUT_LINES`: maximum raw lines returned to Codex after model-selected ranges are merged. In `error_log` mode, newer log ranges are preserved first when this cap is exceeded.
- `OLLAMA_NUM_CTX`: local model context window; defaults to `8192` to reduce memory pressure.
- `OLLAMA_KEEP_ALIVE`: Ollama model residency after a request; defaults to `0s` so the model unloads instead of lingering in memory.

If Ollama is unavailable or returns invalid JSON, use the fallback keyword/preview output only as a starting point and retrieve additional raw ranges as needed.

## Regression Tests

Run the fast mock-based regression suite after changing prompts, model defaults, or routing logic:

```bash
python3 scripts/run_router_tests.py tests/router-tests.json
```

Use `--real` only when you intentionally want to call the local Ollama model.
