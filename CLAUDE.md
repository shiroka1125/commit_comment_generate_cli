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

- `src/commit_comment_generate_cli/main.py` — CLI commands, git diff extraction, LLM prompt, logging
- `src/commit_comment_generate_cli/keyring.py` — API key storage/retrieval via OS keyring

### Flow

1. `main()` (the default callback) runs on every `ccg` invocation
2. `get_git_diff()` runs `git diff --staged`, excluding lock files and `.gitignore`
3. `init_chatmodel()` initializes via `langchain.chat_models.init_chat_model` — currently hardcoded to `google_genai` / `gemini-2.5-flash`; the active branch (`adapt_to_any_llm`) is extending this to support arbitrary providers
4. A `SystemMessage` + `HumanMessage` prompt is sent; the response is printed
5. Processing time, response length, and token count are logged to `ccg.log` (gitignored)

### API key storage

Keys are stored in the OS keyring under service `LLM_API_KEY` / username `user` by default. `ccg start` prompts for and saves the key. `keyring.py` exposes `get_keyring`, `set_keyring_password`, and `delete_keyring_password`.

### Commit message format (prompt output)

```
<type>: <subject>
・<変更点1>
・<変更点2>
```

Types follow conventional commits (`feat`, `fix`, `docs`, `style`, `refactor`, `chore`). Output is in Japanese.
