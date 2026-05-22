import pytest
import typer
from unittest.mock import patch, MagicMock

from commit_comment_generate_cli.llm import init_chatmodel, PROVIDERS


@pytest.mark.parametrize("provider,model", PROVIDERS.values())
def test_init_chatmodel_calls_init_chat_model(provider, model):
    fake_key = "fake-api-key"
    with patch("commit_comment_generate_cli.llm.load_config", return_value=(provider, model, fake_key)), \
         patch("commit_comment_generate_cli.llm.chat_models.init_chat_model") as mock_init:
        mock_init.return_value = MagicMock()
        init_chatmodel()
        mock_init.assert_called_once_with(
            model_provider=provider,
            model=model,
            temperature=0,
            api_key=fake_key,
        )


def test_init_chatmodel_exits_when_no_provider():
    with patch("commit_comment_generate_cli.llm.load_config", return_value=(None, None, None)):
        with pytest.raises(typer.Exit):
            init_chatmodel()


def test_init_chatmodel_exits_when_no_api_key():
    with patch("commit_comment_generate_cli.llm.load_config", return_value=("google_genai", "gemini-2.5-flash", None)):
        with pytest.raises(typer.Exit):
            init_chatmodel()
