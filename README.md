# 小红书内容提取工具

这是一个用于搜索和提取小红书内容的Python工具。

## 功能特点

- 搜索小红书笔记
- 提取笔记内容、图片和评论
- 支持数据导出

## 安装

1. 克隆仓库：
```bash
git clone [repository-url]
cd xiaohongshu_agent
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 安装 Playwright 浏览器：
```bash
playwright install firefox
```

4. 配置文件：
   - 复制 `config.example.py` 为 `config.py`
   - 填入必要的配置信息（如 Cookie 等）

## 获取 Cookie

要使用本工具，你需要获取小红书网页版的 Cookie。以下是获取步骤：

1. 使用 Chrome 或 Firefox 浏览器访问 [小红书网页版](https://www.xiaohongshu.com)
2. 登录你的小红书账号
3. 打开浏览器开发者工具（按 F12 或右键点击 -> 检查）
4. 切换到 Network（网络）标签页
5. 在网页上进行任意操作（如搜索、点击笔记等）
6. 在 Network 标签页中找到任意一个请求
7. 在请求头（Headers）中找到 Cookie 字段
8. 复制整个 Cookie 字段的内容
9. 将复制的内容粘贴到 `config.py` 文件的 `XHS_COOKIE` 字段中

注意事项：
- Cookie 通常包含你的登录凭证，请勿分享给他人
- Cookie 有一定的有效期，过期后需要重新获取
- 建议使用小号登录，避免主账号被限制

## 使用方法

运行脚本：
```bash
python src/main.py -k "关键词" -p 1
```

参数说明：
- `-k` 或 `--keyword`: 搜索关键词（必需）
- `-p` 或 `--pages`: 要爬取的页数（默认为1）
- `-c` 或 `--config`: 配置文件路径（默认为 config.py）

## 注意事项

- 请遵守小红书的使用条款和服务协议
- 合理设置爬取频率，避免对服务器造成压力
- 仅用于个人研究和学习用途
- 首次使用前需要在配置文件中填入有效的 Cookie

## 免责声明

本工具仅供学习和研究使用，请勿用于商业用途。使用本工具产生的任何问题由使用者自行承担。 