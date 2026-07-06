from pathlib import Path


def _find_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name == "saas":
            return parent
    return current.parents[1]


PROJECT_ROOT = _find_project_root()

REPORT_DIR = PROJECT_ROOT / "report"
IMG_DIR = PROJECT_ROOT / "img"
IMG_STEP_DIR = IMG_DIR / "step"
IMG_CODE_DIR = IMG_DIR / "code"
LOG_DIR = PROJECT_ROOT / "test_case" / "outputs"
TEST_CASE_IMG_DIR = PROJECT_ROOT / "test_case" / "img"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def report_dir() -> str:
    return str(ensure_dir(REPORT_DIR))


def img_dir() -> str:
    return str(ensure_dir(IMG_DIR))


def img_file(file_name: str) -> str:
    return str(ensure_dir(IMG_DIR) / file_name)


def img_step_file(file_name: str) -> str:
    return str(ensure_dir(IMG_STEP_DIR) / file_name)


def img_code_file(file_name: str) -> str:
    return str(ensure_dir(IMG_CODE_DIR) / file_name)


def log_dir() -> str:
    return str(ensure_dir(LOG_DIR))


def test_case_img_dir() -> str:
    return str(ensure_dir(TEST_CASE_IMG_DIR))


def test_case_img_file(file_name: str) -> str:
    return str(ensure_dir(TEST_CASE_IMG_DIR) / file_name)
