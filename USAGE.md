# 快速使用指南

## 一键运行

```bash
./run.sh
```

## 手动运行

```bash
# 1. 安装依赖（首次运行）
uv sync

# 2. 运行爬虫
uv run python douban_spider_v2.py
```

## 修改爬取标签

编辑 `douban_spider_v2.py` 文件的第177行：

```python
# 单个标签
book_tag_lists = ['python']

# 多个标签（推荐一次只爬1-2个标签）
book_tag_lists = ['心理', '算法']
```

## 查看结果

爬取完成后，会生成 `book_list-{标签}.xlsx` 文件：

```bash
# 验证Excel内容
uv run python verify_excel.py

# 或用Excel打开
xdg-open book_list-python.xlsx  # Linux
start book_list-python.xlsx     # Windows
open book_list-python.xlsx      # macOS
```

## 常用标签参考

```
编程类：python, java, javascript, 算法, 数据结构
人文类：历史, 哲学, 心理, 经济
科学类：数学, 物理, 生物, 科普
生活类：旅行, 美食, 摄影, 设计
```

## 注意事项

⚠️ **不要频繁爬取**
- 每个标签最多爬取3-5页
- 爬取间隔至少2-5秒
- 避免同时爬取多个标签

⚠️ **遵守规则**
- 仅用于个人学习
- 不要商业使用
- 尊重网站规则

## 故障排除

### 1. uv: command not found
```bash
# 安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 爬取失败（0条数据）
- 等待1-2小时后再试
- 检查网络连接
- 减少爬取页数

### 3. HTTP 418/403错误
- IP被暂时限制
- 更换网络环境
- 等待一段时间

## 获取帮助

查看详细文档：
```bash
cat README.md
```
