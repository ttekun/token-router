# Token Router Benchmark Report

Date: 2026-06-02

## Summary

`token-router` was benchmarked against three synthetic workloads: a sparse infra log, a legacy source file with an explicit bug marker, and a keywordless structural source file. The router also now includes regression coverage for `agent_context`, a static instruction-reference routing mode for long routeable agent context files. Primary benchmark workloads routed successfully without fallback, and `ollama ps` was empty afterward, confirming the model did not remain resident after execution.

Token counts are estimates using `chars / 4`.

## Environment

- Skill: `token-router`
- Script: `scripts/router.py`
- Model: `gemma4:e2b-it-q4_K_M`
- Runtime:
  - `OLLAMA_NUM_CTX=4096`
  - `OLLAMA_KEEP_ALIVE=0s`
  - `ROUTER_TIMEOUT=60`

## Results

| Case | Mode | Lines | Full File Est. Tokens | Router Output Est. Tokens | Reduction | Time | Fallback |
|---|---|---:|---:|---:|---:|---:|---|
| Sparse infra log | `error_log` | 2,000 | 41,711 | 131 | 99.69% | 5.37s | No |
| Legacy bug source | `heavy_code` | 2,155 | 7,520 | 70 | 99.06% | 4.46s | No |
| Keywordless structural source | `heavy_code` | 504 | 4,188 | 48 | 98.85% | 6.13s | No |

## Regression Harness

Latest mock regression suite:

```text
[OK] query pass-through locates token expiration
[OK] overlap merge and output cap
[OK] streaming log tail finds late error
[OK] multi-word query terms are shown in prompt
[OK] error_log cap keeps latest ranges
[OK] agent_context query routes deployment approval
[OK] agent_context query routes frontend testing
[OK] agent_context no query keeps mandatory rules in prompt
[OK] agent_context output cap preserves early mandatory rules
[OK] agent_context fallback preview uses instruction keywords
```

## Real Smoke Checks

- `heavy_code --query "token expiration timeout logic"` selected the token expiration timestamp lines while exposing `[Query Terms]`.
- Forced streaming `error_log --query "payment timeout"` returned raw late-log candidate lines through deterministic fallback when the local model omitted `targets`.
- `agent_context --query "frontend testing"` selected the frontend testing workflow section from a routeable instruction-reference fixture.
- `ollama ps` was empty after smoke runs.

## Caveat

These metrics prove context reduction and routing mechanics on controlled fixtures. They do not prove correctness for every production incident. For high-stakes debugging, treat router output as a first pass and expand nearby lines when the cloud model detects missing dependencies.

For static agent instructions, `agent_context` does not reduce the cost of a long root instruction file after it has already been auto-injected into a session. The recommended architecture is a compact always-on root file plus longer routeable reference files that are pulled through the router only when task-relevant.
