import os
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"


def _parse_scalar(value):
    value = value.strip()
    if value in ("", "null", "None"):
        return None
    if value.startswith(("'", '"')) and value.endswith(("'", '"')):
        return value[1:-1]
    if value.isdigit():
        return int(value)
    return value


def _to_int(value, default=None):
    if value in (None, ""):
        return default
    return int(value)


def _load_simple_yaml(path):
    data = {}
    stack = [(-1, data)]
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, _, value = line.strip().partition(":")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value.strip():
            parent[key] = _parse_scalar(value)
        else:
            child = {}
            parent[key] = child
            stack.append((indent, child))
    return data


def load_config():
    if not CONFIG_PATH.exists():
        return {}
    try:
        import yaml
    except ImportError:
        return _load_simple_yaml(CONFIG_PATH)
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_config_value(path, env_var=None, default=None):
    if env_var:
        env_value = os.environ.get(env_var)
        if env_value not in (None, ""):
            return env_value

    value = load_config()
    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return default if value in (None, "") else value


def get_database_config():
    return {
        "host": get_config_value("database.host", "DB_HOST"),
        "port": _to_int(get_config_value("database.port", "DB_PORT", 3306), 3306),
        "user": get_config_value("database.user", "DB_USER"),
        "password": get_config_value("database.password", "DB_PASSWORD"),
        "name": get_config_value("database.name", "DB_NAME"),
        "charset": get_config_value("database.charset", "DB_CHARSET", "utf8"),
    }


def get_ui_account(name):
    prefix = name.upper()
    return {
        "username": get_config_value(f"ui.{name}.username", f"{prefix}_USERNAME"),
        "password": get_config_value(f"ui.{name}.password", f"{prefix}_PASSWORD"),
    }


def get_web_base_url():
    return get_config_value("web.base_url", "WEB_BASE_URL", "http://localhost:3000/auth")


def get_account(role="default"):
    env_prefix = role.upper()
    return {
        "email": get_config_value(f"accounts.{role}.email", f"{env_prefix}_ACCOUNT_EMAIL"),
        "password": get_config_value(f"accounts.{role}.password", f"{env_prefix}_ACCOUNT_PASSWORD"),
    }


def get_default_account():
    return get_account("default")


def get_default_invalid_password():
    return get_config_value(
        "accounts.default.invalid_password",
        "DEFAULT_ACCOUNT_INVALID_PASSWORD",
        "INVALID_TEST_PASSWORD",
    )


def get_api_config():
    return {
        "authorization": get_config_value("api.authorization", "API_AUTHORIZATION"),
        "clientauthorization": get_config_value("api.clientauthorization", "API_CLIENTAUTHORIZATION"),
        "ad_preference": get_config_value("api.ad_preference", "API_AD_PREFERENCE"),
    }


def get_retry_config():
    return {
        "count": _to_int(get_config_value("retry.count", "RETRY_COUNT", 0), 0),
        "interval_seconds": _to_int(
            get_config_value("retry.interval_seconds", "RETRY_INTERVAL_SECONDS", 10),
            10,
        ),
    }
