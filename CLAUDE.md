# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This project uses `uv` for package management.

```bash
# Install dependencies
uv sync

# Run the CLI (generates commit message from staged changes)
ccg

# Set up API key interactively
ccg start

# Install in editable mode
uv pip install -e .
```

No test suite exists yet.

## Architecture

A single-command CLI tool that reads `git diff --staged`, sends it to an LLM, and prints a Japanese commit message.

**Entry point**: `ccg` → `commit_comment_generate_cli.main:main` (defined as `@app.callback()` in typer)

### Key files

- `src/commit_comment_generate_cli/main.py` — Typer app, CLI command handlers (`start`, `generate`, `pr`), logging setup
- `src/commit_comment_generate_cli/git.py` — Git operations: `get_git_diff()`, `get_git_diff_from_base()`, `get_commit_log()`
- `src/commit_comment_generate_cli/llm.py` — `PROVIDERS` config, `init_chatmodel()` via LangChain
- `src/commit_comment_generate_cli/keyring.py` — API key storage/retrieval via OS keyring

### Flow

1. `main()` runs `app()` (Typer)
2. `get_git_diff()` / `get_git_diff_from_base()` in `git.py` runs the appropriate `git diff`, excluding lock files
3. `init_chatmodel()` in `llm.py` loads provider/model/key from keyring, then initializes via `langchain.chat_models.init_chat_model`
4. A `SystemMessage` + `HumanMessage` prompt is sent; the response is printed
5. Processing time, response length, and token count are logged to `ccg.log` (gitignored)

### API key storage

Keys are stored in the OS keyring. `ccg start` prompts for and saves the key. `keyring.py` exposes `save_config()` and `load_config()`.

### Commit message format (prompt output)

```
<type>: <subject>
・<変更点1>
・<変更点2>
```

Types follow conventional commits (`feat`, `fix`, `docs`, `style`, `refactor`, `chore`). Output is in Japanese.
