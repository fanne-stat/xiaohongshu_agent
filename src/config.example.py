# 小红书配置
XHS_COOKIE = "your_cookie_here"

# 爬虫设置
CRAWLER_CONFIG = {
    "delay_min": 2,  # 最小延迟时间（秒）
    "delay_max": 5,  # 最大延迟时间（秒）
    "max_retries": 3,  # 最大重试次数
    "timeout": 30,  # 请求超时时间（秒）
}

# 输出设置
OUTPUT_DIR = "output"  # 输出目录
SAVE_IMAGES = True  # 是否保存图片
SAVE_COMMENTS = True  # 是否保存评论

# 代理设置（可选）
PROXY = {
    "enabled": False,
    "http": "",  # 例如: "http://127.0.0.1:7890"
    "https": "",  # 例如: "http://127.0.0.1:7890"
} 