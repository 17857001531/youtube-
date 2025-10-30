# -*- coding: utf-8 -*-

"""
翻译模块：
- provider=google：使用 deep-translator 的 GoogleTranslator（无需 Key）
- provider=deepseek：使用 DeepSeek 大模型 API（需设置环境变量 DEEPSEEK_API_KEY）
- 均支持分批与重试
"""

from __future__ import annotations

import time
from typing import List, Optional, Dict, Tuple

from deep_translator import GoogleTranslator
import os
import json
import time

try:
    from openai import OpenAI
except Exception:  # 避免在未安装 openai 时导入失败
    OpenAI = None  # type: ignore


class SubtitleTranslator:
    """字幕翻译器，支持批量翻译与简单重试。"""

    def __init__(self, target_language: str = 'zh-CN', provider: str = 'google', batch_size: int = 25, max_retries: int = 3, retry_delay_seconds: float = 2.0, concurrent_workers: int = 1) -> None:
        self.target_language = target_language
        self.provider = provider
        self.batch_size = max(1, int(batch_size))
        self.max_retries = max(0, int(max_retries))
        self.retry_delay_seconds = float(retry_delay_seconds)
        self.concurrent_workers = max(1, int(concurrent_workers))

        self._translator_google: Optional[GoogleTranslator] = None
        self._client_deepseek: Optional[OpenAI] = None

        if self.provider == 'google':
            self._translator_google = GoogleTranslator(source='auto', target=self.target_language)
        elif self.provider == 'deepseek':
            if OpenAI is None:
                raise RuntimeError('需要安装 openai 依赖以使用 DeepSeek：pip install openai')
            # 从环境变量读取 API Key
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if not api_key:
                raise RuntimeError(
                    '未检测到 DEEPSEEK_API_KEY 环境变量。\n'
                    '请通过以下方式之一设置：\n'
                    '1. 创建 .env 文件并添加：DEEPSEEK_API_KEY=your_api_key\n'
                    '2. 设置环境变量：export DEEPSEEK_API_KEY="your_api_key"\n'
                    '3. 参考 .env.example 文件中的配置说明'
                )
            base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
            self._client_deepseek = OpenAI(api_key=api_key, base_url=base_url)
            # 模型可通过环境变量配置，默认 deepseek-chat（通用）
            self._deepseek_model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
            self._deepseek_temperature = float(os.getenv('DEEPSEEK_TEMPERATURE', '0.2'))
        else:
            raise ValueError('provider 仅支持 google 或 deepseek')

    def translate_texts(self, texts: List[str]) -> List[str]:
        """按批次翻译文本列表，支持并发与去重缓存。"""
        # 去重缓存：相同文本只翻译一次
        unique_texts: List[str] = []
        index_map: Dict[int, int] = {}  # 原索引 -> unique 索引
        text_to_unique_index: Dict[str, int] = {}
        for idx, t in enumerate(texts):
            if t in text_to_unique_index:
                index_map[idx] = text_to_unique_index[t]
            else:
                uidx = len(unique_texts)
                unique_texts.append(t)
                text_to_unique_index[t] = uidx
                index_map[idx] = uidx

        # 将 unique_texts 分批
        batches: List[Tuple[int, List[str]]] = []  # (起始 unique 索引, 批内容)
        for i in range(0, len(unique_texts), self.batch_size):
            batches.append((i, unique_texts[i:i + self.batch_size]))

        # 并发处理各批
        if self.provider == 'google':
            assert self._translator_google is not None
            from concurrent.futures import ThreadPoolExecutor, as_completed

            translated_unique: List[Optional[str]] = [None] * len(unique_texts)

            def work(start_index: int, batch: List[str]) -> Tuple[int, List[str]]:
                for attempt in range(self.max_retries + 1):
                    try:
                        out = self._translator_google.translate_batch(batch)
                        if isinstance(out, str):
                            out = [out]
                        return start_index, out
                    except Exception:
                        if attempt >= self.max_retries:
                            return start_index, batch
                        time.sleep(self.retry_delay_seconds)

            with ThreadPoolExecutor(max_workers=self.concurrent_workers) as ex:
                futures = [ex.submit(work, s, b) for s, b in batches]
                for fut in as_completed(futures):
                    s, out = fut.result()
                    for j, val in enumerate(out):
                        translated_unique[s + j] = val

            # 还原到原顺序
            results: List[str] = []
            for idx in range(len(texts)):
                uidx = index_map[idx]
                val = translated_unique[uidx]
                results.append(val if val is not None else texts[idx])
            return results

        # DeepSeek 模式并发
        return self._translate_with_deepseek_concurrent(unique_texts, index_map, texts)

    def _translate_with_deepseek_concurrent(self, unique_texts: List[str], index_map: Dict[int, int], original_texts: List[str]) -> List[str]:
        assert self._client_deepseek is not None
        from concurrent.futures import ThreadPoolExecutor, as_completed
        translated_unique: List[Optional[str]] = [None] * len(unique_texts)
        system_prompt = (
            "你是专业的字幕翻译助手。严格输出要求：\n"
            "1) 将每一行字幕翻译为 ${target}（中文），保持原意、术语与专有名词。\n"
            "2) 不添加任何解释/标点修饰/序号；不合并或拆分行；不丢行。\n"
            "3) 如果输入行为空或是仅含噪声标记，输出相应的空行或纯噪声去除后的结果。\n"
            "4) 仅输出译文本身（逐行对应输入），不要代码块、不要前后缀。"
        ).replace('${target}', self.target_language)

        def work(start_index: int, batch: List[str]) -> Tuple[int, List[str]]:
            content = (
                "请将以下多行字幕逐行翻译为中文（目标语言：" + self.target_language + ")。"\
                "严格保持行数一致与顺序对应，只输出译文，不要任何额外文本。\n\n"\
                "<INPUT>\n" + "\n".join(batch) + "\n</INPUT>\n"
            )
            for attempt in range(self.max_retries + 1):
                try:
                    resp = self._client_deepseek.chat.completions.create(
                        model=self._deepseek_model,
                        temperature=self._deepseek_temperature,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": content},
                        ],
                        timeout=60,
                    )
                    text = resp.choices[0].message.content.strip()
                    if text.startswith("```"):
                        parts = text.split("\n", 1)
                        text = parts[1] if len(parts) > 1 else ''
                        if text.endswith("```"):
                            text = text.rsplit("\n", 1)[0]
                    lines = [ln.strip() for ln in text.split("\n")]
                    if len(lines) < len(batch):
                        lines += batch[len(lines):]
                    if len(lines) > len(batch):
                        lines = lines[:len(batch)]
                    return start_index, lines
                except Exception:
                    if attempt >= self.max_retries:
                        return start_index, batch
                    time.sleep(self.retry_delay_seconds)

        # 构造并发任务
        batches: List[Tuple[int, List[str]]] = []
        for i in range(0, len(unique_texts), self.batch_size):
            batches.append((i, unique_texts[i:i + self.batch_size]))

        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=self.concurrent_workers) as ex:
            futures = [ex.submit(work, s, b) for s, b in batches]
            from time import time as _now
            start_ts = _now()
            for fut in as_completed(futures):
                s, out = fut.result()
                for j, val in enumerate(out):
                    translated_unique[s + j] = val
                # 简单进度日志
                done = sum(1 for v in translated_unique if v is not None)
                total = len(translated_unique)
                print(f".. 翻译进度 {done}/{total} ({done*100//max(1,total)}%)", flush=True)

        # 还原原顺序
        results: List[str] = []
        for idx in range(len(original_texts)):
            uidx = index_map[idx]
            val = translated_unique[uidx]
            results.append(val if val is not None else original_texts[idx])
        return results

    def translate_items(self, items: List[dict]) -> List[str]:
        """翻译字幕条目列表，仅翻译 text 字段。"""
        texts = [item.get('text', '') for item in items]
        return self.translate_texts(texts)

    def translate_full_and_split(self, full_text: str) -> List[str]:
        """
        将整段英文字幕提交给提供方，请求生成按语义分段的中文段落列表。
        返回分段后的中文段落（每段一项，去除空段）。
        仅 provider=deepseek 实现此能力；google 模式下退化为逐句粗略分段。
        """
        if not full_text.strip():
            return []
        if self.provider == 'google':
            # 粗略分段：按两个换行或句号分段，再调用批量翻译
            import re
            rough = [seg.strip() for seg in re.split(r"\n\n+|(?<=[.!?])\s+", full_text) if seg.strip()]
            return self.translate_texts(rough)

        assert self._client_deepseek is not None
        system_prompt = (
            "你是专业的中英翻译与编辑。请将用户提供的整段英文字幕翻译成中文，并按语义自动分段。\n"
            "要求：\n"
            "1) 输出仅包含中文段落，每段一行，中间用一个空行分隔。\n"
            "2) 不要保留原文，不要添加任何解释或编号，不要代码块标记。\n"
            "3) 尽量合并零散短句，保证上下文连贯、断句自然。\n"
        )
        user_prompt = (
            "以下是完整的英文字幕内容：\n<INPUT>\n" + full_text.strip() + "\n</INPUT>\n" \
            "请直接输出中文段落，段落之间空一行。"
        )
        for attempt in range(self.max_retries + 1):
            try:
                resp = self._client_deepseek.chat.completions.create(
                    model=self._deepseek_model,
                    temperature=self._deepseek_temperature,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    timeout=120,
                )
                text = resp.choices[0].message.content.strip()
                if text.startswith("```"):
                    parts = text.split("\n", 1)
                    text = parts[1] if len(parts) > 1 else ''
                    if text.endswith("```"):
                        text = text.rsplit("\n", 1)[0]
                # 分段：以空行分隔
                raw_paras = [p.strip() for p in text.split("\n\n")]
                return [p for p in raw_paras if p]
            except Exception:
                if attempt >= self.max_retries:
                    return [full_text]
                time.sleep(self.retry_delay_seconds)

    def generate_summary(self, full_text: str) -> str:
        """
        基于完整原文生成归纳总结。
        返回中文总结文本。
        仅 provider=deepseek 支持此功能；google 模式返回简单提示。
        """
        if not full_text.strip():
            return "暂无内容可供总结"
        
        if self.provider == 'google':
            # Google 翻译不支持总结功能
            return "总结功能需要使用 DeepSeek 作为翻译提供方。当前使用的是 Google 翻译。"
        
        assert self._client_deepseek is not None
        system_prompt = (
            "你是专业的内容分析与总结助手。请基于用户提供的完整英文字幕内容，生成一个结构化的中文总结。\n"
            "要求：\n"
            "1) 总结应包含：核心主题、关键要点、主要论点/观点\n"
            "2) 使用清晰的段落结构，用小标题或序号组织内容\n"
            "3) 保持客观准确，不添加个人观点\n"
            "4) 长度控制在 300-500 字左右\n"
            "5) 使用通俗易懂的语言，避免过度技术化"
        )
        user_prompt = (
            "以下是完整的英文字幕内容，请为其生成一个结构化的中文总结：\n\n"
            "<INPUT>\n" + full_text.strip() + "\n</INPUT>\n\n"
            "请直接输出中文总结，使用段落和标题组织内容。"
        )
        
        for attempt in range(self.max_retries + 1):
            try:
                resp = self._client_deepseek.chat.completions.create(
                    model=self._deepseek_model,
                    temperature=self._deepseek_temperature,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    timeout=120,
                )
                summary = resp.choices[0].message.content.strip()
                # 移除可能的代码块标记
                if summary.startswith("```"):
                    parts = summary.split("\n", 1)
                    summary = parts[1] if len(parts) > 1 else ''
                    if summary.endswith("```"):
                        summary = summary.rsplit("\n", 1)[0]
                return summary.strip()
            except Exception as e:
                if attempt >= self.max_retries:
                    return f"生成总结失败：{str(e)}"
                time.sleep(self.retry_delay_seconds)
        
        return "生成总结失败：超过最大重试次数"

    def translate_title(self, title: str) -> str:
        """
        翻译视频标题。
        返回中文翻译。
        """
        if not title.strip():
            return ""
        
        if self.provider == 'google':
            try:
                return self._translator_google.translate(title)
            except Exception:
                return title
        
        assert self._client_deepseek is not None
        system_prompt = "你是专业的翻译助手。请将用户提供的英文标题翻译成中文，保持简洁准确。只输出翻译结果，不要任何解释。"
        user_prompt = f"请将以下标题翻译成中文：\n{title}"
        
        for attempt in range(self.max_retries + 1):
            try:
                resp = self._client_deepseek.chat.completions.create(
                    model=self._deepseek_model,
                    temperature=0.1,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    timeout=30,
                )
                return resp.choices[0].message.content.strip()
            except Exception:
                if attempt >= self.max_retries:
                    return title
                time.sleep(self.retry_delay_seconds)
        return title

    def translate_chapters(self, chapters: List[Dict]) -> List[Dict]:
        """
        翻译章节标题。
        返回带有中文翻译的章节列表。
        """
        if not chapters:
            return []
        
        # 提取所有章节标题
        titles = [ch.get('title', '') for ch in chapters]
        if not titles:
            return chapters
        
        if self.provider == 'google':
            try:
                translated_titles = self.translate_texts(titles)
                for i, ch in enumerate(chapters):
                    ch['title_cn'] = translated_titles[i] if i < len(translated_titles) else ch.get('title', '')
                return chapters
            except Exception:
                for ch in chapters:
                    ch['title_cn'] = ch.get('title', '')
                return chapters
        
        assert self._client_deepseek is not None
        system_prompt = (
            "你是专业的翻译助手。请将用户提供的英文章节标题逐行翻译成中文。\n"
            "要求：\n"
            "1) 每行对应一个章节标题的翻译\n"
            "2) 保持简洁准确，符合中文表达习惯\n"
            "3) 不要添加序号、解释或其他内容\n"
            "4) 严格保持行数一致"
        )
        user_prompt = "请将以下章节标题逐行翻译成中文：\n\n" + "\n".join(titles)
        
        for attempt in range(self.max_retries + 1):
            try:
                resp = self._client_deepseek.chat.completions.create(
                    model=self._deepseek_model,
                    temperature=0.1,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    timeout=60,
                )
                text = resp.choices[0].message.content.strip()
                translated_lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                # 匹配翻译结果到章节
                for i, ch in enumerate(chapters):
                    if i < len(translated_lines):
                        ch['title_cn'] = translated_lines[i]
                    else:
                        ch['title_cn'] = ch.get('title', '')
                return chapters
            except Exception:
                if attempt >= self.max_retries:
                    for ch in chapters:
                        ch['title_cn'] = ch.get('title', '')
                    return chapters
                time.sleep(self.retry_delay_seconds)
        
        for ch in chapters:
            ch['title_cn'] = ch.get('title', '')
        return chapters




