#!/usr/bin/env python3
"""
Python 3.10+ 兼容性测试脚本
在本地测试字幕提取功能是否正常
"""

import sys
print(f"🐍 Python 版本: {sys.version}")
print(f"✅ 主版本: {sys.version_info.major}.{sys.version_info.minor}")
print()

# 检查 Python 版本
if sys.version_info < (3, 10):
    print("❌ 需要 Python 3.10 或更高版本")
    print("💡 请使用以下命令切换 Python 版本：")
    print("   • macOS/Linux: python3.10、python3.11、python3.12 或 python3.13")
    print("   • 或使用虚拟环境：python3.10 -m venv venv310")
    sys.exit(1)

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("📦 检查依赖包")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()

try:
    import youtube_transcript_api
    print(f"✅ youtube-transcript-api 已安装")
except ImportError as e:
    print(f"❌ youtube-transcript-api 未安装: {e}")
    print("💡 运行: pip install -r requirements.txt")
    sys.exit(1)

try:
    import yt_dlp
    print(f"✅ yt-dlp 已安装")
except ImportError as e:
    print(f"❌ yt-dlp 未安装: {e}")
    sys.exit(1)

print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🧪 测试字幕提取功能")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()

# 导入提取模块
from yt_translator.extractor import extract_transcript_with_fallback
import tempfile
import os

# 测试视频
test_videos = [
    ("短视频（18秒）", "https://www.youtube.com/watch?v=jNQXAC9IVRw"),
    ("你的测试视频", "https://www.youtube.com/watch?v=-oy55UWlbdw"),
]

for name, url in test_videos:
    print(f"📹 测试: {name}")
    print(f"🔗 链接: {url}")
    print()
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            items, lang, title, source, chapters = extract_transcript_with_fallback(
                url,
                preferred_langs=['en', 'en-US', 'en-GB', 'auto'],
                workdir=tmpdir
            )
            
            if items:
                print(f"✅ 成功提取字幕！")
                print(f"   • 来源: {source}")
                print(f"   • 语言: {lang}")
                print(f"   • 字幕数: {len(items)}")
                print(f"   • 标题: {title or '未获取'}")
                print(f"   • 章节数: {len(chapters)}")
            else:
                print(f"❌ 未提取到字幕")
    except Exception as e:
        print(f"❌ 提取失败: {str(e)[:200]}")
    
    print()
    print("-" * 60)
    print()

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🎯 测试完成！")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()
print("✅ 如果所有测试都成功，代码已兼容 Python 3.10+")
print("✅ 可以推送到 GitHub，然后在 Streamlit Cloud 重新部署")
print()

