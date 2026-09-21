from bs4 import BeautifulSoup
import time
import json
import requests
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 SLBrowser/9.0.7.12231 SLBChan/115 SLBVPV/64-bit',
    'Referer': 'https://lingtiku.com/',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br'
}


def get_questions(base_url, max_pages=20):
    """
    从灵题库爬取前端面试题
    Args:
        base_url: 基础URL，例如 "https://lingtiku.com/frontend"
        max_pages: 最大爬取页数
    Returns:
        题目列表
    """
    questions = []

    for page in range(1, max_pages + 1):
        try:
            # 构建页面URL - 根据实际网站调整
            if '?' in base_url:
                url = f"{base_url}&page={page}"
            else:
                url = f"{base_url}?page={page}"

            print(f"正在爬取第 {page} 页: {url}")

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # 检查HTTP错误

            # 检查编码
            if response.encoding == 'ISO-8859-1':
                response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')

            # 根据灵题库的实际HTML结构调整选择器
            # 以下是可能需要调整的选择器示例
            question_items = soup.select(
                '.question-item, .list-item, .item, .topic, [class*="question"], [class*="topic"]')

            # 如果没有找到通用选择器，尝试其他可能的类名
            if not question_items:
                # 尝试查找可能的题目容器
                possible_selectors = [
                    'div[class*="question"]',
                    'div[class*="topic"]',
                    '.exam-item',
                    '.problem-item',
                    '.content-item'
                ]
                for selector in possible_selectors:
                    question_items = soup.select(selector)
                    if question_items:
                        print(f"使用选择器: {selector}")
                        break

            if not question_items:
                print(f"警告: 第 {page} 页未找到题目，尝试检查网页结构")
                # 保存当前页面HTML用于调试
                with open(f'debug_page_{page}.html', 'w', encoding='utf-8') as f:
                    f.write(soup.prettify())
                continue

            print(f"第 {page} 页找到 {len(question_items)} 个题目")

            for idx, item in enumerate(question_items):
                try:
                    # 提取题目信息 - 根据实际HTML结构调整
                    question_data = {
                        'page': page,
                        'order': idx + 1,
                        'title': '',
                        'content': '',
                        'options': [],
                        'answer': '',
                        'answer_detail': '',  # 详细答案解释
                        'analysis': '',
                        'category': '',
                        'difficulty': '',
                        'source': 'lingtiku.com',
                        'url': url
                    }

                    # 标题（可能是题目名称）
                    title_selectors = ['.title', '.question-title', 'h3', 'h4', '[class*="title"]', '.q-title']
                    for selector in title_selectors:
                        title_elem = item.select_one(selector)
                        if title_elem and title_elem.text.strip():
                            question_data['title'] = title_elem.text.strip()
                            break

                    # 题目内容
                    content_selectors = ['.content', '.question-content', '.desc', '.text', '.q-content']
                    for selector in content_selectors:
                        content_elem = item.select_one(selector)
                        if content_elem and content_elem.text.strip():
                            question_data['content'] = content_elem.text.strip()
                            break

                    # 选项（多选题或单选题）
                    options = []
                    option_selectors = ['.option', '.choice', '.item', 'li', '.answer-item']
                    for selector in option_selectors:
                        option_elems = item.select(selector)
                        if option_elems:
                            options = [opt.text.strip() for opt in option_elems if opt.text.strip()]
                            if options:
                                question_data['options'] = options
                                break

                    # 答案 - 关键部分
                    answer_selectors = [
                        '.answer',
                        '.correct-answer',
                        '.right-answer',
                        '[class*="answer"]',
                        '.solution',
                        '.key',
                        '.result'
                    ]

                    for selector in answer_selectors:
                        answer_elem = item.select_one(selector)
                        if answer_elem and answer_elem.text.strip():
                            answer_text = answer_elem.text.strip()

                            # 清理答案文本
                            answer_text = answer_text.replace('答案：', '').replace('正确答案：', '').strip()

                            # 判断是否为隐藏答案（例如通过CSS隐藏）
                            style = answer_elem.get('style', '').lower()
                            if 'display:none' not in style and 'visibility:hidden' not in style:
                                question_data['answer'] = answer_text

                                # 尝试获取详细答案解释
                                detail_selectors = ['.detail', '.explain', '.analysis-text', '.answer-detail']
                                for detail_selector in detail_selectors:
                                    detail_elem = answer_elem.select_one(detail_selector)
                                    if detail_elem and detail_elem.text.strip():
                                        question_data['answer_detail'] = detail_elem.text.strip()
                                        break

                                break

                    # 解析/分析
                    analysis_selectors = ['.analysis', '.explanation', '.parse', '.comment']
                    for selector in analysis_selectors:
                        analysis_elem = item.select_one(selector)
                        if analysis_elem and analysis_elem.text.strip():
                            question_data['analysis'] = analysis_elem.text.strip()
                            break

                    # 分类
                    category_selectors = ['.category', '.tag', '.type', '.label']
                    for selector in category_selectors:
                        category_elem = item.select_one(selector)
                        if category_elem and category_elem.text.strip():
                            question_data['category'] = category_elem.text.strip()
                            break

                    # 难度
                    difficulty_selectors = ['.difficulty', '.level', '.star']
                    for selector in difficulty_selectors:
                        difficulty_elem = item.select_one(selector)
                        if difficulty_elem and difficulty_elem.text.strip():
                            question_data['difficulty'] = difficulty_elem.text.strip()
                            break

                    # 如果没有找到答案，尝试其他方法
                    if not question_data['answer']:
                        # 方法1：查找可能包含答案的文本模式
                        import re
                        full_text = item.get_text()
                        answer_patterns = [
                            r'答案[：:]\s*([A-D]+|[对错]|正确|错误)',
                            r'正确答案[：:]\s*([A-D]+|[对错]|正确|错误)',
                            r'正确选项[：:]\s*([A-D]+)',
                            r'选择([A-D]+)'
                        ]

                        for pattern in answer_patterns:
                            match = re.search(pattern, full_text, re.IGNORECASE)
                            if match:
                                question_data['answer'] = match.group(1).strip()
                                print(f"通过正则找到答案: {question_data['answer']}")
                                break

                    questions.append(question_data)

                except Exception as e:
                    print(f"处理第 {page} 页第 {idx + 1} 个题目时出错: {e}")
                    continue

            # 打印进度
            print(f"第 {page} 页处理完成，累计 {len(questions)} 个题目")

            # 延迟，避免被屏蔽
            time.sleep(2 + (page % 3))

        except requests.RequestException as e:
            print(f"请求第 {page} 页失败: {e}")
            time.sleep(5)  # 出错后等待更长时间
            continue
        except Exception as e:
            print(f"处理第 {page} 页时出错: {e}")
            time.sleep(3)
            continue

    return questions


def save_questions(questions, json_filename='questions.json', csv_filename='questions.csv'):
    """保存爬取的题目数据"""

    if not questions:
        print("没有爬取到题目数据")
        return

    # 保存为JSON
    try:
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        print(f"数据已保存为JSON文件: {json_filename}")
    except Exception as e:
        print(f"保存JSON文件失败: {e}")

    # 保存为CSV
    try:
        df = pd.DataFrame(questions)

        # 如果options是列表，转换为字符串
        if 'options' in df.columns:
            df['options'] = df['options'].apply(lambda x: '|'.join(x) if isinstance(x, list) else x)

        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"数据已保存为CSV文件: {csv_filename}")

        # 显示数据统计
        print(f"\n数据统计:")
        print(f"总题目数: {len(df)}")
        print(f"有答案的题目数: {df['answer'].notna().sum()}")
        print(f"分类分布:")
        print(df['category'].value_counts() if 'category' in df.columns and not df[
            'category'].isna().all() else "无分类信息")

    except Exception as e:
        print(f"保存CSV文件失败: {e}")


def try_api_crawl():
    """尝试使用API接口爬取数据"""
    api_url = "https://lingtiku.com/api/questions"
    params = {"page": 1, "limit": 50}

    try:
        print("尝试通过API接口获取数据...")
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        # 根据API的实际响应结构调整
        if isinstance(data, dict) and 'questions' in data:
            questions = data['questions']
            print(f"通过API获取到 {len(questions)} 个题目")
            return questions
        elif isinstance(data, list):
            print(f"通过API获取到 {len(data)} 个题目")
            return data
        else:
            print("API返回的数据格式不符合预期")
            return []

    except Exception as e:
        print(f"API请求失败: {e}")
        return []


def main():
    """主函数"""
    print("开始爬取灵题库前端面试题...")

    # 方法1：尝试API（如果可用）
    api_questions = try_api_crawl()

    if api_questions:
        save_questions(api_questions, 'questions_api.json', 'questions_api.csv')
        print("使用API爬取完成")
        return

    # 方法2：使用HTML解析（如果没有API或API不可用）
    print("API不可用，尝试HTML解析...")

    # 需要根据灵题库的实际URL调整
    base_urls = [
        "https://lingtiku.com/frontend",
        "https://lingtiku.com/interview",
        "https://lingtiku.com/questions"
    ]

    all_questions = []

    for base_url in base_urls:
        print(f"\n尝试从 {base_url} 爬取...")
        try:
            questions = get_questions(base_url, max_pages=3)  # 先测试3页
            all_questions.extend(questions)
            print(f"从 {base_url} 爬取到 {len(questions)} 个题目")

            if questions:  # 如果这个URL有效，可以多爬几页
                break

        except Exception as e:
            print(f"从 {base_url} 爬取失败: {e}")
            continue

    # 去重（基于标题和内容）
    if all_questions:
        unique_questions = []
        seen = set()

        for q in all_questions:
            key = f"{q.get('title', '')}_{q.get('content', '')}"[:100]  # 取前100字符作为唯一标识
            if key not in seen:
                seen.add(key)
                unique_questions.append(q)

        print(f"去重前: {len(all_questions)}, 去重后: {len(unique_questions)}")
        all_questions = unique_questions

    # 保存数据
    if all_questions:
        save_questions(all_questions)
        print("爬取完成!")
    else:
        print("未爬取到任何题目，请检查:")
        print("1. 网站URL是否正确")
        print("2. 网络连接是否正常")
        print("3. 网站是否使用了反爬措施")
        print("4. HTML选择器可能需要调整")


if __name__ == "__main__":
    main()