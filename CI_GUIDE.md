# GitHub Actions CI 使用说明

## Self-hosted Runner 说明

Open Web UI 自动化测试使用 Mac mini 上的 GitHub Actions Self-hosted Runner 执行。

当前 workflow 使用的 runner 标签：

```yaml
runs-on:
  - self-hosted
  - macOS
  - ARM64
  - open-web
```

Mac mini 本机需要提前具备：

- `python3`
- Google Chrome：`/Applications/Google Chrome.app`
- Open Web 服务
- `http://localhost:3000` 可访问
- GitHub Actions Runner 已注册并在线

CI 不负责下载 Python、Chrome 或 ChromeDriver。

## 启动 Runner

进入 Mac mini 上 GitHub Actions Runner 安装目录，执行：

```bash
./run.sh
```

Runner 需要保持运行状态。否则 GitHub Actions 会一直等待 self-hosted runner 接单。

## CI 触发条件

Open Web UI Tests 会在以下场景触发：

- push 到 `develop`
- push 到 `main`
- pull request 目标分支为 `develop`
- pull request 目标分支为 `main`

workflow 文件：

```text
.github/workflows/open-web-ui-tests.yml
```

## CI 执行内容

CI 会在 self-hosted Mac mini 上执行：

```bash
python3 --version
which python3
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version
curl -I "$WEB_BASE_URL"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m compileall .
python test_case/run.py
```

测试失败时，CI job 会失败。

## 如何查看 GitHub Actions 运行结果

1. 打开 GitHub 仓库。
2. 进入 `Actions`。
3. 选择 `Open Web UI Tests` workflow。
4. 打开对应的 run。
5. 查看 `open-web-ui-tests` job。
6. 展开失败 step 查看日志。

优先查看：

1. `Check local environment`
2. `Run Open Web UI tests in virtualenv`
3. Artifacts 中的报告、截图和日志

## 如何下载 BeautifulReport

CI 会上传：

```text
open-web-report
```

下载方式：

1. 打开对应 GitHub Actions run。
2. 滚动到页面底部 `Artifacts` 区域。
3. 下载 `open-web-report`。
4. 解压后打开其中的 HTML 报告。

报告来源目录：

```text
report/
```

## 邮件报告

CI 测试执行完成后会尝试发送 BeautifulReport 邮件。

邮件发送步骤使用：

```yaml
if: always()
```

因此无论测试成功或失败，都会尝试发送邮件。

邮件附件：

```text
report/ 下最新的 BeautifulReport HTML 文件
```

邮件标题包含：

- Open Web 自动化测试报告
- CI 成功或失败状态
- 发送时间

邮件正文包含：

- 测试状态
- 报告文件名
- GitHub Actions run 信息
- commit SHA
- branch/ref

需要在 GitHub Secrets 中配置：

```text
MAIL_HOST
MAIL_PORT
MAIL_USERNAME
MAIL_PASSWORD
MAIL_FROM
MAIL_TO
```

`MAIL_TO` 支持多个收件人，多个邮箱用英文逗号分隔。

不要把邮箱密码、授权码或真实账号写入代码或文档。

如果邮件发送失败，CI 会失败。

## 如何查看截图 artifact

CI 会上传：

```text
open-web-screenshots
```

下载后查看其中的失败截图。

截图来源目录：

```text
img/
```

如果本次没有失败截图，该 artifact 可能为空或不生成。

## 如何查看 logs artifact

CI 会上传：

```text
open-web-logs
```

日志来源目录：

```text
logs/
```

排查失败时，日志可以辅助确认：

- 浏览器是否启动
- ChromeDriver 来源
- 登录流程执行到哪一步
- 失败截图保存路径
- 依赖跳过原因

## 常见失败原因

### Open Web 服务未启动

表现：

- `curl -I "$WEB_BASE_URL"` 失败
- 测试无法打开登录页
- Selenium 报页面不可达

处理：

- 确认 Mac mini 上 Open Web Docker 服务已启动。
- 确认 `http://localhost:3000` 可访问。

### WEB_BASE_URL 不可访问

表现：

- `Check local environment` 中 `curl -I "$WEB_BASE_URL"` 失败。

处理：

- 检查 GitHub Secrets 中的 `WEB_BASE_URL`。
- 如果使用本机服务，确认值指向 Mac mini runner 可访问的地址。

### Secrets 未配置

表现：

- 登录用例失败。
- 日志中账号为空或认证失败。

需要配置：

```text
WEB_BASE_URL
DEFAULT_ACCOUNT_EMAIL
DEFAULT_ACCOUNT_PASSWORD
DEFAULT_ACCOUNT_INVALID_PASSWORD
```

不要提交 `config/config.yaml`。

### Chrome 无法启动

表现：

- Selenium 创建浏览器失败。
- Chrome 或 ChromeDriver 相关异常。

处理：

- 确认本机存在：

```text
/Applications/Google Chrome.app
```

- 查看 `Check local environment` 中 Chrome 版本输出。
- 查看 `open-web-logs` 中 DriverManager 日志。

### 依赖安装失败

表现：

- `python -m pip install -r requirements.txt` 失败。

处理：

- 查看失败包名和错误。
- 确认 self-hosted runner 网络可访问 PyPI。
- 确认 `.venv` 可以创建。

### 用例断言失败

表现：

- `python test_case/run.py` 返回失败。
- BeautifulReport 中有失败用例。

处理：

- 先下载 `open-web-report` 查看失败用例。
- 再下载 `open-web-screenshots` 查看失败截图。
- 最后查看 `open-web-logs` 分析执行过程。

## 失败时应该先看哪里

推荐顺序：

1. GitHub Actions 中失败的 step 日志。
2. `open-web-report` 的 BeautifulReport。
3. `open-web-screenshots` 中的失败截图。
4. `open-web-logs` 中的运行日志。
5. Mac mini 本机 Open Web 服务状态。

## 本地如何复现

在项目根目录执行：

```bash
python3 test_case/run.py
```

如果需要先做语法检查：

```bash
python3 -m compileall .
python3 test_case/run.py
```
