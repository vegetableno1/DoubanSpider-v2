# -*- coding: UTF-8 -*-
"""
豆瓣书籍爬虫 - 适配新版豆瓣页面 (2025)
"""

import sys
import time
import urllib.parse
import urllib.request
import random
import re
import numpy as np
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook

# User Agents
hds = [
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
]


def book_spider(book_tag, max_pages=3, min_people=300):
    """
    爬取指定标签的豆瓣书籍信息
    book_tag: 书籍标签
    max_pages: 最多爬取页数（默认3页，避免被封）
    min_people: 最少评价人数（默认300人，低于此数的书籍将被过滤）
    """
    page_num = 0
    book_list = []
    try_times = 0
    max_try_times = 5
    filtered_count = 0  # 统计被过滤的书籍数量

    print(f"\n{'='*60}")
    print(f"开始爬取标签: {book_tag}")
    print(f"筛选条件: 评价人数 >= {min_people} 人")
    print(f"{'='*60}")

    while page_num < max_pages:
        # 构造URL - 新版豆瓣使用20条每页
        url = f'https://book.douban.com/tag/{urllib.parse.quote(book_tag)}?start={page_num * 20}'

        # 随机延迟，避免被封
        sleep_time = random.uniform(2, 5)
        print(f"等待 {sleep_time:.1f} 秒后访问第 {page_num + 1} 页...")
        time.sleep(sleep_time)

        try:
            # 使用requests获取页面（更稳定）
            headers = hds[page_num % len(hds)]
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code != 200:
                print(f"HTTP错误: {response.status_code}")
                break

            plain_text = response.text

        except Exception as e:
            print(f"请求错误: {e}")
            try_times += 1
            if try_times >= max_try_times:
                print(f"连续失败 {max_try_times} 次，停止爬取")
                break
            continue

        # 解析HTML
        soup = BeautifulSoup(plain_text, 'html.parser')

        # 新版豆瓣使用 li.subject-item
        book_items = soup.find_all('li', class_='subject-item')

        if not book_items:
            print(f"第 {page_num + 1} 页未找到书籍信息")
            try_times += 1
            if try_times >= max_try_times:
                break
            continue

        print(f"第 {page_num + 1} 页找到 {len(book_items)} 本书")

        # 解析每本书的信息
        for book_info in book_items:
            try:
                # 获取标题
                title_elem = book_info.find('h2').find('a') if book_info.find('h2') else None
                title = title_elem.get('title', '').strip() if title_elem else '暂无书名'

                # 获取链接
                book_url = title_elem.get('href', '') if title_elem else ''

                # 获取作者/出版社信息
                pub_elem = book_info.find('div', class_='pub')
                if pub_elem:
                    pub_text = pub_elem.get_text().strip()
                    # 格式: [美] 作者 / 译者 / 出版社 / 出版日期 / 价格
                    parts = [p.strip() for p in pub_text.split('/')]

                    if len(parts) >= 3:
                        author = ' / '.join(parts[0:-3]) if len(parts) > 3 else parts[0]
                        publisher_info = ' / '.join(parts[-3:])
                    else:
                        author = pub_text
                        publisher_info = '暂无'
                else:
                    author = '暂无'
                    publisher_info = '暂无'

                # 获取评分
                rating_elem = book_info.find('span', class_='rating_nums')
                rating = rating_elem.get_text().strip() if rating_elem else ''
                rating = rating if rating else '0.0'  # 确保空字符串被替换为 '0.0'

                # 获取评价人数 - 格式: "(25人评价)"
                people_elem = book_info.find('span', class_='pl')
                if people_elem:
                    people_text = people_elem.get_text().strip()
                    # 使用正则提取数字
                    match = re.search(r'(\d+)人评价', people_text)
                    people_num = match.group(1) if match else '0'
                else:
                    people_num = '0'

                # 获取简介（可选）
                desc_elem = book_info.find('p')
                description = desc_elem.get_text().strip() if desc_elem else ''

                # 筛选条件：评价人数 >= min_people
                if int(people_num) >= min_people:
                    book_list.append({
                        'title': title,
                        'rating': rating,
                        'people_num': people_num,
                        'author': author,
                        'publisher': publisher_info,
                        'url': book_url,
                        'description': description[:100] if description else ''  # 只保存前100字
                    })
                else:
                    filtered_count += 1
                    print(f"  ⚠ 过滤: 《{title}》 - 评价人数 {people_num} 人 (<{min_people})")

                try_times = 0  # 重置失败计数

            except Exception as e:
                print(f"解析书籍信息时出错: {e}")
                continue

        page_num += 1

    print(f"\n标签 '{book_tag}' 爬取完成:")
    print(f"  ✓ 收录书籍: {len(book_list)} 本 (评价人数>={min_people})")
    if filtered_count > 0:
        print(f"  ⚠ 过滤书籍: {filtered_count} 本 (评价人数<{min_people})")
    return book_list


def do_spider(book_tag_lists, max_pages=3, min_people=300):
    """
    执行爬虫主程序
    book_tag_lists: 书籍标签列表
    max_pages: 每个标签最多爬取页数
    min_people: 最少评价人数筛选条件
    """
    book_lists = []

    for book_tag in book_tag_lists:
        book_list = book_spider(book_tag, max_pages, min_people)
        # 按评分排序（添加异常处理）
        def safe_rating(book):
            try:
                return float(book['rating'])
            except (ValueError, TypeError):
                return 0.0

        book_list = sorted(book_list, key=safe_rating, reverse=True)
        book_lists.append(book_list)

    return book_lists


def save_to_excel(book_lists, book_tag_lists):
    """将爬取结果保存到Excel文件"""
    wb = Workbook(write_only=True)
    ws_list = []

    # 创建工作表
    for i, book_tag in enumerate(book_tag_lists):
        ws = wb.create_sheet(title=book_tag[:31])  # Excel工作表名称最多31字符
        ws_list.append(ws)

    # 写入数据
    for i, (book_list, book_tag) in enumerate(zip(book_lists, book_tag_lists)):
        ws = ws_list[i]

        # 写入表头
        ws.append(['序号', '书名', '评分', '评价人数', '作者', '出版社', '链接', '简介'])

        # 写入书籍数据
        for count, book in enumerate(book_list, 1):
            try:
                ws.append([
                    count,
                    book['title'],
                    float(book['rating']),
                    int(book['people_num']),
                    book['author'],
                    book['publisher'],
                    book['url'],
                    book['description']
                ])
            except ValueError:
                # 如果数值转换失败，使用原始值
                ws.append([
                    count,
                    book['title'],
                    book['rating'],
                    book['people_num'],
                    book['author'],
                    book['publisher'],
                    book['url'],
                    book['description']
                ])

    # 保存文件
    filename_suffix = '-'.join(book_tag_lists)
    save_path = f'book_list-{filename_suffix}.xlsx'

    wb.save(save_path)
    print(f"\n{'='*60}")
    print(f"✓ 结果已保存到: {save_path}")
    print(f"{'='*60}")

    return save_path


def main():
    """主函数"""
    print("="*60)
    print("豆瓣书籍爬虫 - Python 3 版本 (适配2025新版豆瓣)")
    print("="*60)

    # 测试标签列表（小规模测试）
    #book_tag_lists = ['python']

    # 可以修改这里的标签来爬取不同的书籍分类
    # book_tag_lists = ['个人管理', '时间管理', '投资']
    book_tag_lists = ['心理', '算法', '数据结构']
    # book_tag_lists = ['历史', '哲学', '经济']

    # 筛选条件：最少评价人数（可根据需要修改）
    min_people = 300

    print(f"\n将要爬取的标签: {', '.join(book_tag_lists)}")
    print(f"筛选条件: 只收录评价人数 >= {min_people} 的书籍")
    print(f"注意: 为避免被豆瓣限制，每个标签最多爬取3页\n")

    try:
        # 执行爬虫（每个标签最多3页，只收录评价人数>=300的书籍）
        book_lists = do_spider(book_tag_lists, max_pages=3, min_people=min_people)

        # 统计结果
        total_books = sum(len(books) for books in book_lists)
        print(f"\n{'='*60}")
        print(f"爬取统计:")
        for tag, books in zip(book_tag_lists, book_lists):
            print(f"  - {tag}: {len(books)} 本")
        print(f"  总计: {total_books} 本")
        print(f"{'='*60}")

        if total_books > 0:
            # 保存到Excel
            save_path = save_to_excel(book_lists, book_tag_lists)
            print(f"\n✓ 爬取成功完成！")
        else:
            print("\n✗ 未获取到任何数据")
            print("可能原因:")
            print("  1. 网络连接问题")
            print("  2. IP被豆瓣暂时限制")
            print("  3. 标签名称不存在")

    except KeyboardInterrupt:
        print("\n\n用户中断爬取")
    except Exception as e:
        print(f"\n✗ 爬取过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
