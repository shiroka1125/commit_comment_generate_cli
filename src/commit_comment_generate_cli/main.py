import logging
import subprocess
import time

import typer
from langchain import chat_models
from langchain.messages import HumanMessage, SystemMessage

from commit_comment_generate_cli.keyring import load_config, save_config

app = typer.Typer()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("ccg.log")],
)

logger = logging.getLogger(__name__)

PROVIDERS: dict[str, tuple[str, str]] = {
    "1": ("google_genai", "gemini-2.5-flash"),
    "2": ("openai", "gpt-4o"),
    "3": ("anthropic", "claude-opus-4-5"),
}


def get_git_diff():
    exclude_patterns = [
        ":(exclude)*.lock",
        ":(exclude)package-lock.json",
        ":(exclude)*.min.js",
        ":(exclude).gitignore",
    ]

    command = ["git", "diff", "--staged", "--", "."] + exclude_patterns

    git_diff_result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout
    return git_diff_result


def get_git_diff_from_base(base_branch: str):
    exclude_patterns = [
        ":(exclude)*.lock",
        ":(exclude)package-lock.json",
        ":(exclude)*.min.js",
        ":(exclude).gitignore",
    ]

    command = ["git", "diff", f"{base_branch}...HEAD", "--", "."] + exclude_patterns

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise ValueError(f"ブランチ '{base_branch}' が見つかりません。")
    return result.stdout


def get_commit_log(base_branch: str):
    result = subprocess.run(
        ["git", "log", f"{base_branch}..HEAD", "--oneline"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def init_chatmodel():
    provider, model, api_key = load_config()
    if not provider or not api_key:
        typer.echo(
            "設定が見つかりません。`ccg start` を実行してAPIキーを設定してください。"
        )
        raise typer.Exit(1)

    llm_client = chat_models.init_chat_model(
        model_provider=provider,
        model=model,
        temperature=0,
        api_key=api_key,
    )
    return llm_client


@app.command()
def start():
    typer.echo("使用するLLMプロバイダーを選択してください:")
    for key, (provider, default_model) in PROVIDERS.items():
        typer.echo(f"  {key}: {provider}  (デフォルトモデル: {default_model})")

    choice = typer.prompt("番号", default="1")
    provider, default_model = PROVIDERS.get(choice, PROVIDERS["1"])
    model = typer.prompt("モデル名", default=default_model)
    api_key = typer.prompt("APIキー", hide_input=True)

    save_config(provider, model, api_key)
    typer.echo(f"設定を保存しました: {provider} / {model}")


@app.command()
def generate():
    try:
        start_time = time.perf_counter()

        git_diff_result = get_git_diff()
        if not git_diff_result:
            print(
                "ファイルがステージされていません。変更をステージング後にこのコマンドを実行してください。"
            )
            return

        llm_client = init_chatmodel()

        prompt = [
            SystemMessage(
                content="""git diffの内容から、適切なコミットメッセージを生成してください。

                            ## 出力形式
                            <type>: <subject>
                            ・<変更点1>
                            ・<変更点2>

                            ## ルール
                            - typeは feat, fix, docs, style, refactor, chore などから選択してください。
                            - 日本語で簡潔に記述してください。"""
            ),
            HumanMessage(content=f"これがgit diffの内容です: \n{git_diff_result}"),
        ]

        response = llm_client.invoke(prompt)
        end_time = time.perf_counter() - start_time
        response_length = len(response.content)
        response_tokens = llm_client.get_num_tokens(response.content)
        logger.info(
            f"処理時間: {end_time:.2f}秒, レスポンス長: {response_length}文字, トークン数: {response_tokens}トークン."
        )
        print(response.content)
    except typer.Exit:
        raise
    except Exception as e:
        print(f"エラーが発生しました: {e}")


@app.command()
def pr(base: str = typer.Option("main", help="比較元のブランチ名")):
    try:
        start_time = time.perf_counter()

        diff = get_git_diff_from_base(base)
        commits = get_commit_log(base)

        if not diff:
            print(f"`{base}` ブランチからの差分がありません。")
            return

        llm_client = init_chatmodel()

        prompt = [
            SystemMessage(
                content="""git diffとコミット履歴をもとに、GitHubのPull RequestのDescriptionを生成してください。

                            ## 出力形式
                            ## 概要
                            （このPRで何をしたかを2〜3文で説明）

                            ## 変更内容
                            ・<変更点1>
                            ・<変更点2>

                            ## ルール
                            - 日本語で記述してください。
                            - 技術的な詳細より、目的や背景を重視してください。"""
            ),
            HumanMessage(
                content=f"## コミット履歴\n{commits}\n\n## git diff\n{diff}"
            ),
        ]

        response = llm_client.invoke(prompt)
        end_time = time.perf_counter() - start_time
        response_length = len(response.content)
        response_tokens = llm_client.get_num_tokens(response.content)
        logger.info(
            f"処理時間: {end_time:.2f}秒, レスポンス長: {response_length}文字, トークン数: {response_tokens}トークン."
        )
        print(response.content)
    except ValueError as e:
        print(f"エラー: {e}")
    except typer.Exit:
        raise
    except Exception as e:
        print(f"エラーが発生しました: {e}")


def main():
    app()
