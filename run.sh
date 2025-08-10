# --- 1. 明确地加载用户的环境变量 ---
# 这一步是关键！它会加载.profile文件，让cron环境更接近登录环境。
# if [ -f ~/.profile ]; then
#     . ~/.profile
# fi

# --- 2. 设置脚本的工作目录 ---
cd /home/warm/code/python/daily-news-reporter/ || exit

# --- 3. 设置网络代理环境变量 ---
# 将端口替换成你自己的
export https_proxy=http://127.0.0.1:7897
export http_proxy=http://127.0.0.1:7897
export all_proxy=http://127.0.0.1:7897

# --- 4. 激活Python虚拟环境 ---
source /home/warm/code/python/daily-news-reporter/.venv/bin/activate

# --- 5. 执行Python脚本 ---
/home/warm/code/python/daily-news-reporter/.venv/bin/python3 main.py

# --- 6. (可选) 停用虚拟环境 ---
deactivate