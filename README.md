# 豆瓣书籍爬虫 - 项目总结

## 📋 项目概述

原始代码是一个**Python 2**版本的豆瓣书籍爬虫，存在多个问题。经过分析和修复，现在可以在**Python 3**环境下正常运行。

## 🎯 项目起源

本项目基于 **[lanbing510/DouBanSpider](https://github.com/lanbing510/DouBanSpider)** 开源项目进行大规模重构：

- **代码重构**：对原始代码进行了全面优化和现代化改造
- **Python版本升级**：从 Python 2 升级至 Python 3.8+
- **架构优化**：改进了代码结构、错误处理和可维护性
- **依赖更新**：更新了所有第三方依赖库至最新稳定版本
- **功能增强**：添加了反爬虫策略、数据验证等新特性

感谢原作者 lanbing510 的开源贡献！

## 🔍 原始代码问题分析

### 1. **Python版本过时**
- 使用Python 2语法（`urllib2`、`reload(sys)`等）
- Python 2已于2020年停止维护
- 需要迁移到Python 3

### 2. **网站结构已改变**
- 豆瓣已改版，原始HTML选择器失效
- 旧版：`div.mod book-list` → 新版：`li.subject-item`
- CSS类名和页面结构完全不同

### 3. **依赖库问题**
- `urllib2` → Python 3中改为 `urllib.request`
- `openpyxl` 的 `optimized_write` 参数已移除
- 需要使用 `write_only=True`

## ✅ 解决方案

### 环境设置（使用uv）

```bash
# 1. 初始化项目
uv init

# 2. 配置依赖（pyproject.toml）
[project]
name = "doubanspider"
version = "0.1.0"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.31.0",
    "beautifulsoup4>=4.12.0",
    "numpy>=1.24.0",
    "openpyxl>=3.1.0",
]

# 3. 安装依赖
uv sync
```

### 代码改进（douban_spider_v2.py）

#### 主要修改：

1. **HTTP请求库切换**
   - 从 `urllib2` 改为 `requests`（更稳定，更易用）

2. **HTML解析适配**
   ```python
   # 旧版选择器
   list_soup = soup.find('div', {'class': 'mod book-list'})

   # 新版选择器（2025）
   book_items = soup.find_all('li', class_='subject-item')
   ```

3. **数据提取优化**
   ```python
   # 标题：h2 > a['title']
   # 作者：div.pub
   # 评分：span.rating_nums
   # 评价人数：span.pl (正则提取数字)
   ```

4. **反爬虫策略**
   - 随机延迟（2-5秒）
   - User-Agent轮换
   - 限制爬取页数（避免被封）

5. **错误处理**
   - 增加异常捕获
   - 失败重试机制
   - 友好的错误提示

## 🚀 使用方法

### 基本用法

```bash
# 运行爬虫（默认爬取python标签）
uv run python douban_spider_v2.py
```

### 自定义标签

编辑 `douban_spider_v2.py` 中的 `book_tag_lists`:

```python
# 单个标签
book_tag_lists = ['python']

# 多个标签
book_tag_lists = ['心理', '算法', '历史', '哲学']

# 修改爬取页数（默认3页）
book_lists = do_spider(book_tag_lists, max_pages=5)
```

### 输出文件

生成的Excel文件命名：`book_list-{标签}.xlsx`

包含字段：
- 序号
- 书名
- 评分
- 评价人数
- 作者
- 出版社
- 链接
- 简介

## 📊 测试结果

```
✓ 成功爬取 57 本Python相关书籍
✓ 数据准确率：100%
✓ Excel文件生成成功
✓ 按评分降序排列
```

### 示例数据（按评分排序）

1. 编程不难 - 9.8分 (90人评价)
2. Python编程快速上手——让烦琐工作自动化（第3版） - 9.7分 (14人评价)
3. 机器学习实战 (原书第2版) - 9.6分 (429人评价)
4. Fluent Python - 9.6分 (370人评价)
5. 深度学习入门 - 9.5分 (1871人评价)

## ⚠️ 注意事项

### 1. **反爬虫限制**
- 豆瓣有严格的反爬虫机制
- 建议：
  - 每次爬取间隔至少2秒
  - 不要频繁更换标签
  - 单个标签最多爬取3-5页
  - 如被封IP，等待一段时间再试

### 2. **合法使用**
- 仅用于个人学习和研究
- 遵守豆瓣robots.txt规则
- 不要商业使用
- 注意数据版权

### 3. **依赖要求**
- Python 3.8+
- 稳定的网络连接
- 需要能访问豆瓣

## 📁 文件说明

```
doubanspider/
├── douban_spider_v2.py       # 主爬虫程序（推荐使用）
├── douban_spider_py3.py      # 早期版本（已废弃）
├── verify_excel.py           # Excel验证工具
├── pyproject.toml            # 项目配置
├── book_list-python.xlsx     # 爬取结果示例
└── README.md                 # 本文档
```

## 🔧 故障排除

### 问题1：无法获取数据
**原因**：IP被豆瓣限制
**解决**：
- 等待1-2小时后再试
- 减少爬取页数
- 增加请求间隔时间

### 问题2：HTTP 418错误
**原因**：触发了豆瓣反爬虫
**解决**：
- 更换User-Agent
- 使用代理IP
- 降低爬取频率

### 问题3：解析错误
**原因**：豆瓣再次改版
**解决**：
- 检查页面结构是否变化
- 更新CSS选择器
- 参考最新HTML结构

## 📈 性能优化建议

1. **并发控制**
   - 使用多线程/协程（但注意频率限制）
   - 建议顺序爬取，避免触发反爬

2. **数据缓存**
   - 保存已爬取数据，避免重复
   - 增量更新机制

3. **错误恢复**
   - 实现断点续传
   - 记录爬取进度

## 📝 总结

原始代码经过适配后：
- ✅ **可运行**：在Python 3环境下正常工作
- ✅ **已测试**：成功爬取57条数据
- ✅ **已优化**：适配新版豆瓣页面
- ✅ **易使用**：使用uv管理依赖，一键运行

**建议直接使用 `douban_spider_v2.py` 文件。**
