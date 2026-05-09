import keyring

_USERNAME = "user"
_PROVIDER_SERVICE = "CCG_PROVIDER"
_MODEL_SERVICE = "CCG_MODEL"


def save_config(provider: str, model: str, api_key: str):
    keyring.set_password(_PROVIDER_SERVICE, _USERNAME, provider)
    keyring.set_password(_MODEL_SERVICE, _USERNAME, model)
    keyring.set_password(f"CCG_{provider.upper()}_API_KEY", _USERNAME, api_key)


def load_config() -> tuple[str | None, str | None, str | None]:
    provider = keyring.get_password(_PROVIDER_SERVICE, _USERNAME)
    model = keyring.get_password(_MODEL_SERVICE, _USERNAME)
    api_key = keyring.get_password(f"CCG_{provider.upper()}_API_KEY", _USERNAME) if provider else None
    return provider, model, api_key
