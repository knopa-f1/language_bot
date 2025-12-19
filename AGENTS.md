## Purpose

You are helping me work on **language_bot** — a Python Telegram bot deployed via Docker.
Your goal is to make code improvements that are **controlled, minimal, and reviewable**.

This file defines rules, restrictions, and expectations so you don’t break Docker configs, behavior, or introduce risky changes.

---

## Hard Rules (Do NOT break these)

1. **Do not change any Docker-related files** unless I explicitly request it:

   * `Dockerfile`
   * `docker-compose.yml`
   * `.env`, `.env.*`, `.env.example`

2. **Do not add new dependencies** (no new pip packages) unless I explicitly request it.

3. **Do not change user-visible behavior** unless the task clearly says so.

4. **Before editing any code, always output a plan** that includes:

   * what you are going to do
   * which files you plan to modify
   * why the change is low-risk

5. **After making changes, always include verification steps** (commands I can run locally).

6. **Keep diffs small and focused** — one logical change per task.

---

## Required Output Format (for every task)

When proposing or performing changes, strictly follow this structure:

1. **Plan**

   * Short explanation of the approach

2. **Files to change**

   * Exact list of files

3. **Code changes**

   * Diffs or full updated code blocks

4. **How to verify**

   * Commands I should run locally (do not execute them yourself)

Example:

```
Plan:
- Reduce duplication in message handlers

Files to change:
- bot/handlers.py
- bot/utils.py

Code changes:
...

How to verify:
- docker compose up --build
- Send /start to the bot and check logs
```

---

## Safety Constraints

* Reading and inspecting repository files is always allowed and does not require approval.
* **Do not run shell commands** unless I explicitly approve.
* **Do not touch CI/CD configs** unless explicitly requested.
* **Never introduce secrets or tokens** into the codebase — always rely on environment variables.
* **Avoid network calls in tests** — mock external services.

---

## Project Context

* Python Telegram bot
* Async message handlers
* Deployed and run via Docker
* Local development and testing done through Docker Compose

---

## Task Priority Order (when request is vague)

If a task is broad or underspecified, prioritize work in this order:

1. Reduce code duplication
2. Improve readability and naming
3. Add or improve unit tests
4. Improve error handling and logging
5. Add type hints where safe
6. Suggest (but do not implement) architectural changes

---

## Verification Expectations

Every task must include clear local verification steps, for example:

```
docker compose build
docker compose up
```

For tests:

```
docker compose run app pytest
```

Do not execute these commands yourself — only suggest them.

---

## Code Quality Expectations

* Follow existing project style and conventions
* Prefer clarity over abstraction
* Avoid large refactors unless explicitly requested
* Keep changes backward-compatible by default
* If a change affects usage, behavior, configuration, or developer workflow, update the relevant documentation (e.g. README)
* If a change affects logic, add or update tests accordingly

---

## Mental Model

Act as a careful senior engineer:

* cautious with changes
* explicit about risks
* focused on maintainability
* respectful of existing design
