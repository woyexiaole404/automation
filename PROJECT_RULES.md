# 项目长期维护规则

## 项目修改原则

1. 每次只解决一个明确问题，避免把无关清理、重构和功能修改混在一起。
2. 默认保持当前项目风格：`unittest` 测试结构、`BeautifulReport` 报告入口、`BasePage` 公共操作、`page_object` 页面对象分层。
3. 修改必须基于当前代码实际情况，不虚构不存在的模块、配置或运行入口。
4. 优先做低风险、小范围、可验证的改动。
5. 不主动改变现有业务流程、测试步骤、断言语义和测试覆盖范围。
6. 新增说明文档、依赖清单、路径工具等维护性文件时，应说明来源和适用范围。

## 重大框架修改确认规则

任何涉及以下内容的修改，都必须先输出设计方案，等待用户确认后才能实施：

1. 框架目录结构
2. `test_case/run.py` 运行入口
3. `BasePage`
4. `DriverManager`
5. `Config` 配置中心
6. Page Object 设计规范
7. 测试发现规则
8. BeautifulReport 集成方式
9. Git 分支/Tag 流程
10. CI/CD 配置

## Git 工作流

1. 所有开发默认在 `develop` 分支进行。
2. `main` 分支只保存稳定版本，不直接在 `main` 上进行日常开发。
3. 每完成一个功能必须依次执行：

```bash
git status
git add <本次功能相关文件>
git commit
```

4. 提交前确认没有混入无关文件、本地缓存和运行产物。
5. 功能验证稳定后再执行 `push`。
6. 重要版本使用 Git Tag 标记。
7. 每次提交只聚焦一个主题，提交说明应写清楚修改目的和验证方式。

建议提交类型：

```text
docs: update project documentation
test: update automation tests
chore: improve framework or project tooling
```

## 测试范围

1. 默认测试范围仅为：

```text
test_case/open_web/
```

2. `archive/` 目录永远不参与默认测试发现和默认测试执行。
3. 默认运行入口为：

```bash
python3 test_case/run.py
```

4. 不要为了验证单个页面或单个模块而运行全部测试。

## 测试执行规则

### 修改单个模块

修改单个 Page Object 或对应测试文件时，例如：

- `login_page.py`
- `test_login.py`

只运行对应模块测试：

```bash
python3 test_case/run.py --module login
```

不要运行整个项目。

### 修改 Open Web 多个页面

同时修改 Dashboard、User、Order 等多个 Open Web 页面或其测试时，执行：

```bash
python3 test_case/run.py
```

该命令用于 Open Web 回归测试。

### 修改公共框架

修改下列公共能力时：

- `BasePage`
- `DriverManager`
- `Config`
- `run.py`
- `WaitManager`

先执行：

```bash
python3 -m compileall .
```

再执行：

```bash
python3 test_case/run.py
```

### Git 提交前

提交 Git 前统一执行：

```bash
python3 test_case/run.py
```

确认 Open Web 全部测试通过后再提交。

## 新功能开发

新增 UI 自动化功能必须遵循以下流程，不得跳过任何步骤：

```text
Page Object
    ↓
Test Case
    ↓
Run
    ↓
BeautifulReport
    ↓
Git Commit
```

1. 页面定位器和业务操作放在对应 Page Object 中。
2. 测试步骤和断言放在对应 Test Case 中。
3. 通过统一运行入口执行测试。
4. 确认 BeautifulReport 正常生成并检查结果。
5. 验证通过后进行 Git Commit。

## BasePage 原则

1. 所有 Open Web 页面必须复用 `base/base.py` 中的 `BasePage`。
2. Page Object 优先调用 BasePage 提供的等待、点击、输入、文本读取、URL 获取和截图等公共方法。
3. 不得在测试用例中大量编写 Selenium 原生操作。
4. 通用 Selenium 操作应先沉淀到 BasePage，再由 Page Object 复用。
5. 页面等待优先使用显式等待，不新增固定 `time.sleep()`。

## AI（Codex）执行规则

1. 默认不要在用户未明确要求时自动修改代码。
2. 开始任务前必须阅读 `FRAMEWORK.md`；涉及运行方式、依赖或项目说明时，同时阅读 `CODEX_GUIDE.md` 和 `README.md`。
3. 修改前先确认任务范围，只处理用户指定的问题。
4. 不确定是否属于重构时，按重构处理，先等待用户确认。
5. 标准工作流程为：

```text
分析
  ↓
修改
  ↓
验证
  ↓
停止
  ↓
等待用户确认
```

6. 完成验证后停止，不进行无限循环修改。
7. 最终输出必须说明：
   - 修改了哪些文件。
   - 为什么修改。
   - 如何验证。
   - 是否存在未完成或无法验证的事项。

## AI 修改限制

1. 单次任务最多修改 5 个文件。
2. 单次任务最多运行测试 3 次。
3. 测试连续失败时立即停止，不继续反复修改或重跑。
4. 连续失败后必须输出：
   - 当前失败原因。
   - 已尝试的方法。
   - 下一步建议。
5. 输出失败信息后停止，等待用户确认。
6. 不允许因为本机环境不可用而修改测试逻辑绕过失败。

## 禁止事项

除非用户明确要求，否则禁止：

1. 删除历史项目或历史测试资产。
2. 修改 `archive/` 目录。
3. 修改旧商户后台业务。
4. 修改旧 API 测试。
5. 修改旧小程序测试。
6. 删除任何测试用例。
7. 修改既有业务流程、测试步骤或断言语义。
8. 未经确认进行重构、替换测试框架或替换报告框架。
9. 把账号、密码、Token、数据库连接等敏感信息扩散到新文件。
10. 把 `api.py` 等直接执行脚本当作普通可导入模块调用。

## 配置安全规则

1. 新增文件时不要复制、扩散或重新整理敏感值。
2. 文档中只描述敏感信息存在的位置和风险，不重复写具体值。
3. 配置外置化必须分阶段进行，并保持当前测试入口兼容。
4. `.env`、本机私有配置、真实 Token 文件不应提交到仓库。
5. 数据库或外部服务配置的调整不得直接改变现有查询和业务行为。
