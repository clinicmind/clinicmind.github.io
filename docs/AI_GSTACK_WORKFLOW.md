# gstack-inspired AI workflow — pilot

Source: https://github.com/garrytan/gstack (digest reviewed: v1.91.95.0, 2026-10-13).
This file defines **workflow guidance**, not proof of a gstack binary installation.

## Scope and precedence
- Applies to this repository's AI-assisted work only.
- Follow user instructions, repository-specific constraints and safety requirements first.
- Never auto-deploy, auto-merge or push to the default branch. Use a feature branch and draft PR.
- Do not access or commit secrets, credentials, private case information, user uploads or databases.
- Preserve existing behavior unless the issue explicitly authorizes changes. Keep diffs small.

## Workflow
1. **Understand** — State the goal, desired user-visible outcome, constraints and acceptance tests; inspect existing code/docs.
2. **Reuse first** — Check existing helpers, standard library, platform primitives, and existing dependencies before introducing code or packages. Ask before any new dependency.
3. **Plan** — For nontrivial changes, identify minimum viable scope, risks and rollback. Prefer a small verifiable task to a broad refactor.
4. **Implement** — Make isolated, focused edits. Do not mix content research changes with technical refactors.
5. **Review** — Inspect the actual diff for correctness, accessibility, security, regression risk, maintainability, and unnecessary complexity.
6. **QA** — Run available repository-native tests. For UI changes, test navigation, keyboard, mobile layout, broken links and console errors if browser testing is available. Clearly distinguish tested from untested claims.
7. **Release** — Draft PR with summary, evidence, risks, rollback notes and relevant screenshots; user controls merge and deployment.
8. **Learn** — Record recurring pitfalls and actionable follow-up in the project handoff.

## gstack role mapping
- Product strategy: `/office-hours`, `/plan-ceo-review` (or equivalent structured questions).
- Architecture: `/plan-eng-review`.
- Design and accessibility: `/plan-design-review`, `/design-review`.
- Code review: `/review`; tests: `/test-audit`; QA: `/qa-only` before repair, `/qa` when a safe fixture exists.
- Release: `/ship` recommendations are advisory only; **no auto-merges or deployments**.
- Learning: `/retro`, `/learn` only on authorized, non-sensitive records.

## Environment
Full gstack requires a compatible Claude Code / Codex CLI runtime and Bun, Git; Codex is listed as experimental in upstream docs. This repository guide does not install those runtimes. On a machine with suitable tools, assess `./setup --host codex` and `./setup --host claude` separately. Review install scripts and permissions before execution. Avoid the auto-update team mode until approved.

## Project constraints
- Source facts in health, psychology and policy content; separate verified sources from interpretation.
- Never invent research results, medical advice, citations, test output, deployment status or passing checks.
- For public-facing clinical resources: include accessibility, readability and privacy review.
