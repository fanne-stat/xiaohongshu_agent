import os
import time
import random
import json
from typing import Dict, List, Optional
import requests
from fake_useragent import UserAgent
from loguru import logger
import pandas as pd
from playwright.sync_api import sync_playwright
from urllib.parse import quote

class XHSCrawler:
    def __init__(self, config_path: str = "config.py"):
        """初始化小红书爬虫

        Args:
            config_path (str): 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.ua = UserAgent()
        self._setup_directories()
        self._setup_logging()
        
    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", config_path)
            config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config)
            return {k: v for k, v in config.__dict__.items() if not k.startswith('_')}
        except Exception as e:
            raise Exception(f"配置文件加载失败: {str(e)}")

    def _setup_directories(self):
        """创建必要的目录"""
        os.makedirs(self.config['OUTPUT_DIR'], exist_ok=True)
        os.makedirs(os.path.join(self.config['OUTPUT_DIR'], 'data'), exist_ok=True)

    def _setup_logging(self):
        """配置日志"""
        logger.add(
            os.path.join(self.config['OUTPUT_DIR'], "crawler.log"),
            rotation="500 MB",
            level="INFO"
        )

    def _get_headers(self) -> Dict[str, str]:
        """生成请求头"""
        return {
            'User-Agent': self.ua.random,
            'Cookie': self.config['XHS_COOKIE'],
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Origin': 'https://www.xiaohongshu.com',
            'Referer': 'https://www.xiaohongshu.com'
        }

    def search_notes(self, keyword: str, page_num: int = 1) -> List[Dict]:
        """搜索笔记

        Args:
            keyword (str): 搜索关键词
            page_num (int): 页码

        Returns:
            List[Dict]: 搜索结果列表
        """
        logger.info(f"搜索关键词: {keyword}, 页码: {page_num}")
        
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0'
            )
            
            try:
                # 设置cookie
                cookies = []
                for cookie_str in self.config['XHS_COOKIE'].split('; '):
                    if '=' in cookie_str:
                        name, value = cookie_str.split('=', 1)
                        cookies.append({
                            'name': name,
                            'value': value,
                            'domain': '.xiaohongshu.com',
                            'path': '/'
                        })
                
                context.add_cookies(cookies)
                page = context.new_page()
                
                # 访问搜索页面
                encoded_keyword = quote(keyword)
                url = f"https://www.xiaohongshu.com/search_result?keyword={encoded_keyword}&type=51"
                if page_num > 1:
                    url += f"&page={page_num}"
                
                logger.debug(f"访问URL: {url}")
                page.goto(url, wait_until='domcontentloaded', timeout=30000)
                time.sleep(2)
                
                # 等待内容加载
                selectors = ['.note-item', 'div[data-id]', 'div[data-note-id]', '.search-note-item', '.note-card']
                content_found = False
                for selector in selectors:
                    try:
                        page.wait_for_selector(selector, timeout=5000)
                        content_found = True
                        logger.debug(f"找到内容选择器: {selector}")
                        break
                    except Exception:
                        continue
                
                if not content_found:
                    logger.error("未找到内容元素")
                    return []
                
                # 提取数据
                notes = []
                for selector in selectors:
                    try:
                        note_items = page.query_selector_all(selector)
                        logger.debug(f"使用选择器 {selector} 找到 {len(note_items)} 个元素")
                        
                        if note_items:
                            for idx, item in enumerate(note_items):
                                try:
                                    html = item.evaluate('el => el.outerHTML')
                                    logger.debug(f"处理第 {idx + 1} 个元素: {html}")
                                    
                                    # 获取链接
                                    link = item.query_selector('a[href*="/search_result/"]') or item.query_selector('a[href*="/explore/"]')
                                    if not link:
                                        logger.debug("未找到链接")
                                        continue
                                        
                                    href = link.get_attribute('href')
                                    logger.debug(f"找到链接: {href}")
                                    
                                    # 提取ID和token
                                    import re
                                    match = re.search(r'/(?:explore|search_result)/([a-zA-Z0-9]+)(?:\?.*xsec_token=([^&]+))?', href)
                                    if not match:
                                        logger.debug("无法从链接中提取ID")
                                        continue
                                        
                                    note_id = match.group(1)
                                    xsec_token = match.group(2) or ''
                                    logger.debug(f"从链接中提取到ID: {note_id}, token: {xsec_token}")
                                    
                                    # 构造URL
                                    note_url = f"https://www.xiaohongshu.com/explore/{note_id}"
                                    if xsec_token:
                                        note_url += f"?xsec_token={xsec_token}"
                                    
                                    # 获取标题
                                    title = ''
                                    for title_selector in ['.title', '.note-title', 'h3', '.desc', '.content']:
                                        title_elem = item.query_selector(title_selector)
                                        if title_elem:
                                            title = title_elem.inner_text().strip()
                                            logger.debug(f"使用选择器 {title_selector} 找到标题: {title}")
                                            break
                                    
                                    # 获取用户名
                                    user = ''
                                    for user_selector in ['.user-name', '.author-name', '.nickname', '.user', '.name']:
                                        user_elem = item.query_selector(user_selector)
                                        if user_elem:
                                            user = user_elem.inner_text().strip()
                                            logger.debug(f"使用选择器 {user_selector} 找到用户名: {user}")
                                            break
                                    
                                    note = {
                                        'id': note_id,
                                        'url': note_url,
                                        'title': title,
                                        'user': user
                                    }
                                    
                                    notes.append(note)
                                    logger.debug(f"成功添加笔记: {note}")
                                    
                                except Exception as e:
                                    logger.error(f"提取笔记信息失败: {str(e)}")
                                    continue
                            
                            if notes:
                                break
                    except Exception as e:
                        logger.error(f"使用选择器 {selector} 提取数据失败: {str(e)}")
                        continue
                
                logger.info(f"共找到 {len(notes)} 条笔记")
                return notes
                
            except Exception as e:
                logger.error(f"搜索笔记失败: {str(e)}")
                return []
            
            finally:
                browser.close()

    def get_note_detail(self, note_id: str, note_url: str = None) -> Dict:
        """获取笔记详情

        Args:
            note_id (str): 笔记ID
            note_url (str, optional): 笔记完整URL。如果提供，将优先尝试从URL直接获取内容

        Returns:
            Dict: 笔记详情
        """
        logger.info(f"获取笔记详情: {note_id}")
        
        if not note_url:
            logger.error("未提供笔记URL")
            return None
            
        try:
            with sync_playwright() as p:
                browser = p.firefox.launch(headless=True)
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0'
                )
                
                try:
                    # 设置cookie
                    cookies = []
                    for cookie_str in self.config['XHS_COOKIE'].split('; '):
                        if '=' in cookie_str:
                            name, value = cookie_str.split('=', 1)
                            cookies.append({
                                'name': name,
                                'value': value,
                                'domain': '.xiaohongshu.com',
                                'path': '/'
                            })
                    
                    context.add_cookies(cookies)
                    page = context.new_page()
                    page.goto(note_url, wait_until='networkidle')
                    
                    # 等待内容加载
                    page.wait_for_selector('.note-text', timeout=10000)
                    
                    # 提取页面内容
                    detail = {
                        'id': note_id,
                        'title': page.evaluate('() => document.querySelector(".title")?.innerText || ""'),
                        'content': page.evaluate('() => document.querySelector(".note-text")?.innerText || ""')
                    }
                    
                    logger.debug(f"成功从页面提取笔记数据: {detail}")
                    return detail
                    
                except Exception as e:
                    logger.error(f"从页面获取笔记内容失败: {str(e)}")
                    return None
                
                finally:
                    browser.close()
        except Exception as e:
            logger.error(f"Playwright初始化失败: {str(e)}")
            return None

    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """随机延迟一段时间

        Args:
            min_seconds (float): 最小延迟秒数
            max_seconds (float): 最大延迟秒数
        """
        time.sleep(random.uniform(min_seconds, max_seconds))

    def save_to_csv(self, data: List[Dict], filename: str):
        """保存数据到CSV文件

        Args:
            data (List[Dict]): 要保存的数据
            filename (str): 文件名
        """
        try:
            df = pd.DataFrame(data)
            output_path = os.path.join(self.config['OUTPUT_DIR'], 'data', filename)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            logger.info(f"数据已保存到: {output_path}")
        except Exception as e:
            logger.error(f"保存CSV文件失败: {str(e)}") 