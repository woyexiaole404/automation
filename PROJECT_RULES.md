# 项目长期维护规则

## 项目修改原则

1. 每次只解决一个明确问题，避免把无关清理、重构和功能修改混在一起。
2. 默认保持当前项目风格：`unittest` 测试结构、`BeautifulReport` 报告入口、`BasePage` 公共操作、`page_object` 页面对象分层。
3. 修改必须基于当前代码实际情况，不虚构不存在的模块、配置或运行入口。
4. 优先做低风险、小范围、可验证的改动。
5. 不主动改变现有业务流程、测试步骤、断言语义和测试用例覆盖范围。
6. 新增说明文档、依赖清单、路径工具等维护性文件时，应说明来源和适用范围。

## Codex 工作规则

1. 每次开始工作必须先阅读 `FRAMEWORK.md`。
2. 涉及运行方式、依赖、项目说明时，同时参考 `README.md` 和 `CODEX_GUIDE.md`。
3. 修改前先确认任务范围，只处理用户指定的问题。
4. 不确定是否属于重构时，按重构处理，必须先询问。
5. 如果预计或实际修改超过 10 个文件，必须停止并说明原因。
6. 输出结论时必须说明：
   - 修改了哪些文件。
   - 为什么修改。
   - 如何验证。
7. 不运行真实测试，除非用户明确要求。真实测试包括启动浏览器、访问外部站点、连接数据库、调用真实 API。

## 禁止事项

1. 不允许修改目录结构。
2. 不允许删除任何测试用例。
3. 不允许未经确认修改业务流程。
4. 不允许未经确认做重构。
5. 不允许把账号、密码、Token、数据库连接等敏感信息扩散到新文件。
6. 不允许在未确认的情况下替换测试框架、报告框架或自动化工具。
7. 不允许把 `api.py` 这类直接执行脚本当作普通可导入模块随意调用。
8. 不允许因为本机环境不可用就改动测试逻辑绕过失败。

## 每次修改后的验证要求

1. 修改完成后必须执行：

```bash
python -m compileall .
```

2. 如果当前环境没有 `python` 命令，可以补充执行：

```bash
python3 -m compileall .
```

3. 如果用户明确要求使用 `python3`，执行：

```bash
python3 -m compileall .
```

4. 编译检查只验证 Python 语法，不代表 UI、API、小程序测试通过。
5. 如果没有运行真实测试，必须明确说明没有启动浏览器、没有连接数据库、没有调用真实接口。

## Git 提交规范

1. 每次提交聚焦一个主题。
2. 提交前查看变更范围，确认没有混入无关文件。
3. 不提交本地缓存和运行产物，例如 `__pycache__`、`.DS_Store`、临时日志、临时截图。
4. 文档类提交建议使用：

```text
docs: update project documentation
```

5. 依赖类提交建议使用：

```text
chore: add requirements file
```

6. 测试维护类提交建议使用：

```text
test: update automation test maintenance
```

7. 路径、配置、运行入口等工程化提交建议使用：

```text
chore: improve project path handling
```

8. 提交说明应写清楚验证方式，例如是否执行过 `python3 -m compileall .`。

## UI 自动化维护规则

1. UI 自动化测试当前主要位于：
   - `test_case/test_shanghu.py`
   - `test_case/test_xinlian.py`
   - `test_case/test_lhcz.py`
   - `test_case/test_yichuang.py`
2. 公共浏览器页面操作优先复用 `base/base.py` 中的 `BasePage`。
3. 可复用页面流程优先放入 `page_object/`，当前实际存在的页面对象是 `page_object/index_page.py` 中的 `shanghu`。
4. 不随意修改登录流程、页面跳转顺序和断言目标。
5. 不随意删除 `save_img()`、`step_img()`、`get_yzm()`、`draw_yzm()` 等截图和验证码相关方法。
6. ChromeDriver 路径仍有历史硬编码，后续工程化必须保持原有运行方式兼容。
7. 固定等待 `time.sleep()` 和绝对 XPath 可以作为后续优化点，但优化前应单独评估风险。
8. UI 测试会启动真实浏览器并访问真实地址，默认不要在维护任务中直接运行。

## API 自动化维护规则

1. API 自动化相关文件当前包括：
   - `test_case/test_api.py`
   - `test_case/api.py`
2. `test_case/test_api.py` 是 `unittest` 测试文件。
3. `test_case/api.py` 是直接执行的 API 调试脚本，运行时会立即发起 HTTP 请求。
4. 不随意修改接口地址、请求头、Token、请求体和断言。
5. 不把真实 API 调用作为默认验证步骤。
6. 如需新增 API 测试，优先使用 `unittest.TestCase`，避免导入即执行。
7. 涉及 `verify=False`、Authorization、clientauthorization 等内容时，只做必要范围内维护，避免扩大敏感信息暴露。

## 配置安全规则

1. 当前项目中存在硬编码账号、密码、Token、数据库连接、外部 URL 和本机路径。
2. 新增文件时不要复制、扩散或重新整理敏感值。
3. 文档中只描述敏感信息存在的位置和风险，不重复写具体值。
4. 后续配置外置化必须分阶段进行，并保持当前测试入口兼容。
5. `.env`、本机私有配置、真实 Token 文件不应提交到仓库。
6. 小程序配置当前位于 `test_case/config.json`，其中包含本机路径；修改前应确认运行环境和 minium 使用方式。
7. 数据库连接当前位于 `base/base.py`；任何外置化改造都必须先确认，不直接改变查询行为。
