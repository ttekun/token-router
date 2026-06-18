# Security Policy

## Supported Versions

`token-router` is currently distributed from the `main` branch. Security fixes are applied to the latest public version unless a release branch is explicitly announced.

## Reporting a Vulnerability

Please do not report security vulnerabilities through public GitHub issues.

Use GitHub's private vulnerability reporting feature if it is available on the repository. If private reporting is unavailable, contact the maintainer privately through the GitHub profile contact channel and include a concise description of the issue.

## What To Include

Please include:

- Affected file or feature.
- Minimal reproduction steps.
- Local environment details, such as Python version and Ollama model.
- Whether the issue involves command execution, file disclosure, prompt injection, unsafe fallback output, or secret exposure.

Do not include real API keys, credentials, private logs, customer data, proprietary source code, or other sensitive material. Use sanitized examples whenever possible.

## Scope

Security-sensitive areas include:

- Accidental disclosure of raw file contents in fallback output.
- Handling of logs that may contain secrets.
- Prompt injection attempts inside routed files.
- Unsafe instructions in `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, or other agent-context references.
- Command examples that could encourage destructive behavior.

Out of scope:

- General model quality issues.
- Invalid JSON emitted by a local model, unless it causes unsafe output or data exposure.
- Performance differences between Ollama models.

## Responsible Disclosure

Please give maintainers reasonable time to investigate and publish a fix before publicly disclosing a vulnerability. We will try to acknowledge valid reports within 7 days and provide a remediation plan or status update as soon as practical.
