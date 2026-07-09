from pathlib import Path
from copy import deepcopy


class dualmethod:
    def __init__(self, method):
        self.method = method

    def __get__(self, instance, owner):
        target = instance if instance is not None else owner.default()

        def wrapper(*args, **kwargs):
            return self.method(target, *args, **kwargs)

        return wrapper


class TestDataManager:
    """Project-wide test data manager backed by config/test_data.yaml."""

    DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "config" / "test_data.yaml"
    _default_manager = None

    def __init__(self, data_path=None):
        self.data_path = Path(data_path) if data_path else self.DEFAULT_DATA_PATH
        self._cache = None

    @classmethod
    def default(cls):
        if cls._default_manager is None:
            cls._default_manager = cls()
        return cls._default_manager

    @dualmethod
    def get_account(self, name):
        return self.get(f"accounts.{name}")

    @dualmethod
    def get_accounts(self):
        return self.get("accounts")

    @dualmethod
    def get_chat_data(self, name):
        return self.get(f"chat.{name}")

    @dualmethod
    def get_search_data(self, name):
        return self.get(f"search.{name}")

    @dualmethod
    def get_workspace_data(self, name):
        return self.get(f"workspace.{name}")

    @dualmethod
    def get_model_data(self, name):
        return self.get(f"model.{name}")

    @dualmethod
    def get(self, path):
        return self._get(path)

    @dualmethod
    def exists(self, path):
        return self._exists(path)

    @dualmethod
    def list_keys(self, section):
        return self._list_keys(section)

    @dualmethod
    def reload(self):
        return self._reload()

    def _get(self, path):
        value = self._resolve_path(path)
        return deepcopy(value)

    def _exists(self, path):
        try:
            self._resolve_path(path)
        except (FileNotFoundError, KeyError):
            return False
        return True

    def _list_keys(self, section):
        value = self._resolve_path(section)
        if not isinstance(value, dict):
            raise KeyError(
                f"Test data section '{section}' is not a mapping. Available keys: none"
            )
        return sorted(value.keys())

    def _reload(self):
        self._cache = self._load()
        return deepcopy(self._cache)

    def _data(self):
        if self._cache is None:
            self._cache = self._load()
        return self._cache

    def _load(self):
        if not self.data_path.is_file():
            raise FileNotFoundError(
                f"Test data file not found: {self.data_path}. "
                "Copy config/test_data.yaml.example to config/test_data.yaml."
            )

        try:
            import yaml
        except ImportError:
            data = self._load_simple_yaml(self.data_path)
        else:
            with self.data_path.open("r", encoding="utf-8") as file:
                data = yaml.safe_load(file) or {}

        if not isinstance(data, dict):
            raise ValueError(f"Test data root must be a mapping: {self.data_path}")
        return data

    def _resolve_path(self, path):
        keys = self._split_path(path)
        value = self._data()
        traversed = []

        for key in keys:
            if not isinstance(value, dict) or key not in value:
                missing_path = ".".join(traversed + [key])
                available_keys = sorted(value.keys()) if isinstance(value, dict) else []
                raise KeyError(
                    f"Test data not found: {missing_path}. "
                    f"Available keys: {', '.join(available_keys) or 'none'}"
                )
            value = value[key]
            traversed.append(key)

        return value

    def _split_path(self, path):
        if not isinstance(path, str) or not path.strip():
            raise KeyError("Test data path must be a non-empty string. Available keys: none")
        return [part.strip() for part in path.split(".") if part.strip()]

    @classmethod
    def _load_simple_yaml(cls, data_path):
        data = {}
        stack = [(-1, data)]

        for raw_line in data_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.split("#", 1)[0].rstrip()
            if not line.strip():
                continue

            indent = len(line) - len(line.lstrip(" "))
            key, _, value = line.strip().partition(":")
            while stack and indent <= stack[-1][0]:
                stack.pop()

            parent = stack[-1][1]
            if value.strip():
                parent[key] = cls._parse_scalar(value)
            else:
                child = {}
                parent[key] = child
                stack.append((indent, child))

        return data

    @staticmethod
    def _parse_scalar(value):
        value = value.strip()
        if value in ("true", "True"):
            return True
        if value in ("false", "False"):
            return False
        if value in ("", "null", "None"):
            return None
        if value.startswith(("'", '"')) and value.endswith(("'", '"')):
            return value[1:-1]
        if value.isdigit():
            return int(value)
        return value
