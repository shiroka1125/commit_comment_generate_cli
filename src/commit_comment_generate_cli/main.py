import logging
import time

import typer
from langchain.messages import HumanMessage, SystemMessage

from commit_comment_generate_cli.git import get_commit_log, get_git_diff, get_git_diff_from_base
from commit_comment_generate_cli.keyring import save_config
from commit_comment_generate_cli.llm import PROVIDERS, init_chatmodel

app = typer.Typer()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("ccg.log")],
)
logger = logging.getLogger(__name__)


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

        git_diff = get_git_diff()
        if not git_diff:
            print("ファイルがステージされていません。変更をステージング後にこのコマンドを実行してください。")
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
            HumanMessage(content=f"これがgit diffの内容です: \n{git_diff}"),
        ]

        response = llm_client.invoke(prompt)
        elapsed = time.perf_counter() - start_time
        logger.info(
            f"処理時間: {elapsed:.2f}秒, レスポンス長: {len(response.content)}文字, "
            f"トークン数: {llm_client.get_num_tokens(response.content)}トークン."
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
        if not diff:
            print(f"`{base}` ブランチからの差分がありません。")
            return

        commits = get_commit_log(base)
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
            HumanMessage(content=f"## コミット履歴\n{commits}\n\n## git diff\n{diff}"),
        ]

        response = llm_client.invoke(prompt)
        elapsed = time.perf_counter() - start_time
        logger.info(
            f"処理時間: {elapsed:.2f}秒, レスポンス長: {len(response.content)}文字, "
            f"トークン数: {llm_client.get_num_tokens(response.content)}トークン."
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
