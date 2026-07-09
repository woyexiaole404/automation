# 项目框架说明

## 一、项目整体架构

当前项目是一个 Python 自动化测试项目，主要由 Selenium UI 自动化、requests 接口脚本、minium 小程序自动化脚本，以及内置的 BeautifulReport HTML 报告工具组成。

目录树：

```text
saas/
├── BeautifulReport/
│   ├── BeautifulReport.py
│   ├── __init__.py
│   ├── README.md
│   ├── LICENSE
│   ├── img/
│   ├── sample/
│   │   ├── sample.py
│   │   ├── img/
│   │   └── 测试报告.html
│   ├── template/
│   │   └── template
│   └── tests/
│       └── test_make_report.py
├── base/
│   ├── base.py
│   └── project_path.py
├── config/
├── data/
│   └── mysql_data.py
├── img/
│   ├── code/
│   └── step/
├── page_object/
│   └── index_page.py
├── report/
│   └── shanghu*.html
└── test_case/
    ├── api.py
    ├── config.json
    ├── run.py
    ├── test.py
    ├── test_api.py
    ├── test_lhcz.py
    ├── test_shanghu.py
    ├── test_tuizhanggui.py
    ├── test_xinlian.py
    ├── test_yichuang.py
    ├── img/
    └── outputs/
```

目录作用：

- `BeautifulReport/`：项目内置的 HTML 测试报告库。`BeautifulReport.py` 实现 unittest 结果收集、stdout/stderr 捕获、HTML 模板写入和截图 base64 嵌入。
- `base/`：基础能力层。`base.py` 包含数据库连接、数据库操作工具和 Selenium 页面基础操作封装；`project_path.py` 提供项目根目录和输出目录路径工具。
- `config/`：当前为空目录。
- `data/`：测试数据读取层，目前只有 `mysql_data.py`，用于从 MySQL 查询短信验证码。
- `img/`：测试过程截图目录，当前包含 `step/` 步骤截图和 `code/` 验证码图片目录。
- `page_object/`：Page Object 层，目前只有 `index_page.py`，封装商户端登录和“我的应用”页面入口操作。
- `report/`：BeautifulReport 生成的历史 HTML 报告目录。
- `test_case/`：测试脚本目录，包含 UI 测试、API 测试、小程序测试、测试入口脚本和运行配置。

## 二、测试执行流程

主入口是 `test_case/run.py`。

执行路径：

1. `run.py` 导入 `unittest`、`datetime`、`BeautifulReport` 和 `base.project_path.report_dir`。
2. `run(py_name)` 根据传入文件名设置报告文件名前缀和报告描述：
   - `test_shanghu.py` -> `shanghu`，`商户后台测试用例`
   - `test_xinlian.py` -> `xinlian`，`C端测试用例`
   - `test_houtai.py` -> `houtai`，`管理后台测试用例`
   - `test_case.py` -> `case`，`心链项目测试用例`
3. 使用 `unittest.defaultTestLoader.discover(".", pattern=py_name, top_level_dir=None)` 从当前目录发现匹配的测试文件。
4. 使用 `report_dir()` 获取项目内 `report/` 输出路径。
5. 根据当前时间拼接 HTML 报告文件名。
6. 调用 `BeautifulReport(suite_tests).report(description=b, filename=filename, log_path=report_path)`。

BeautifulReport 生成流程：

1. `BeautifulReport.report()` 接收 `description`、`filename`、`log_path`。
2. 如果传入 `filename`，自动补 `.html` 后缀。
3. 保存报告标题和输出目录。
4. 执行 `self.suites.run(result=self)`，即直接运行 unittest suite。
5. `ReportTestResult.startTest()` 在每个用例开始时重定向 stdout/stderr。
6. 用例执行过程中 `print()` 输出会进入报告日志。
7. 成功、失败、错误、跳过分别由 `addSuccess()`、`addFailure()`、`addError()`、`addSkip()` 收集。
8. `stopTestRun()` 汇总通过数、失败数、错误数、跳过数、总耗时和每条用例结果。
9. `output_report()` 读取 `BeautifulReport/template/template`，把 `var resultData` 替换为本次测试结果 JSON，并写出 HTML 报告。

Selenium 启动流程：

- Selenium UI 测试文件的测试类继承 `unittest.TestCase`。
- `test_shanghu.py`、`test_xinlian.py`、`test_lhcz.py` 在 `setUp()` 中通过 `Service(r'D:\Python310\chromedriver.exe')` 创建 ChromeDriver 服务，再调用 `webdriver.Chrome(service=path)`。
- `test_yichuang.py` 在 `setUp()` 中创建 `webdriver.ChromeOptions()`，添加 `--start-maximized`，再调用 `webdriver.Chrome(options=self.options)`。
- 各测试在 `tearDown()` 中调用 `self.driver.quit()` 关闭浏览器。

截图保存流程：

- `test_shanghu.py`：
  - `save_img(img_name)` 保存失败截图到 `test_case/img/`。
  - 保存后调用 `BeautifulReport.img2base(self.img_path, img_name + now + '.png')` 转为 base64。
  - 使用 `HTML_IMG_TEMPLATE` 打印 `<img>` HTML，BeautifulReport 会把 print 内容收进报告。
  - `step_img(img_name)` 保存步骤截图到 `img/step/`。
  - `get_yzm()` 保存验证码图片到 `img/code/`。
- `test_xinlian.py`：
  - `save_img(img_name)` 保存失败截图到 `test_case/img/` 并打印 base64 图片 HTML。
  - `step_img(img_name)` 保存步骤截图到 `img/`。
- `test_lhcz.py` 和 `test_yichuang.py`：
  - `get_yzm(self)` 保存验证码图片到 `img/code/`。
  - `draw_yzm(self)` 从同一路径读取验证码图片并交给 `ddddocr` 识别。

数据库读取流程：

1. `data/mysql_data.py` 中的 `MysqlData.get_code(mobile)` 构造 SQL。
2. 调用 `base.base.Tool.select(sql, mobile)`。
3. `Tool.select()` 调用 `connect_mysql()`。
4. `connect_mysql()` 使用 `pymysql.Connect(...)` 连接 MySQL。
5. `cursor.execute(sql, args=args)` 执行查询。
6. `cursor.fetchall()` 获取结果。
7. 关闭连接。
8. `MysqlData.get_code()` 返回第一行第一列验证码。

当前代码里 `test_shanghu.py` 引入了 `MysqlData`，但获取验证码的调用处是注释状态。

页面对象调用流程：

1. 测试用例实例化页面对象，例如 `shanghu(self.driver)`。
2. `shanghu` 继承 `BasePage`，复用 `go_url()`、`click_element()`、`send_element()` 等基础操作。
3. `shanghu.login(username, passwd)` 打开登录页，点击登录方式图片，输入账号密码，点击登录按钮。
4. `shanghu.wodeyingyong(username, passwd)` 先调用 `self.login(username, passwd)`，再点击侧边栏“我的应用”相关入口。
5. 测试用例再使用 `BasePage(self.driver).get_txt(xpath)` 读取页面文本并断言。

## 三、Base 模块说明

`base/base.py` 包含三类能力：数据库连接、数据库操作工具、Selenium 页面基础操作。

数据库连接：

- `connect_mysql()` 使用 `pymysql.Connect()` 创建连接。
- 连接参数在代码中直接写死，包括 host、port、user、passwd、db、charset。
- 返回 `connect` 对象。

数据库工具：

- `Tool.select(sql, args)`：
  - 创建数据库连接。
  - 获取 cursor。
  - 执行 SQL。
  - `fetchall()` 获取所有结果。
  - 关闭连接。
  - 返回结果。
- `Tool.update(sql)`：
  - 创建数据库连接。
  - 执行 update SQL。
  - `commit()` 提交。
  - `fetchone()` 获取结果。
  - 关闭连接。
  - 返回结果。

`BasePage`：

- 构造函数接收 Selenium `driver` 并保存为 `self.driver`。
- 当前代码中浏览器启动不在 `BasePage` 内完成，而是在各测试类的 `setUp()` 中完成。
- `BasePage` 只负责基于已有 driver 做页面操作。

公共方法：

- 地址与浏览器：
  - `driver_url()`：返回当前 URL。
  - `go_url(url)`：打开 URL。
  - `refresh()`：刷新页面。
  - `maximize()`：最大化窗口。
- 元素查找与操作：
  - `find(xpath, by=By.XPATH)`：默认 XPath 查找元素。
  - `click_id_element(element_id)`：按 ID 点击。
  - `click_css_element(css)`：按 CSS 点击。
  - `click_element(xpath)`：按 XPath 点击。
  - `send_element(xpath, input_txt)`：输入文本。
  - `clear_element(xpath)`：清空输入框。
  - `clear_backspace(xpath)`：通过 Ctrl+A 和 Backspace 清空。
  - `click_js(xpath)`：通过 JavaScript 点击。
- 页面滚动：
  - `scroll_bottom_page()`：滚动到底部。
  - `scroll_top_page()`：滚动到顶部。
  - `scroll_page(step_length)`：按指定像素滚动。
- frame 和窗口：
  - `switch_frame(xpath)`：切入 iframe。
  - `switch_default()`：回到默认上下文。
  - `get_handles()`：获取窗口句柄。
  - `switch_to_handles(handles)`：切换窗口。
- 鼠标悬浮：
  - `mouse_hover(xpath)`：XPath 元素悬浮。
  - `mouse_hover_id(element_id)`：ID 元素悬浮。
  - `mouse_hover_css(css)`：CSS 元素悬浮。
- 文本与属性：
  - `get_txt(xpath)`：读取 `textContent`。
  - `get_elements_num(value)`：返回 XPath 匹配元素数量。
  - `checkbox_status(xpath)`：读取勾选状态。
  - `get_attribute_value(xpath, key)`：读取元素属性。

`base/project_path.py`：

- `_find_project_root()` 从当前文件路径向上查找名为 `saas` 的目录。
- 提供项目内路径常量：
  - `PROJECT_ROOT`
  - `REPORT_DIR`
  - `IMG_DIR`
  - `IMG_STEP_DIR`
  - `IMG_CODE_DIR`
  - `LOG_DIR`
  - `TEST_CASE_IMG_DIR`
- `ensure_dir(path)` 会创建目录并返回路径。
- 提供 `report_dir()`、`img_dir()`、`img_file()`、`img_step_file()`、`img_code_file()`、`log_dir()`、`test_case_img_dir()`、`test_case_img_file()` 等路径函数。

`base/test_data_manager.py`：

- v5.3.0 新增的企业级测试数据管理入口。
- 默认读取 `config/test_data.yaml`，示例文件为 `config/test_data.yaml.example`。
- `config.yaml` 继续负责环境配置，例如 base URL、数据库、浏览器、CI secret 映射和 retry；`test_data.yaml` 只负责测试输入数据，两者职责不混用。
- 首次读取 YAML 后缓存在 manager 实例中，后续读取直接使用缓存。
- `reload()` 会重新读取 YAML 并刷新缓存。
- 支持点路径读取：
  - `TestDataManager.get("accounts.admin")`
  - `TestDataManager.get("chat.question_normal")`
  - `TestDataManager.get("workspace.workspace_default")`
- 支持专用便捷接口：
  - `get_account(name)`
  - `get_accounts()`
  - `get_chat_data(name)`
  - `get_search_data(name)`
  - `get_workspace_data(name)`
  - `get_model_data(name)`
  - `get(path)`
  - `exists(path)`
  - `list_keys(section)`
  - `reload()`
- 可按业务 section 横向扩展，例如 `search`、`workspace`、`knowledge`、`model`、`settings`；新增 section 不需要修改 `TestDataManager` 架构，可直接通过 `get("section.key")` 读取。
- 当路径不存在时抛出 `KeyError`，错误信息会包含当前层级的 `Available keys`，便于排查数据命名错误。

## 四、Page Object 设计

当前 `page_object/` 下只有一个页面对象文件：`index_page.py`。

`page_object/index_page.py`：

- 定义类 `shanghu(BasePage)`。
- 继承 `BasePage` 后直接复用基础页面操作方法。

页面对象方法：

- `login(self, username, passwd)`：
  - 打开 `http://t.webmerchant.baishouopen.com/#/login`。
  - 点击登录页中的图片元素。
  - 输入用户名。
  - 输入密码。
  - 点击登录按钮。
  - 每个关键步骤之间使用 `time.sleep()` 等待。
- `wodeyingyong(self, username, passwd)`：
  - 先调用 `self.login(username, passwd)`。
  - 点击侧边栏第一个菜单。
  - 点击子菜单进入“我的应用”页面。

调用关系：

```text
test_case/test_shanghu.py
test_case/test_xinlian.py
        │
        ├── shanghu(self.driver).login(...)
        │       └── BasePage.go_url/click_element/send_element
        │
        └── shanghu(self.driver).wodeyingyong(...)
                ├── shanghu.login(...)
                └── BasePage.click_element(...)
```

当前没有多个页面对象之间的相互调用；`shanghu.wodeyingyong()` 只调用同一个对象内的 `login()`。

## 五、test_case

`test_case/run.py`：

- unittest + BeautifulReport 的主运行入口。
- 默认执行 `run("test_shanghu.py")`。
- 根据文件名设置报告名称和描述。
- 生成 HTML 报告到 `report/`。

`test_case/test_shanghu.py`：

- 类型：UI 自动化。
- 框架：`unittest` + Selenium + BeautifulReport。
- 页面对象：调用 `page_object.index_page.shanghu`。
- 用例：
  - `test_01_login`：正确账号密码登录成功。
  - `test_02_login`：错误密码登录失败。
  - `test_03_wodeyingyong`：打开“我的应用”页面。
- 包含失败截图、步骤截图、验证码截图和 OCR 方法。
- 引入了 `MysqlData`，但实际获取验证码调用处是注释状态。

`test_case/test_xinlian.py`：

- 类型：UI 自动化。
- 框架：`unittest` + Selenium + BeautifulReport。
- 页面对象：调用 `page_object.index_page.shanghu`。
- 用例：
  - `test_01_login1`：正确账号密码登录成功。
- 包含失败截图和步骤截图。

`test_case/test_lhcz.py`：

- 类型：UI 自动化。
- 框架：`unittest` + Selenium + ddddocr。
- 直接使用 `BasePage` 操作页面，没有使用 `page_object`。
- 访问 `http://t.qf.baiopen.top/#/login`。
- 截取验证码图片，使用 `ddddocr` 识别，输入用户名、密码、验证码并断言页面文本。

`test_case/test_yichuang.py`：

- 类型：UI 自动化。
- 框架：`unittest` + Selenium + ddddocr。
- 直接使用 `BasePage` 操作页面，没有使用 `page_object`。
- 访问 `https://plus.xiwshijieheping.com/`。
- 执行登录、进入应用后台、搜索应用、进入编辑页面、切换组件列表等流程。
- 断言文本中包含预期值。

`test_case/test_api.py`：

- 类型：API 自动化。
- 框架：`unittest` + requests。
- 用例 `test_chuangjian`：
  - 构造 Authorization 请求头。
  - 请求 `http://192.168.5.9:2800/prod/product/delete`。
  - 使用 `requests.session().delete(...)`。
  - 断言响应文本包含预期 JSON 字符串。

`test_case/api.py`：

- 类型：API 调试脚本。
- 不是 unittest 测试类。
- 直接构造请求头和 JSON body。
- 请求 `https://adv.xiwshijieheping.com/adAlliance/ad/pullAds`。
- `verify=False` 关闭 HTTPS 证书校验。
- 直接 `print(req.json())`。

`test_case/test_tuizhanggui.py`：

- 类型：小程序自动化。
- 框架：`unittest` + minium。
- 测试类继承 `minium.MiniTest`。
- 点击文本为“我的抵用金”的 view 元素，再点击指定 `data-event-opts` 元素。

`test_case/test.py`：

- 类型：小程序自动化，同时包含大量注释掉的历史实验代码。
- 有效代码与 `test_tuizhanggui.py` 类似：
  - 测试类继承 `minium.MiniTest`。
  - 点击“我的抵用金”。
  - 点击指定 `data-event-opts` 元素。

`test_case/config.json`：

- minium/微信开发者工具相关配置。
- 包含 `project_path` 和 `dev_tool_path`。

分类汇总：

- UI 自动化：
  - `test_shanghu.py`
  - `test_xinlian.py`
  - `test_lhcz.py`
  - `test_yichuang.py`
- API：
  - `test_api.py`
  - `api.py`
- 小程序：
  - `test_tuizhanggui.py`
  - `test.py`
- 执行入口：
  - `run.py`

## 六、项目依赖

当前项目没有看到 `requirements.txt`、`pyproject.toml`、`Pipfile` 或类似依赖清单。以下依赖来自实际 import。

`selenium`：

- 用于浏览器 UI 自动化。
- 使用位置：
  - `base/base.py`
  - `page_object/index_page.py`
  - `test_shanghu.py`
  - `test_xinlian.py`
  - `test_lhcz.py`
  - `test_yichuang.py`
  - `BeautifulReport/tests/test_make_report.py`

`requests`：

- 用于 HTTP API 请求。
- 使用位置：
  - `test_case/test_api.py`
  - `test_case/api.py`

`ddddocr`：

- 用于验证码图片 OCR 识别。
- 使用位置：
  - `test_case/test_shanghu.py`
  - `test_case/test_lhcz.py`
  - `test_case/test_yichuang.py`

`pymysql`：

- 用于连接 MySQL。
- 使用位置：
  - `base/base.py`

`BeautifulReport`：

- 项目内置包。
- 用于 unittest HTML 报告生成、用例日志收集、截图嵌入。
- 使用位置：
  - `test_case/run.py`
  - `test_case/test_shanghu.py`
  - `test_case/test_xinlian.py`
  - `BeautifulReport/sample/sample.py`

`minium`：

- 用于微信小程序自动化。
- 使用位置：
  - `test_case/test_tuizhanggui.py`
  - `test_case/test.py`

其他实际 import：

- `lxml.etree`：`BeautifulReport/tests/test_make_report.py` 中用于解析 HTML。
- `pytest`：`BeautifulReport/BeautifulReport.py` 中有 import，但当前代码中没有直接使用。
- `certifi`、`urllib3`：`test_case/api.py` 中导入，实际 HTTPS 证书校验相关代码多数被注释。

## 七、目前存在的问题

以下问题仅根据当前代码分析。

1. 缺少依赖清单
   - 项目没有 `requirements.txt` 等依赖文件。
   - 新环境无法直接知道需要安装哪些包和版本。

2. 浏览器驱动路径仍然硬编码
   - 多个 UI 测试中保留 `D:\Python310\chromedriver.exe`。
   - `test_yichuang.py` 使用默认 ChromeDriver 查找方式。
   - 不同机器运行方式不一致。

3. 运行环境强绑定真实外部服务
   - UI 测试访问真实 URL。
   - API 测试访问内网或线上地址。
   - 数据库连接直接指向真实 MySQL。

4. 敏感信息直接写在代码中
   - MySQL host、账号、密码在 `base/base.py` 中。
   - API Authorization、clientauthorization、ad-preference 等在测试脚本中。
   - 登录账号密码写在 UI 测试中。

5. 用例之间存在隐式依赖
   - `test_shanghu.py` 中使用全局 `skip` 控制后续用例是否跳过。
   - `skip` 的声明位置和类变量 `skip` 并不完全一致，实际依赖执行顺序和全局变量状态。

6. 等待方式以 `time.sleep()` 为主
   - UI 测试大量使用固定等待。
   - 页面加载慢或快都会影响稳定性和执行效率。

7. XPath 过长且脆弱
   - 多数元素定位使用完整绝对 XPath。
   - 页面结构轻微变化会导致用例失败。

8. Page Object 覆盖范围很小
   - 当前只有 `shanghu` 一个页面对象。
   - `test_lhcz.py`、`test_yichuang.py` 大量直接在测试里写页面操作。

9. BeautifulReport 内部存在实现问题
   - `complete_output()` 中 `self.sys_stdout = sys.stderr` 和后续恢复 stderr 的逻辑看起来不一致。
   - `img2base()` 中使用 `platform != 'Windows'`，这里的 `platform` 是模块，不是 `platform.system()` 的结果。
   - `add_test_img()` 异常时调用 `sys.exit(0)`，可能掩盖真实失败。

10. `api.py` 是直接执行脚本，不是测试用例
    - import 或执行文件时会直接发起 HTTP 请求。
    - 不适合被测试发现机制误收集或被其他模块 import。

11. 命名不统一
    - 类名有 `Testshanghu`、`Testxinlian`、`Testlhcz`、`Testsaas`、`class test`。
    - 文件名和测试描述存在历史项目混用痕迹。

12. 小程序配置仍是本机路径
    - `test_case/config.json` 中 `project_path` 和 `dev_tool_path` 是 Windows 绝对路径。

13. 缺少统一测试运行策略
    - `run.py` 默认只跑 `test_shanghu.py`。
    - 其他测试通常依赖直接 `python file.py` 或 `python -m unittest`。
    - 没有区分 UI、API、小程序、冒烟、回归等测试集。

14. 项目包含历史产物
    - 仓库中存在历史 HTML 报告、截图、日志、`.DS_Store`、`__pycache__`。
    - 这些文件不影响代码逻辑，但会增加项目噪音。

15. 测试断言存在明显调试痕迹
    - `test_shanghu.py` 和 `test_xinlian.py` 中登录成功断言预期值为 `'123'`，旁边注释了原本的页面标题。
    - `test_yichuang.py` 中预期值为 `'234'`。

## 八、建议升级路线

按风险由低到高排序：

1. 建立依赖清单
   - 增加 `requirements.txt`。
   - 只记录当前代码实际 import 的第三方依赖。
   - 不改变任何测试逻辑。

2. 完善路径工程化
   - 继续把 chromedriver、小程序配置、日志路径纳入统一配置。
   - 保持默认行为兼容当前项目。

3. 增加运行说明
   - 编写 README 或补充本文档。
   - 明确 UI、API、小程序分别如何运行。
   - 标注哪些运行会访问真实环境。

4. 清理仓库产物
   - 增加 `.gitignore` 规则。
   - 后续再决定是否移除历史报告、截图、缓存文件。

5. 配置外置化
   - 将账号、密码、Token、数据库连接、URL、ChromeDriver 路径移到环境变量或配置文件。
   - 先保持默认兼容，再逐步切换。

6. 拆分测试类型入口
   - 为 UI、API、小程序建立明确运行入口。
   - 避免 `api.py` 这类脚本被误当作普通模块执行。

7. 稳定 Selenium 等待
   - 用显式等待替代固定 `time.sleep()`。
   - 优先处理登录、验证码、页面跳转等关键等待点。

8. 强化 Page Object
   - 把 `test_lhcz.py`、`test_yichuang.py` 中重复页面操作逐步下沉到 Page Object。
   - 避免一次性大重构，按页面或业务流迁移。

9. 优化定位器
   - 用更稳定的 CSS、ID、文本、属性定位替代绝对 XPath。
   - 对高频元素先迁移。

10. 修复用例依赖和断言
    - 消除全局 `skip` 对执行顺序的依赖。
    - 将调试断言恢复为真实业务断言。
    - 明确哪些用例可独立运行。

11. 改造报告库集成
    - 修复 BeautifulReport 中 stdout/stderr、图片路径、异常处理等问题。
    - 或评估切换到维护更活跃的报告方案。

12. 建立隔离测试环境
    - 为 API、数据库、UI 自动化准备独立测试环境和测试数据。
    - 减少对真实线上数据和个人本机配置的依赖。
