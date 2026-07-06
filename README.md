# saas 自动化测试项目

## 项目介绍

这是一个 Python 自动化测试项目，当前代码包含三类测试脚本：

- Selenium UI 自动化测试
- requests API 测试脚本
- minium 小程序自动化测试

项目使用 `unittest` 作为主要测试框架，并内置 `BeautifulReport` 用于生成 HTML 测试报告。页面操作基础能力集中在 `base/`，页面对象集中在 `page_object/`，测试脚本集中在 `test_case/`。

## 环境要求

当前项目会访问真实测试环境、接口地址、数据库和本机浏览器环境。运行前需要确认：

- 已安装 Python。
- 已安装 Chrome 浏览器。
- Selenium UI 用例需要可用的 ChromeDriver。
- API 测试需要目标接口网络可达。
- 数据库相关能力需要 MySQL 网络可达。
- 小程序测试需要 minium 运行环境和微信开发者工具配置。

注意：部分 UI 测试中仍保留 Windows 本机 ChromeDriver 路径 `D:\Python310\chromedriver.exe`，当前阶段未处理该路径。

## Python版本

项目代码中没有声明固定 Python 版本，也没有 `pyproject.toml`、`setup.py` 或 `requirements.txt`。

从现有缓存文件和代码使用情况看，项目曾在 Python 3.10 和 Python 3.12 环境下运行或编译过。建议优先使用 Python 3.10+。

本机如果没有 `python` 命令，可以使用 `python3`。

## 安装依赖

项目当前没有依赖清单文件。根据实际代码 import，至少需要安装以下第三方依赖：

```bash
pip install selenium requests ddddocr pymysql minium lxml pytest certifi urllib3
```

如果使用 `python3`：

```bash
python3 -m pip install selenium requests ddddocr pymysql minium lxml pytest certifi urllib3
```

依赖来源说明：

- `selenium`：浏览器 UI 自动化。
- `requests`：接口请求。
- `ddddocr`：验证码图片识别。
- `pymysql`：MySQL 数据读取。
- `minium`：微信小程序自动化。
- `lxml`：BeautifulReport 测试样例中解析 HTML。
- `pytest`：`BeautifulReport/BeautifulReport.py` 中有导入。
- `certifi`、`urllib3`：`test_case/api.py` 中有导入。

## 运行方式

### 运行默认 BeautifulReport 入口

默认入口是 `test_case/run.py`，当前默认执行 `test_shanghu.py`：

```bash
cd /Users/woyexiaole/saas/test_case
python run.py
```

如果当前环境没有 `python`：

```bash
cd /Users/woyexiaole/saas/test_case
python3 run.py
```

注意：该入口会运行真实测试，可能启动浏览器、访问外部页面，并生成 HTML 报告。

### 运行单个 unittest 测试文件

可从项目根目录执行：

```bash
cd /Users/woyexiaole/saas
python -m unittest test_case.test_shanghu
python -m unittest test_case.test_xinlian
python -m unittest test_case.test_lhcz
python -m unittest test_case.test_yichuang
python -m unittest test_case.test_api
```

如果当前环境没有 `python`，使用 `python3 -m unittest ...`。

### 运行 API 调试脚本

`test_case/api.py` 不是 unittest 用例，是直接发起请求并打印结果的脚本：

```bash
cd /Users/woyexiaole/saas
python test_case/api.py
```

### 运行小程序测试

小程序测试文件：

- `test_case/test.py`
- `test_case/test_tuizhanggui.py`

它们继承 `minium.MiniTest`，相关配置在：

```text
test_case/config.json
```

当前配置中包含 Windows 本机路径，需要在实际运行环境中保证 minium 和微信开发者工具配置可用。

## BeautifulReport生成方式

`test_case/run.py` 使用以下流程生成报告：

1. 使用 `unittest.defaultTestLoader.discover(".", pattern=py_name)` 收集测试。
2. 使用 `BeautifulReport(suite_tests)` 包装测试套件。
3. 调用 `report(description=b, filename=filename, log_path=report_path)`。
4. `BeautifulReport.report()` 内部执行 unittest suite。
5. 测试结束后读取 `BeautifulReport/template/template`。
6. 将测试结果写入 HTML 文件。

核心调用位置：

```python
BeautifulReport(suite_tests).report(description=b, filename=filename, log_path=report_path)
```

历史报告文件位于 `report/`。

## 截图位置

当前截图位置由 `base/project_path.py` 统一生成。

主要位置：

```text
img/
img/step/
img/code/
test_case/img/
```

用途：

- `test_case/img/`：失败截图，主要由 `save_img()` 保存。
- `img/step/`：步骤截图，主要由 `test_shanghu.py` 保存。
- `img/code/`：验证码图片，主要由 `get_yzm()` 保存。
- `img/`：部分步骤截图，例如 `test_xinlian.py` 的 `step_img()`。

截图写入后，部分测试会调用 `BeautifulReport.img2base()` 转为 base64，并通过 `print()` 将图片 HTML 写入 BeautifulReport 日志。

## 报告位置

BeautifulReport HTML 报告输出到：

```text
report/
```

报告文件名由 `test_case/run.py` 根据测试类型前缀和当前时间生成，例如：

```text
shanghu2023-03-24 18：46：01.html
```

当前项目中已有历史报告文件保存在 `report/`。

## 目录说明

```text
BeautifulReport/
```

项目内置报告工具。`BeautifulReport.py` 实现 unittest 结果收集、HTML 报告生成和截图嵌入。

```text
base/
```

基础能力目录：

- `base.py`：数据库连接、数据库操作工具、Selenium 页面基础方法。
- `project_path.py`：项目根目录、报告目录、截图目录、日志目录路径工具。

```text
data/
```

测试数据读取目录。当前 `mysql_data.py` 用于从 MySQL 查询短信验证码。

```text
page_object/
```

Page Object 目录。当前 `index_page.py` 中定义 `shanghu` 页面对象，封装登录和“我的应用”入口操作。

```text
test_case/
```

测试脚本目录：

- `run.py`：unittest + BeautifulReport 主入口。
- `test_shanghu.py`：商户后台 UI 测试。
- `test_xinlian.py`：C 端相关 UI 测试。
- `test_lhcz.py`：联合成长相关 UI 测试。
- `test_yichuang.py`：SaaS 页面 UI 测试。
- `test_api.py`：unittest API 测试。
- `api.py`：直接执行的 API 调试脚本。
- `test.py`：minium 小程序测试。
- `test_tuizhanggui.py`：minium 小程序测试。
- `config.json`：minium/微信开发者工具配置。

```text
img/
```

测试截图目录。

```text
report/
```

HTML 测试报告目录。

```text
config/
```

当前为空目录。

## 新增测试脚本流程

### 新增 UI 测试

1. 在 `test_case/` 下新增 `test_*.py` 文件。
2. 使用 `unittest.TestCase` 编写测试类。
3. 在 `setUp()` 中创建 Selenium driver。
4. 在 `tearDown()` 中关闭 driver。
5. 页面通用操作优先使用 `BasePage`。
6. 如果是可复用页面流程，优先在 `page_object/` 中增加或复用页面对象。
7. 如需进入 BeautifulReport 主入口，需要在 `test_case/run.py` 中调用对应文件名。

### 新增 API 测试

1. 在 `test_case/` 下新增 `test_*.py` 文件。
2. 使用 `unittest.TestCase`。
3. 使用 `requests` 发起请求。
4. 使用 unittest 断言校验响应。
5. 避免写成导入即执行的脚本，除非明确只是调试脚本。

### 新增小程序测试

1. 在 `test_case/` 下新增 `test_*.py` 文件。
2. 测试类继承 `minium.MiniTest`。
3. 确认 `test_case/config.json` 中的小程序项目路径和微信开发者工具路径可用。
4. 使用 minium 提供的 `self.page`、`self.app` 操作小程序。

## 常见问题

### 1. `python: command not found`

当前环境可能只有 `python3` 命令。可以改用：

```bash
python3 -m unittest test_case.test_shanghu
python3 test_case/run.py
```

### 2. ChromeDriver 路径不可用

部分 UI 测试中仍保留：

```text
D:\Python310\chromedriver.exe
```

这通常只适用于原 Windows 本机环境。当前阶段未工程化 ChromeDriver 路径。

### 3. 运行 UI 测试会打开真实浏览器

UI 测试的 `setUp()` 会创建 Chrome 浏览器实例，测试会访问真实 URL。运行前请确认浏览器、驱动和网络环境可用。

### 4. 报告没有生成

检查：

- 是否通过 `test_case/run.py` 入口运行。
- `report/` 目录是否存在或可写。
- 测试是否在启动前因依赖缺失、ChromeDriver 不可用等问题中断。

### 5. 截图没有出现在报告中

当前截图嵌入依赖测试中的 `save_img()` 保存图片后，再调用 `BeautifulReport.img2base()` 转 base64，并通过 `print()` 输出 HTML。若截图路径、文件名或保存时机不一致，报告中可能无法显示截图。

### 6. 数据库连接失败

`base/base.py` 中数据库连接参数写在代码里。运行涉及 `MysqlData.get_code()` 的流程时，需要确保数据库地址、账号、密码、网络都可用。

### 7. API 测试失败

`test_case/test_api.py` 请求的是固定接口地址，并带有固定 Authorization。接口不可达、Token 失效、数据不存在或环境变化都会导致失败。

### 8. 小程序测试无法启动

检查：

- 是否安装 minium。
- 是否安装微信开发者工具。
- `test_case/config.json` 中 `project_path` 是否存在。
- `dev_tool_path` 是否指向可执行的微信开发者工具 CLI。

### 9. `api.py` 和 `test_api.py` 有什么区别

- `test_api.py` 是 `unittest` 测试文件。
- `api.py` 是直接执行的 API 调试脚本，运行文件时会立即发起请求。

### 10. 可以直接用 pytest 吗

当前测试类主要继承 `unittest.TestCase`，历史缓存中能看到 pytest 收集痕迹，但项目没有 pytest 配置文件。默认建议按 unittest 和 `test_case/run.py` 方式运行。
