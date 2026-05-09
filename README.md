# ccg - Commit Comment Generator

ステージング済みの変更を LLM に渡し、日本語のコミットメッセージを自動生成する CLI ツールです。

## インストール

お使いの環境に合わせて選択してください。

> **Note:** `ccg` はプロジェクトに関係なく使うツールです。venv に `pip install` した場合は毎回 activate が必要になるため、`pipx` または `uv tool install` を推奨します。

**pipx（推奨）**
```bash
pipx install git+https://github.com/shiroka1125/commit_comment_generate_cli.git
```

**uv**
```bash
uv tool install git+https://github.com/shiroka1125/commit_comment_generate_cli.git
```

**pip**
```bash
pip install git+https://github.com/shiroka1125/commit_comment_generate_cli.git
```

OpenAI または Anthropic を使用する場合は、対応オプションを追加してください。

```bash
pipx install "commit-comment-generate-cli[openai] @ git+https://github.com/shiroka1125/commit_comment_generate_cli.git"
pipx install "commit-comment-generate-cli[anthropic] @ git+https://github.com/shiroka1125/commit_comment_generate_cli.git"
```

## 使い方

### 1. 初回セットアップ

```bash
ccg start
```

使用するLLMプロバイダー・モデル・APIキーを対話形式で設定します。

```
使用するLLMプロバイダーを選択してください:
  1: google_genai  (デフォルトモデル: gemini-2.5-flash)
  2: openai        (デフォルトモデル: gpt-4o)
  3: anthropic     (デフォルトモデル: claude-opus-4-5)
番号 [1]:
モデル名 [gemini-2.5-flash]:
APIキー:
```

APIキーはOSのキーチェーンに安全に保存されます。

### 2. コミットメッセージの生成

変更をステージングしてから実行します。

```bash
git add <files>
ccg generate
```

**出力例:**

```
feat: ユーザー認証機能を追加
・JWTトークンによるセッション管理を実装
・ログイン・ログアウトエンドポイントを追加
・パスワードのbcryptハッシュ化に対応
```

## 対応プロバイダー

| # | プロバイダー | 追加パッケージ |
|---|---|---|
| 1 | Google Gemini | デフォルトで含まれる |
| 2 | OpenAI | `[openai]` オプション |
| 3 | Anthropic Claude | `[anthropic]` オプション |

## コマンド一覧

| コマンド | 説明 |
|---|---|
| `ccg start` | LLMプロバイダーとAPIキーを設定 |
| `ccg generate` | ステージ済み変更からコミットメッセージを生成 |
| `ccg pr` | ベースブランチとの差分からPR descriptionを生成 |

`ccg pr` はデフォルトで `main` ブランチとの差分を使います。別のブランチを指定する場合：

```bash
ccg pr --base develop
```

## ログ

実行ログ（処理時間・レスポンス長・トークン数）は `ccg.log` に出力されます。

## 動作要件

- Python 3.13 以上
- Git
