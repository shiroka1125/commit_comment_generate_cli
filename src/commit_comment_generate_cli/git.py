import subprocess
from pathlib import Path

_DEFAULT_PATTERNS = [
    "*.lock",
    "package-lock.json",
    "*.min.js",
    ".gitignore",
]

_CCGIGNORE = ".ccgignore"


def _load_exclude_pathspecs() -> list[str]:
    ccgignore = Path(_CCGIGNORE)
    if ccgignore.exists():
        patterns = [
            line.strip()
            for line in ccgignore.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
    else:
        patterns = _DEFAULT_PATTERNS
    return [f":(exclude){p}" for p in patterns]


def get_git_diff() -> str:
    command = ["git", "diff", "--staged", "--", "."] + _load_exclude_pathspecs()
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    return result.stdout


def get_git_diff_from_base(base_branch: str) -> str:
    command = ["git", "diff", f"{base_branch}...HEAD", "--", "."] + _load_exclude_pathspecs()
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        raise ValueError(f"ブランチ '{base_branch}' が見つかりません。")
    return result.stdout


def get_commit_log(base_branch: str) -> str:
    result = subprocess.run(
        ["git", "log", f"{base_branch}..HEAD", "--oneline"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout
