from pathlib import Path


class DataManager:
    """统一测试数据读取入口。"""

    DATA_ROOT = Path(__file__).resolve().parent.parent / "data"

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
        return value

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

    @classmethod
    def get_data(cls, project, module):
        data_path = cls.DATA_ROOT / project / f"{module}.yaml"
        if not data_path.is_file():
            raise FileNotFoundError(f"Test data file not found: {data_path}")

        try:
            import yaml
        except ImportError:
            return cls._load_simple_yaml(data_path)

        with data_path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}
