# main.py

import logging
import os
import datetime
import google.generativeai as genai
from newsapi import NewsApiClient
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import requests
from dotenv import load_dotenv

# --- 配置日志 ---
# 将日志输出到文件，方便排查问题
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='reporter.log', # 日志会记录到这个文件
    filemode='a' # a for append
)
# 同时也在控制台输出
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


# --- 加载配置 ---
# 从 .env 文件加载环境变量
load_dotenv()

# 读取所有配置
# 因为你的服务器已经开了系统代理，我们不需要在代码里做任何代理配置
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
MAIL_SENDER = os.getenv("MAIL_SENDER")
MAIL_RECEIVER = os.getenv("MAIL_RECEIVER")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# --- 初始化服务 ---
try:
    genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    gemini_model = genai.GenerativeModel(model_name='gemini-2.5-flash-lite', safety_settings=safety_settings)
except Exception as e:
    logging.error(f"初始化Gemini失败: {e}")
    gemini_model = None

# --- 函数定义 (与之前完全相同) ---
def get_news_from_newsapi():
    logging.info("正在从 NewsAPI.org 获取新闻...")
    try:
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)
        top_headlines = newsapi.get_top_headlines(language='en', page_size=10)
        if top_headlines['status'] == 'ok':
            logging.info("成功获取新闻。")
            return top_headlines['articles']
        else:
            logging.error(f"NewsAPI返回错误: {top_headlines.get('message')}")
            return None
    except Exception as e:
        logging.error(f"从NewsAPI.org获取新闻时出错: {e}")
        return None

def summarize_news(news_list):
    logging.info("正在使用Google Gemini Pro总结新闻...")
    summaries = []
    for news in news_list:
        title = news.get('title')
        description = news.get('description')
        url = news.get('url')
        content_to_summarize = description if description else title
        prompt = f"""直接提取并输出以下新闻内容的核心要点，使用中文，以无序列表（bullet points）的形式呈现。
要求：
1. 不超过3个要点。
2. 直接输出要点，不要包含任何前导、解释或总结性文字。
3. 你的回答必须以第一个要点（例如•或*）开始。

新闻标题: {title}
新闻内容: {content_to_summarize}
"""
        try:
            response = gemini_model.generate_content(prompt)
            summary = response.text
            summaries.append({"title": title, "summary": summary, "url": url})
            logging.info(f"已总结新闻: {title}")
        except Exception as e:
            logging.error(f"使用Gemini总结新闻 '{title}' 时出错: {e}")
            continue
    return summaries

def generate_inspiration():
    logging.info("正在使用Google Gemini Pro生成灵感卡片...")

    # --- 优化后的、旨在提升多样性的Prompt ---
    prompt = """你是一位知识渊博且富有创造力的科普作家，你的任务是为读者带来每日的知识惊喜。

请生成一个“今日概念卡片”，内容必须满足以下所有要求：
1.  **主题新颖**: 请避免选择过于大众化或陈词滥调的概念（例如：量子纠缠、薛定谔的猫、相对论、巴甫洛夫的狗等）。我希望看到一些真正能拓展我知识面的、不常见的知识点。
2.  **领域多样**: 请从下面这个更详细的领域列表中，随机选择一个进行介绍：
    *   **硬核科技**: 如最新的AI架构、某个不为人知的编程语言范式、空间探测器上的某个关键技术、材料科学的新突破。
    *   **深刻哲思**: 如某个冷门哲学家的核心思想、一个有趣的逻辑悖论、东方哲学中的某个特定概念（如“无为”）。
    *   **精妙科学**: 如某个有趣的生物学现象（如灯塔水母的永生）、一个反直觉的物理学原理、化学中的某个奇特反应。
    *   **认知心理**: 如一个不常见的认知偏误（如“宜家效应”）、关于记忆或学习的新理论。
    *   **社科经济**: 如某个小众但影响深远的经济学模型、一个有趣的历史社会学现象。
3.  **格式要求**:
    *   用3-5句话简明扼要地介绍这个概念。
    *   解释它为什么重要、有趣，或者它在现实世界中的应用。
    *   你的回答必须直接是概念的介绍，不包含任何“当然，这是一个...”之类的前导语。

现在，请给我带来一个惊喜。"""

    try:
        # 这个任务更复杂，保留重试逻辑
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = gemini_model.generate_content(prompt)
                logging.info("灵感卡片生成成功！")
                return response.text
            except Exception as e:
                logging.warning(f"生成灵感时出错 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt + 1 == max_retries:
                    raise e
    except Exception as e:
        logging.error(f"最终生成灵感失败: {e}")
        return "今日灵感卡片正在多元宇宙中穿梭，暂时无法连接。但请记住，知识的边界，就是探索的起点。"

def format_email_body(summaries, inspiration):
    # (此函数无任何修改)
    today_str = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d') # 使用北京时间
    html_content = f"""
    <html><head><style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; }} .container {{ max-width: 680px; margin: 20px auto; padding: 25px; border: 1px solid #e0e0e0; border-radius: 12px; background-color: #f9f9f9; }} h1 {{ color: #2c3e50; text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 10px; }} h2 {{ color: #34495e; }} .news-item {{ background-color: #ffffff; padding: 15px; margin-bottom: 20px; border-radius: 8px; border-left: 4px solid #3498db; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }} .news-title {{ font-size: 1.2em; font-weight: 600; margin-top: 0; }} .summary {{ margin-left: 15px; border-left: 2px solid #ecf0f1; padding-left: 15px; }} .source-link {{ display: inline-block; margin-top: 10px; font-size: 0.9em; text-decoration: none; color: #ffffff; background-color: #3498db; padding: 8px 12px; border-radius: 5px; }} .inspiration-card {{ background-color: #e8f6f3; border-left: 4px solid #1abc9c; padding: 15px; margin-top: 30px; border-radius: 8px; }} .footer {{ margin-top: 30px; font-size: 0.8em; color: #7f8c8d; text-align: center; }}
    </style></head><body>
    <div class="container">
        <h1>📰 全球新闻摘要 ({today_str})</h1>
    """
    for item in summaries:
        summary_html = item['summary'].replace('•', '&#8226;').replace('*', '&#8226;').replace('\n', '<br>')
        html_content += f"""
        <div class="news-item"> <p class="news-title">{item['title']}</p> <div class="summary">{summary_html}</div> <a href="{item['url']}" class="source-link">阅读原文 &rarr;</a> </div>
        """
    html_content += f"""
        <div class="inspiration-card"> <h2>今日灵感卡片 ✨</h2> <p>{inspiration}</p> </div>
        <div class="footer"> <p>Powered by Python on Ubuntu Server</p> </div>
    </div></body></html>
    """
    return html_content, f"每日全球新闻头条 ({today_str})"

def send_email(html_content, subject):
    logging.info(f"准备使用SMTP服务 ({SMTP_HOST}) 发送邮件...")
    message = MIMEText(html_content, 'html', 'utf-8')
    message['From'] = Header(f"每日新闻助手 <{MAIL_SENDER}>", 'utf-8')
    message['To'] = Header(f"订阅者 <{MAIL_RECEIVER}>", 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')
    try:
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(MAIL_SENDER, [MAIL_RECEIVER], message.as_string())
        server.quit()
        logging.info("邮件发送成功！")
    except Exception as e:
        logging.error(f"邮件发送失败: {e}")

# --- 主执行块 ---
if __name__ == "__main__":
    logging.info("============ 任务开始 ============")
    if not all([GOOGLE_GEMINI_API_KEY, NEWS_API_KEY, SMTP_HOST, SMTP_USER, SMTP_PASSWORD]):
        logging.error("一个或多个关键配置缺失，请检查.env文件。")
    elif not gemini_model:
        logging.error("Gemini模型初始化失败，任务中止。")
    else:
        news_list = get_news_from_newsapi()
        if news_list:
            summaries = summarize_news(news_list)
            inspiration = generate_inspiration()
            if summaries:
                html_body, subject = format_email_body(summaries, inspiration)
                send_email(html_body, subject)
            else:
                logging.warning("新闻总结为空，不发送邮件。")
        else:
            logging.warning("未能获取任何新闻，任务结束。")
    logging.info("============ 任务结束 ============\n")