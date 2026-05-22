import typer
from langchain import chat_models

from commit_comment_generate_cli.keyring import load_config

PROVIDERS: dict[str, tuple[str, str]] = {
    "1": ("google_genai", "gemini-2.5-flash"),
    "2": ("openai", "gpt-4o"),
    "3": ("anthropic", "claude-opus-4-5"),
}


def init_chatmodel():
    provider, model, api_key = load_config()
    if not provider or not api_key:
        typer.echo("設定が見つかりません。`ccg start` を実行してAPIキーを設定してください。")
        raise typer.Exit(1)

    return chat_models.init_chat_model(
        model_provider=provider,
        model=model,
        temperature=0,
        api_key=api_key,
    )
