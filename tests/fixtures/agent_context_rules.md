---
name: example-agent-context
router_mode: agent_context
---

# Agent Operating Context

Always preserve user-owned worktree changes before editing files.
Never expose secrets, credentials, tokens, or private keys in responses.
Do not run destructive git commands unless the user explicitly asks for them.

## Frontend Testing Workflow

For frontend work, verify the rendered UI before reporting completion.
Run the local dev server when the application needs one.
Use viewport checks for desktop and mobile before final delivery.

## Deployment Approval

Deployment requires approval from the release owner.
The deployment workflow must validate migrations before pushing.
Always record the target environment and rollback command.

## Database Migration Rules

Database migrations must be reversible unless a documented exception exists.
Verify migration ordering before running integration tests.
Never edit generated migration history by hand.

## Archive

This section is intentionally lower priority for most queries.
