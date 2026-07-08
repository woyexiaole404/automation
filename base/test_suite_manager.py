SUITE_DEFINITIONS = {
    "smoke": {
        "modules": ["login", "home", "chat"],
        "description": "快速验证 Open Web 核心链路是否可用。",
    },
    "regression": {
        "modules": ["login", "home", "chat"],
        "description": "当前阶段与 smoke 相同，后续模块增加后扩展。",
    },
    "nightly": {
        "modules": ["login", "home", "chat"],
        "description": "当前阶段与 regression 相同，后续增加长流程和深度测试。",
    },
}


class TestSuiteManager:
    def __init__(self, suite_definitions=None):
        self.suite_definitions = suite_definitions or SUITE_DEFINITIONS

    def list_suites(self):
        return {
            suite_name: {
                "modules": self._deduplicate_modules(definition["modules"]),
                "description": definition.get("description", ""),
            }
            for suite_name, definition in sorted(self.suite_definitions.items())
        }

    def get_suite_modules(self, suite_name):
        suite = self._get_suite_definition(suite_name)
        return self._deduplicate_modules(suite["modules"])

    def get_suite_description(self, suite_name):
        suite = self._get_suite_definition(suite_name)
        return suite.get("description", "")

    def validate_suite(self, suite_name, available_modules):
        suite_modules = self.get_suite_modules(suite_name)
        missing_modules = [
            module for module in suite_modules if module not in available_modules
        ]
        if missing_modules:
            raise ValueError(
                f"Suite '{suite_name}' contains unavailable modules: "
                f"{', '.join(missing_modules)}."
            )
        return suite_modules

    def _get_suite_definition(self, suite_name):
        if suite_name not in self.suite_definitions:
            supported_suites = ", ".join(sorted(self.suite_definitions)) or "none"
            raise ValueError(
                f"Unsupported suite '{suite_name}'. Available suites: {supported_suites}."
            )
        return self.suite_definitions[suite_name]

    def _deduplicate_modules(self, modules):
        unique_modules = []
        seen_modules = set()
        for module in modules:
            if module in seen_modules:
                continue
            unique_modules.append(module)
            seen_modules.add(module)
        return unique_modules
