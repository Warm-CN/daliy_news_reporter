# 🤖 AI Daily News Reporter - 每日新闻AI助手

这是一个自动化Python项目，旨在每日定时获取全球头条新闻，利用大型语言模型（Google Gemini）进行智能分析和总结，并结合一个新颖的知识卡片，最终通过电子邮件发送给用户。这是一个完美的、可部署在个人服务器上的“知识早餐”解决方案。

---

## ✨ 功能亮点

*   **全自动化**: 一次部署，每日在北京时间上午8点自动运行，无需任何人工干预。
*   **智能总结**: 调用强大的Google Gemini模型，将新闻精准地总结为中文要点，摒弃冗余信息。
*   **知识拓展**: 每日附上一张精心设计的“灵感卡片”，介绍一个来自科技、哲学、心理学等领域的非热门知识点，助你拓展知识边界。
*   **精美排版**: 邮件使用HTML精心排版，提供专业、舒适的阅读体验，并包含新闻原文链接。
*   **高度可配置**: 所有API密钥和个人设置均通过`.env`文件管理，安全且易于修改。
*   **稳定可靠**: 部署在Linux服务器上，通过`cron`或`systemd`定时器保证任务的稳定执行。
*   **网络适应性强**: 通过在执行脚本中配置代理，能完美适应需要网络代理的环境。

---

## 🛠️ 技术栈

*   **语言**: Python 3
*   **核心库**:
    *   `google-generativeai`: 用于调用Google Gemini API。
    *   `newsapi-python`: 用于从NewsAPI.org获取新闻。
    *   `requests`: 底层HTTP通信。
    *   `python-dotenv`: 管理环境变量。
*   **部署环境**:
    *   **操作系统**: Ubuntu Desktop (或任何Linux发行版)
    *   **自动化**: Cron
    *   **网络**: 通过Shell脚本环境变量或Clash等工具的TUN模式进行代理。

---

## 🚀 部署指南 (在Ubuntu上)

### 1. 前置准备

在开始之前，请确保你已经获取了以下所有API密钥和凭证：

*   **NewsAPI.org API Key**: 从 [NewsAPI.org](https://newsapi.org/) 获取。
*   **Google Gemini API Key**: 从 [Google AI Studio](https://aistudio.google.com/) 获取。
*   **Gmail 应用专用密码**: 从你的 [Google账户](https://myaccount.google.com/apppasswords) 获取 (需要开启两步验证)。
*   **网络代理**: 确保你的Ubuntu电脑上有一个可以正常工作的网络代理服务（如Clash Verge），并知道其HTTP代理端口（例如 `7890`）。

### 2. 环境设置

在你的Ubuntu上打开一个终端，执行以下步骤：

```bash
# 1. 安装Python和相关工具
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# 2. 克隆或创建项目
# 如果从GitHub克隆
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

# 或者手动创建
mkdir daily-news-reporter
cd daily-news-reporter

# 3. 创建并激活Python虚拟环境
python3 -m venv venv
source venv/bin/activate
```

### 3. 配置项目

1.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **创建并配置`.env`文件**:
    手动创建`.env`文件，并填入你所有的密钥和个人信息。
    ```ini
    # .env - 密钥配置文件
    GOOGLE_GEMINI_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"
    NEWS_API_KEY="YOUR_NEWSAPI_API_KEY"
    
    # Gmail SMTP配置
    SMTP_HOST="smtp.gmail.com"
    SMTP_PORT="587"
    SMTP_USER="your-email@gmail.com"
    SMTP_PASSWORD="your-16-digit-gmail-app-password"
    MAIL_SENDER="your-email@gmail.com"
    MAIL_RECEIVER="your-recipient-email@example.com"
    ```

### 4. 创建执行脚本 `run.sh`

为了封装所有运行环境，我们创建一个Shell脚本。在项目根目录下创建`run.sh`文件：

```bash
#!/bin/bash

# 切换到脚本所在的目录，确保路径正确
cd "$(dirname "$0")" || exit

# 设置网络代理环境变量 (请将端口号替换成你自己的)
export https_proxy=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890

# 激活Python虚拟环境
source venv/bin/activate

# 执行Python主脚本
python3 main.py

# 停用虚拟环境
deactivate
```

**重要**: 为该脚本添加执行权限。
```bash
chmod +x run.sh
```

### 5. 手动测试

在正式部署前，手动运行一次脚本，确保一切正常。
```bash
# 确保你的网络代理正在运行
./run.sh
```
执行后，检查终端输出的日志，并查看你的邮箱是否收到了邮件。

### 6. 部署到Cron实现自动化

1.  **编辑crontab**:
    ```bash
    crontab -e
    ```

2.  **添加定时任务**:
    在文件末尾添加以下一行。请确保将脚本的绝对路径替换成你自己的。
    ```crontab
    # 在每天北京时间上午8点，运行每日新闻报告脚本
    # 格式: 分 时 日 月 周 命令
    0 8 * * * /home/your-username/path/to/your/project/run.sh >> /home/your-username/path/to/your/project/cron.log 2>&1
    ```

3.  保存并退出。你的AI新闻助手现已完全部署并自动化！

---

## 📝 日志与维护

*   脚本的详细运行日志会记录在项目目录下的 `reporter.log` 文件中。
*   `cron`任务的执行输出（包括任何潜在的错误）会记录在 `cron.log` 文件中。
*   如果想修改功能，只需编辑`main.py`文件，`cron`会自动执行最新版本，无需重新部署。

---

## 🤝 贡献与致谢

欢迎提出Issues或Pull Requests来改进这个项目。
感谢所有提供API服务的平台：
*   [Google AI](https://ai.google/)
*   [NewsAPI.org](https://newsapi.org/)
*   [Gmail](https://www.google.com/gmail/)

---
*本项目由 [Warm-CN] 创建和维护。*
