from pathlib import Path


PROJECT_MARKERS = ("BeautifulReport", "base", "test_case")


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for parent in (current, *current.parents):
        if parent.name == "saas" and all((parent / marker).exists() for marker in PROJECT_MARKERS):
            return parent
        if all((parent / marker).exists() for marker in PROJECT_MARKERS):
            return parent
    return current.parent


PROJECT_ROOT = _find_project_root()

REPORT_DIR = PROJECT_ROOT / "report"
IMG_DIR = PROJECT_ROOT / "img"
IMG_STEP_DIR = IMG_DIR / "step"
IMG_CODE_DIR = IMG_DIR / "code"
LOG_DIR = PROJECT_ROOT / "logs"
TEST_CASE_IMG_DIR = PROJECT_ROOT / "test_case" / "img"
TEST_CASE_OUTPUTS_DIR = PROJECT_ROOT / "test_case" / "outputs"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_project_dirs() -> None:
    for path in (
        REPORT_DIR,
        IMG_DIR,
        IMG_STEP_DIR,
        IMG_CODE_DIR,
        LOG_DIR,
        TEST_CASE_IMG_DIR,
        TEST_CASE_OUTPUTS_DIR,
    ):
        ensure_dir(path)


def project_root() -> str:
    return str(PROJECT_ROOT)


def report_path() -> Path:
    return ensure_dir(REPORT_DIR)


def report_dir() -> str:
    return str(report_path())


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


def test_case_outputs_dir() -> str:
    return str(ensure_dir(TEST_CASE_OUTPUTS_DIR))


def test_case_img_dir() -> str:
    return str(ensure_dir(TEST_CASE_IMG_DIR))


def test_case_img_file(file_name: str) -> str:
    return str(ensure_dir(TEST_CASE_IMG_DIR) / file_name)


ensure_project_dirs()
