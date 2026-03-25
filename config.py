"""
配置模块 - Blackboard Learn 下载器
"""

import os

# Blackboard 基础 URL（通过环境变量配置，或修改此默认值）
BB_BASE_URL = os.environ.get("BB_BASE_URL", "https://your-blackboard-domain.edu")

# REST API 路径前缀
API_PREFIX = "/learn/api/public/v1"

# 完整 API 基础 URL
API_BASE_URL = f"{BB_BASE_URL}{API_PREFIX}"

# 默认下载目录
DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")

# Cookie 缓存文件路径
COOKIE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.json")

# 登录成功后的判断条件
# 登录成功后，浏览器会跳转到包含以下路径的 URL
LOGIN_SUCCESS_INDICATORS = [
    "/ultra/",
    "/webapps/portal",
    "/webapps/blackboard",
    "/ultra/course",
    "/ultra/institution-page",
]

# 登录页面 URL
LOGIN_URL = f"{BB_BASE_URL}"

# API 分页设置
PAGE_SIZE = 100

# 下载超时（秒）
DOWNLOAD_TIMEOUT = 300

# API 请求超时（秒）
API_TIMEOUT = 30

# 下载重试次数
MAX_RETRIES = 3

# 文件名中不允许的字符替换映射
INVALID_CHARS = {
    '<': '＜',
    '>': '＞',
    ':': '：',
    '"': '＂',
    '/': '／',
    '\\': '＼',
    '|': '｜',
    '?': '？',
    '*': '＊',
}
