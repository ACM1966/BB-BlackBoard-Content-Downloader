"""
认证模块 - 通过浏览器登录并提取 Cookie
"""

import json
import os
import time

import requests
from rich.console import Console
from rich.panel import Panel

from config import (
    BB_BASE_URL,
    COOKIE_FILE,
    LOGIN_SUCCESS_INDICATORS,
    LOGIN_URL,
    API_BASE_URL,
    API_TIMEOUT,
)

console = Console()


def _save_cookies(cookies: list[dict]) -> None:
    """将 cookie 保存到本地文件"""
    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)
    console.print(f"[green]✓[/green] Cookie 已缓存到 {COOKIE_FILE}")


def _load_cookies() -> list[dict] | None:
    """从本地文件加载 cookie"""
    if not os.path.exists(COOKIE_FILE):
        return None
    try:
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        return cookies
    except (json.JSONDecodeError, IOError):
        return None


def _cookies_to_session(cookies: list[dict]) -> requests.Session:
    """将 cookie 列表转换为 requests.Session"""
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(
            cookie["name"],
            cookie["value"],
            domain=cookie.get("domain", ""),
            path=cookie.get("path", "/"),
        )
    # 设置通用请求头
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    })
    return session


def _validate_session(session: requests.Session) -> bool:
    """验证 session 是否有效（尝试获取用户信息）"""
    try:
        resp = session.get(
            f"{API_BASE_URL}/users/me",
            timeout=API_TIMEOUT,
            allow_redirects=False,
        )
        return resp.status_code == 200
    except requests.RequestException:
        return False


def _login_via_browser() -> list[dict]:
    """
    打开浏览器让用户登录，登录成功后提取 cookie。
    使用 Selenium WebDriver。
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions

    console.print(
        Panel(
            "[bold yellow]即将打开浏览器，请在浏览器中登录 Blackboard[/bold yellow]\n"
            f"网址: {LOGIN_URL}\n\n"
            "[dim]登录成功后程序会自动检测并继续...[/dim]",
            title="🔐 登录",
            border_style="yellow",
        )
    )

    # 配置 Chrome
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # 尝试使用 webdriver-manager 自动管理驱动
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception:
        # 如果 webdriver-manager 失败，尝试直接使用系统 Chrome
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            # 尝试 Edge 作为备选
            try:
                from selenium.webdriver.edge.service import Service as EdgeService
                from selenium.webdriver.edge.options import Options as EdgeOptions
                from webdriver_manager.microsoft import EdgeChromiumDriverManager

                edge_options = EdgeOptions()
                edge_options.add_argument("--disable-blink-features=AutomationControlled")
                edge_service = EdgeService(EdgeChromiumDriverManager().install())
                driver = webdriver.Edge(service=edge_service, options=edge_options)
            except Exception:
                try:
                    from selenium.webdriver.edge.options import Options as EdgeOptions
                    edge_options = EdgeOptions()
                    edge_options.add_argument("--disable-blink-features=AutomationControlled")
                    driver = webdriver.Edge(options=edge_options)
                except Exception:
                    console.print("[bold red]✗ 无法启动浏览器！请确保已安装 Chrome 或 Edge。[/bold red]")
                    raise RuntimeError("无法启动任何浏览器") from e

    try:
        driver.get(LOGIN_URL)
        console.print("[cyan]⏳ 等待登录...[/cyan]")

        # 等待用户登录成功
        max_wait = 300  # 最多等待 5 分钟
        start_time = time.time()

        while time.time() - start_time < max_wait:
            current_url = driver.current_url
            # 检查是否已经跳转到登录成功的页面
            if any(indicator in current_url for indicator in LOGIN_SUCCESS_INDICATORS):
                console.print("[green]✓ 检测到登录成功！[/green]")
                time.sleep(2)  # 多等 2 秒确保所有 cookie 都设置完毕
                break
            time.sleep(1)
        else:
            console.print("[bold red]✗ 登录超时（5分钟）[/bold red]")
            raise TimeoutError("登录超时")

        # 提取所有 cookie
        selenium_cookies = driver.get_cookies()
        cookies = []
        for c in selenium_cookies:
            cookies.append({
                "name": c["name"],
                "value": c["value"],
                "domain": c.get("domain", ""),
                "path": c.get("path", "/"),
                "secure": c.get("secure", False),
            })

        return cookies

    finally:
        driver.quit()


def get_session(force_relogin: bool = False) -> requests.Session:
    """
    获取已认证的 requests.Session。

    优先使用缓存的 cookie，如果无效则重新登录。

    Args:
        force_relogin: 是否强制重新登录

    Returns:
        已配置好 cookie 的 requests.Session
    """
    # 尝试使用缓存的 cookie
    if not force_relogin:
        cached_cookies = _load_cookies()
        if cached_cookies:
            console.print("[cyan]🔄 尝试使用缓存的 Cookie...[/cyan]")
            session = _cookies_to_session(cached_cookies)
            if _validate_session(session):
                console.print("[green]✓ Cookie 有效，无需重新登录[/green]")
                return session
            else:
                console.print("[yellow]⚠ 缓存的 Cookie 已失效，需要重新登录[/yellow]")

    # 通过浏览器登录获取新 cookie
    cookies = _login_via_browser()
    _save_cookies(cookies)

    session = _cookies_to_session(cookies)
    if not _validate_session(session):
        console.print("[bold red]✗ 登录后仍无法访问 API，请检查网络或账户[/bold red]")
        raise RuntimeError("认证失败")

    return session
