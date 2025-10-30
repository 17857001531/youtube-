# 🎬 YouTube 字幕翻译工具

一个功能强大的 YouTube 视频字幕提取、翻译和展示工具，支持生成精美的交互式 HTML 报告。

## ✨ 功能特点

- 📥 **自动提取字幕** - 支持多语言字幕自动提取
- 🌐 **智能翻译** - 支持 Google 翻译和 DeepSeek AI 翻译
- 📊 **交互式报告** - 生成现代化的 HTML 查看界面
- 🎬 **嵌入式播放器** - 内嵌 YouTube 播放器，字幕与视频同步
- 🔍 **字幕搜索** - 支持原文和译文搜索，快速定位
- 📖 **章节导航** - 自动提取视频章节，快速跳转
- 📝 **AI 总结** - 使用 AI 生成视频内容总结（DeepSeek 模式）
- 🎨 **精美界面** - 知乎风格的现代化 UI 设计

## 🚀 快速开始

### 1. 克隆或下载项目

```bash
git clone https://github.com/yourusername/youtube-translator.git
cd youtube-translator
```

### 2. 运行安装脚本

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```batch
setup.bat
```

或者手动安装：

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置 Streamlit 应用（Web 界面）

#### 3.1 配置 GitHub Token（在线预览功能）

本项目使用 **GitHub Gist** 提供在线预览功能，需要配置 GitHub Token：

1. 访问 https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. 只勾选 `gist` 权限
4. 生成并复制 Token

5. 创建 `.streamlit/secrets.toml` 文件：
```bash
# 将示例文件重命名
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# 编辑文件，填入你的 Token
nano .streamlit/secrets.toml
```

6. 在 `secrets.toml` 中填入：
```toml
GITHUB_TOKEN = "ghp_你的token"
```

**注意：** `.streamlit/secrets.toml` 已在 `.gitignore` 中，不会被提交到 Git。

#### 3.2 启动 Web 应用

```bash
# 启动 Streamlit 应用
streamlit run app.py

# 或指定端口
streamlit run app.py --server.port 8501
```

访问：http://localhost:8501

---

### 4. 配置命令行工具（可选）

#### 方式一：使用 .env 文件（推荐）

```bash
# 将配置模板重命名为 .env
mv env.example.txt .env  # Linux/Mac
# 或
ren env.example.txt .env  # Windows

# 编辑 .env 文件，填入你的配置
nano .env  # 或使用其他编辑器
```

#### 方式二：设置环境变量

```bash
# Linux/Mac
export DEEPSEEK_API_KEY="your_api_key_here"
export YT_DLP_BROWSER="chrome"

# Windows
set DEEPSEEK_API_KEY=your_api_key_here
set YT_DLP_BROWSER=chrome
```

### 5. 使用

#### Streamlit Web 界面（推荐）

直接访问 http://localhost:8501 使用图形界面，无需命令行。

#### 命令行基础用法（使用 Google 翻译）

```bash
python main.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
```

#### 使用 DeepSeek 翻译（推荐，质量更高）

1. 修改 `config.yaml`，将 `translation.provider` 改为 `deepseek`
2. 设置 `DEEPSEEK_API_KEY` 环境变量
3. 运行命令

```bash
python main.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
```

## 📖 命令行参数

```bash
python main.py [参数]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--url` | YouTube 视频链接（必填） | - |
| `--lang` | 目标翻译语言 | zh-CN |
| `--outdir` | 输出目录 | outputs |
| `--source-langs` | 原字幕语言列表（逗号分隔） | en,en-US,en-GB,auto |
| `--config` | 配置文件路径 | config.yaml |
| `--raw-only` | 仅提取原始字幕，不翻译 | False |

### 示例

```bash
# 基础用法
python main.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 指定输出目录和语言
python main.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --lang ja --outdir my_outputs

# 仅提取原始字幕
python main.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --raw-only
```

## 🔑 获取 API Key

### DeepSeek API Key（推荐）

1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/)
2. 注册账号并登录
3. 在控制台创建 API Key
4. 将 Key 配置到 `.env` 文件或环境变量中

**为什么推荐 DeepSeek？**
- ✅ 翻译质量高，语义理解准确
- ✅ 支持 AI 内容总结功能
- ✅ 价格实惠，性价比高

## ⚙️ 配置说明

### config.yaml

主配置文件，用于设置默认参数：

```yaml
# 基本配置
target_language: zh-CN
output_dir: outputs

# 翻译配置
translation:
  provider: google  # google 或 deepseek
  batch_size: 100
  max_retries: 3
  concurrent_workers: 4
```

### 环境变量

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key | 使用 DeepSeek 时必需 | - |
| `DEEPSEEK_BASE_URL` | DeepSeek API 地址 | 否 | https://api.deepseek.com |
| `DEEPSEEK_MODEL` | DeepSeek 模型名称 | 否 | deepseek-chat |
| `DEEPSEEK_TEMPERATURE` | 温度参数 (0-1) | 否 | 0.2 |
| `YT_DLP_BROWSER` | 浏览器名称（用于 Cookie） | 否 | - |

## 📁 输出文件

生成的文件保存在 `outputs/VIDEO_ID/` 目录下：

```
outputs/
└── VIDEO_ID/
    ├── report.html                     # 📊 交互式 HTML 报告（主要输出）
    ├── transcript_raw.json             # 📄 原始字幕 JSON
    ├── transcript_translated.json      # 📄 翻译后字幕 JSON
    ├── VIDEO_ID.info.json              # ℹ️ 视频元信息
    └── VIDEO_ID.en.vtt                 # 📝 原始字幕文件（如有）
```

### HTML 报告功能

- 🎬 内嵌 YouTube 播放器
- 📖 章节导航（自动提取）
- 🔄 中英文字幕切换
- 🔍 字幕搜索功能
- ⏰ 时间轴同步开关
- 📝 AI 内容总结（DeepSeek 模式）
- 🎨 知乎风格的现代化界面

## 🛠️ 故障排除

### 1. 找不到字幕

**问题：** 提示 "未能获取到任何字幕"

**解决方法：**
- 确保视频有字幕（自动生成或手动添加）
- 尝试使用 `--source-langs` 指定其他语言
- 检查视频是否为私有或有地区限制

### 2. DeepSeek API 错误

**问题：** API 调用失败

**解决方法：**
- 检查 API Key 是否正确设置
- 确认账户余额充足
- 检查网络连接，确保能访问 API 地址
- 查看错误信息，根据提示调整

### 3. Cookie 相关问题

**问题：** 无法下载某些视频的字幕

**解决方法：**
- 确保浏览器已登录 YouTube
- 使用 `YT_DLP_BROWSER` 环境变量指定浏览器
- 例如：`export YT_DLP_BROWSER="chrome"`

### 4. 依赖安装失败

**问题：** pip install 报错

**解决方法：**
- 升级 pip：`pip install --upgrade pip`
- 使用国内镜像源（如果在中国）：
  ```bash
  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```

## 📦 依赖说明

主要依赖包：

- `youtube-transcript-api` - YouTube 字幕提取
- `yt-dlp` - YouTube 下载工具
- `deep-translator` - Google 翻译接口
- `openai` - DeepSeek API 客户端
- `python-dotenv` - 环境变量管理
- `PyYAML` - YAML 配置文件解析

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

如果这个项目对你有帮助，请给个 ⭐️ Star 支持一下！

## 📄 许可证

MIT License

## 📮 联系方式

- GitHub Issues: [项目地址]
- Email: [你的邮箱]

## 🙏 致谢

感谢以下开源项目：

- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [deep-translator](https://github.com/nidhaloff/deep-translator)
- [DeepSeek](https://platform.deepseek.com/)

## 📝 更新日志

### v1.0.0 (2025-01-XX)

- ✨ 初始版本发布
- 🎨 知乎风格 UI 设计
- 🌐 支持 Google 和 DeepSeek 翻译
- 📖 章节导航和 AI 总结功能
- 🔍 字幕搜索和同步功能
