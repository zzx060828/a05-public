import os
import json
import time
import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Any


class JavaGuideQACrawler:
    def __init__(self, base_url="https://javaguide.cn/", output_json="javaguide_interview.json"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 SLBrowser/9.0.7.12231 SLBChan/115 SLBVPV/64-bit',
        })
        self.visited_urls = set()
        # 用于存储所有提取到的 Q&A
        self.qa_list: List[Dict[str, Any]] = []
        # 输出的 JSON 文件路径
        self.output_json = output_json

    def is_valid_url(self, url):
        parsed_href = urlparse(url)
        return parsed_href.scheme in ('http', 'https') and 'javaguide.cn' in parsed_href.netloc

    def fetch_page(self, url):
        try:
            print(f"[Fetching] {url}")
            time.sleep(1.5)  # 增加延迟以示友好
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            print(f"  [Error] 抓取失败: {e}")
            return None

    def _clean_html_element(self, element: Tag) -> str:
        """递归清理一个 BeautifulSoup 元素，将其转换为格式化的纯文本，保留部分结构。"""
        text_parts = []
        for child in element.children:
            if isinstance(child, Tag):
                tag_name = child.name
                # 处理不同的标签，保留一些结构语义
                if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    text_parts.append(f"\n{child.get_text(strip=True)}\n")
                elif tag_name == 'p':
                    text_parts.append(f"{child.get_text(strip=True)}\n")
                elif tag_name in ['ul', 'ol']:
                    for li in child.find_all('li', recursive=False):
                        text_parts.append(f"  - {li.get_text(strip=True)}\n")
                    text_parts.append("\n")
                elif tag_name == 'pre':
                    # 代码块，保留缩进
                    code_text = child.get_text()
                    text_parts.append(f"\n```\n{code_text}\n```\n")
                elif tag_name == 'code' and child.parent.name != 'pre':
                    # 行内代码
                    text_parts.append(f" `{child.get_text()}` ")
                elif tag_name == 'a':
                    text_parts.append(child.get_text(strip=True))
                elif tag_name == 'strong' or tag_name == 'b':
                    text_parts.append(f"**{child.get_text(strip=True)}**")
                elif tag_name == 'br':
                    text_parts.append("\n")
                else:
                    # 递归处理其他块级元素
                    text_parts.append(self._clean_html_element(child))
            elif child.string:
                text_parts.append(child.string)
        return ''.join(text_parts).strip()

    def extract_qa_from_article(self, url: str, html_content: str) -> List[Dict[str, str]]:
        """
        从一篇文章中尝试提取 Q&A 对。
        将 <h2> 或 <h3> 标签的内容识别为“问题”，将其后直到下一个 <h2>/<h3> 之前的内容视为“答案”。
        """
        article_qa = []
        if not html_content:
            return article_qa

        soup = BeautifulSoup(html_content, 'html.parser')

        # 1. 定位文章主要内容区域
        main_content = soup.find('div', class_='theme-hope-content') or soup.find('article') or soup.find('main')
        if not main_content:
            print(f"  [Warning] 无法定位文章主体内容区域: {url}")
            return article_qa

        # 2. 获取文章主标题和分类
        article_title_tag = soup.find('h1')
        article_title = article_title_tag.get_text(strip=True) if article_title_tag else "Unknown Article"
        # 简单从URL路径推断分类
        category = "未分类"
        for cat in ['java', 'jvm', 'collection', 'concurrent', 'spring', 'database', 'redis', 'network',
                    'system-design', 'os']:
            if f'/{cat}/' in url:
                category = cat.upper()
                break

        # 3. 查找所有可能的“问题”标题 (h2, h3)
        # 注意：有些 h2 可能是文章内部的大章节标题，不一定都是题目。这里做通用处理。
        all_headings = main_content.find_all(['h2', 'h3'])

        for i, heading in enumerate(all_headings):
            question_text = heading.get_text(strip=True)
            # 简单过滤：跳过太短或明显不是问题的标题（如“目录”、“参考资料”）
            if len(question_text) < 4 or any(
                    word in question_text.lower() for word in ['目录', '参考', 'footer', 'nav', '评论']):
                continue

            # 4. 提取“答案”：从当前标题的下一个兄弟节点开始，直到遇到下一个同级或更高级的标题
            answer_elements = []
            current_element = heading.next_sibling

            while current_element and not (isinstance(current_element, Tag) and current_element.name in ['h2',
                                                                                                         'h3'] and current_element in all_headings):
                if isinstance(current_element, Tag):
                    # 跳过导航、广告等无关元素
                    if current_element.name in ['nav', 'aside', 'footer', 'header', 'script', 'style']:
                        pass
                    else:
                        answer_elements.append(current_element)
                current_element = current_element.next_sibling

            # 5. 将答案元素合并、清理
            if answer_elements:
                # 创建一个临时的容器来存放答案元素
                answer_container = soup.new_tag("div")
                for elem in answer_elements:
                    answer_container.append(elem)

                answer_text = self._clean_html_element(answer_container)
            else:
                answer_text = "（未提取到明确答案内容）"

            # 6. 构建一个 Q&A 字典
            qa_pair = {
                "id": f"{hash(url)}_{i}",
                "source_url": url,
                "article_title": article_title,
                "category": category,
                "question": question_text,
                "answer": answer_text,
                "raw_html_snippet": str(heading) + (''.join(
                    str(e) for e in answer_elements) if answer_elements else "")[:500] + "..."  # 保留一小段原始HTML供核查
            }
            article_qa.append(qa_pair)
            print(f"    [Q&A] 发现题目: {question_text[:50]}...")

        return article_qa

    def crawl_and_extract(self, start_url=None, max_articles=30):
        """
        主爬取流程
        :param max_articles: 最大爬取的文章数量
        """
        to_visit = [start_url or self.base_url]
        articles_processed = 0

        print("=" * 50)
        print("开始爬取并提取 Java 面试题 Q&A")
        print("=" * 50)

        while to_visit and articles_processed < max_articles:
            current_url = to_visit.pop(0)

            if current_url in self.visited_urls:
                continue
            self.visited_urls.add(current_url)

            html = self.fetch_page(current_url)
            if not html:
                continue

            # 判断当前URL是否为可能包含面试题的文章页
            is_article_page = any(path in current_url for path in (
            '/java/', '/jvm/', '/collection/', '/concurrent/', '/spring/', '/database/', '/redis/', '/network/',
            '/system-design/', '/os/'))
            is_homepage = current_url.rstrip('/') == self.base_url.rstrip('/')

            qa_from_page = []
            if is_article_page:
                # 从文章页提取 Q&A
                qa_from_page = self.extract_qa_from_article(current_url, html)
                if qa_from_page:
                    self.qa_list.extend(qa_from_page)
                    articles_processed += 1
                    print(
                        f"  [Info] 已处理文章 {articles_processed}/{max_articles}， 本页提取到 {len(qa_from_page)} 个Q&A。")
            elif is_homepage:
                # 首页：提取可能存在的面试题链接
                print("  [Info] 正在从首页提取文章链接...")
                soup = BeautifulSoup(html, 'html.parser')
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    full_url = urljoin(current_url, href)
                    if (self.is_valid_url(full_url) and
                            any(path in full_url for path in (
                            '/java/', '/jvm/', '/collection/', '/concurrent/', '/spring/', '/database/', '/redis/',
                            '/network/', '/system-design/', '/os/')) and
                            full_url not in self.visited_urls and
                            full_url not in to_visit):
                        to_visit.append(full_url)
                print(f"  [Info] 已将 {len(to_visit)} 个文章链接加入队列。")

            # 保存阶段性结果（可选，防止意外中断）
            if len(self.qa_list) % 20 == 0 and len(self.qa_list) > 0:
                self._save_to_json()

        # 最终保存
        self._save_to_json()
        print("\n" + "=" * 50)
        print(f"爬取与提取完成！")
        print(f"共处理 {articles_processed} 篇文章，提取到 {len(self.qa_list)} 个潜在的 Q&A 对。")
        print(f"结果已保存至: {os.path.abspath(self.output_json)}")
        print("=" * 50)

    def _save_to_json(self):
        """将提取到的 Q&A 列表保存为 JSON 文件。"""
        with open(self.output_json, 'w', encoding='utf-8') as f:
            # ensure_ascii=False 确保中文正常显示，indent=2 美化格式
            json.dump(self.qa_list, f, ensure_ascii=False, indent=2)
        print(f"  [Saved] 已保存 {len(self.qa_list)} 条记录到 {self.output_json}")


# --- 主程序入口 ---
if __name__ == '__main__':
    crawler = JavaGuideQACrawler(
        base_url="https://javaguide.cn/",
        output_json="javaguide_interview.json"  # 指定输出 JSON 文件名
    )

    # 参数说明：
    # start_url: 可以从特定分类开始，如 "https://javaguide.cn/java/basis/"
    # max_articles: 限制处理多少篇“文章”。请务必设置一个较小的数字（如5-10）进行测试。
    crawler.crawl_and_extract(start_url="https://javaguide.cn/", max_articles=5)