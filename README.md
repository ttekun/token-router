# token-router

<!-- Badge placeholders -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Ollama](https://img.shields.io/badge/Ollama-local%20routing-black)
![Codex Skill](https://img.shields.io/badge/OpenAI%20Codex-skill-green)

**Lossless local line routing for massive logs and source files before they reach a cloud reasoning model.**

`token-router` is a Codex skill and standalone Python router that uses a local Ollama model to identify exact line ranges in oversized files, then returns the raw, unmodified slices to a high-reasoning cloud model such as GPT-5.5, o3, or another AI coding agent.

## Executive Summary

Large logs and legacy source files are expensive context. Sending a 2,000+ line deployment log or monolithic source file directly to a cloud LLM can waste tokens, increase latency, and exhaust budgets before the model reaches the evidence that matters.

`token-router` solves this with a hybrid separation-of-concerns architecture:

- **Local model for search and triage:** Gemma 4 via Ollama runs on the user's machine and scans large files for relevant line coordinates.
- **Cloud model for reasoning:** GPT-5.5, o3, or another cloud model receives only raw high-density evidence slices and applies deep reasoning where it matters.
- **No lossy summarization:** The local model does not rewrite, summarize, or interpret code. It emits JSON line ranges; the router then extracts exact raw text from the original file.

The result is aggressive context reduction without degrading the technical evidence available to the reasoning model.

## Architecture & Core Philosophy

### Separation Of Concerns

`token-router` deliberately splits the workflow into two specialized phases:

| Phase | Engine | Responsibility | Output |
|---|---|---|---|
| Search / Triage | Local Ollama model | Find relevant line coordinates | JSON ranges |
| Evidence Extraction | Router script | Slice original file by line number | Raw unedited text |
| Reasoning | Cloud LLM / Codex | Debug, explain, patch, or review | High-confidence answer |

This prevents the local model from becoming an unreliable summarizer. The local model is a router, not the analyst.

### Lossless Line Routing

Summarizing source code or logs through a smaller local model is lossy. A single dropped stack frame, config key, indentation detail, or error suffix can change the diagnosis.

`token-router` avoids that failure mode:

1. The file is scanned locally.
2. The local model returns line coordinates.
3. The Python script slices the original file directly.
4. The cloud model receives raw text exactly as it appeared on disk.

The selection step can be imperfect, but the extracted evidence itself is lossless. If the cloud model needs more context, it can request wider line ranges instead of hallucinating around omitted dependencies.

## Features & Context Safety Guardrails

- **Two routing modes**
  - `error_log`: optimized for logs, stack traces, CI output, and deployment failures.
  - `heavy_code`: optimized for long source files and localized code investigations.
- **Query pass-through**
  - Use `--query "token expiration"` to bias routing toward user intent.
  - Multi-word queries are tokenized and exposed as `[Query Terms]` so the local model can match any relevant term, not only the full phrase.
- **Deterministic prefilters**
  - Log mode uses keyword and tail-window scanning.
  - Code mode prioritizes query hits, then suspicious code markers, then structural head/tail previews.
- **Lossless raw slicing**
  - Router output is copied from the original file by line number.
- **Output caps**
  - `ROUTER_MAX_OUTPUT_LINES` bounds cloud-visible raw text.
  - In `error_log` mode, newer log ranges survive first when the cap is exceeded.
- **Memory safety**
  - `OLLAMA_KEEP_ALIVE=0s` unloads the model immediately after routing.
  - `OLLAMA_NUM_CTX=4096` or `8192` bounds local context pressure.
- **Regression harness**
  - Fixture-based tests catch prompt, line-selection, cap, and fallback regressions.

## Benchmark Highlights

Token counts are estimated with `chars / 4` and should be treated as directional rather than billing-exact.

| Case | Mode | Est. Input Tokens | Router Output Tokens | Reduction | Time |
|---|---|---:|---:|---:|---:|
| Sparse infra log | `error_log` | 41,711 | 131 | 99.69% | 5.37s |
| Legacy bug source | `heavy_code` | 7,520 | 70 | 99.06% | 4.46s |
| Keywordless structural source | `heavy_code` | 4,188 | 48 | 98.85% | 6.13s |

See [docs/benchmark-report.md](docs/benchmark-report.md) for methodology, caveats, and regression results.

## Quick Start

### Prerequisites

- Python 3.10+
- Ollama installed and running
- A local routing model, defaulting to:

```bash
ollama pull gemma4:e2b-it-q4_K_M
```

### Run Against A Large Log

```bash
OLLAMA_NUM_CTX=4096 OLLAMA_KEEP_ALIVE=0s \
python3 scripts/router.py error_log path/to/deploy.log --query "database migration timeout"
```

### Run Against A Long Source File

```bash
OLLAMA_NUM_CTX=4096 OLLAMA_KEEP_ALIVE=0s \
python3 scripts/router.py heavy_code path/to/service.py --query "token expiration"
```

### Use As A Codex Skill

Install or copy this repository into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R token-router ~/.codex/skills/token-router
```

Then invoke it naturally:

```text
Use $token-router to analyze this large log with query "payment timeout".
```

## Configuration

| Variable | Default | Purpose |
|---|---:|---|
| `OLLAMA_MODEL` | `gemma4:e2b-it-q4_K_M` | Local model used for line routing |
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Ollama generate endpoint |
| `OLLAMA_NUM_CTX` | `8192` | Local model context window |
| `OLLAMA_KEEP_ALIVE` | `0s` | Unload model immediately after routing |
| `ROUTER_TIMEOUT` | `120` | Ollama request timeout in seconds |
| `ROUTER_MAX_CHARS` | `120000` | Maximum line-numbered content sent to Ollama |
| `ROUTER_MAX_OUTPUT_LINES` | `160` | Maximum raw lines returned to the cloud model |
| `ROUTER_STREAM_THRESHOLD_BYTES` | `5000000` | File size threshold for streaming log prefiltering |
| `ROUTER_LOG_CONTEXT_LINES` | `6` | Log context lines around keyword/query hits |
| `ROUTER_LOG_TAIL_LINES` | `200` | Tail lines preserved for large logs |
| `ROUTER_CODE_CONTEXT_LINES` | `8` | Code context lines around query/keyword hits |

## Regression Tests

Run the fast mock-based test suite:

```bash
python3 scripts/run_router_tests.py tests/router-tests.json
```

Run against the real local model only when you intentionally want to exercise Ollama:

```bash
python3 scripts/run_router_tests.py tests/router-tests.json --real
```

## When To Use vs When To Bypass

| Situation | Use `token-router`? | Rationale |
|---|---|---|
| Massive deployment logs | Yes | Error evidence is usually localized and recent |
| CI logs with stack traces | Yes | Keyword and tail scanning preserve high-value ranges |
| Long files with a specific bug or query | Yes | `--query` and code markers narrow routing safely |
| Legacy files with `TODO`, `FIXME`, `raise`, or `assert` markers | Yes | Code keyword windows are highly effective |
| Broad architecture review | Bypass | The model needs global context, not narrow slices |
| Refactor planning across many modules | Bypass or combine manually | Local routing may hide cross-file relationships |
| Security-sensitive code requiring complete audit | Bypass | Completeness matters more than token reduction |
| Very dense source files where every section matters | Bypass | Context reduction can remove necessary dependencies |

## Design Caveats

`token-router` is lossless in extraction, not omniscient in selection. If a selected range is too narrow, the cloud model should request nearby or broader line ranges. The intended workflow is iterative: route, reason, expand when needed.

## License

MIT License. See [LICENSE](LICENSE).
