import subprocess
import time

import typer
from langchain import chat_models
from langchain.messages import AIMessage, HumanMessage, SystemMessage

app = typer.Typer()


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


def init_chatmodel(model: str = "gemini-2.5-flash"):
    llm_client = chat_models.init_chat_model(
        model_provider="google_genai",
        model=model,
        temperature=0,
    )
    return llm_client


@app.callback()
def main():
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
                content="あなたは優れたエンジニアです。git diffの内容を見て、コミットコメントを生成してください。"
            ),
            HumanMessage(content=git_diff_result),
            AIMessage(
                content="""
                            以下の出力例を参考にコミットコメントを生成してください。
                            <type>: <subject>
                            ・<変更点1>
                            ・<変更点2>        
                                """
            ),
        ]

        response = llm_client.invoke(prompt)
        end_time = time.perf_counter() - start_time
        print(f"処理時間: {end_time:.2f}秒")
        return response.content
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None
