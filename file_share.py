# -*- coding: utf-8 -*-

"""
文件分享模块：使用 GitHub Gist 托管 HTML 文件
"""

import requests
import streamlit as st
import time
from typing import Optional


def get_github_token() -> Optional[str]:
    """
    获取 GitHub Token
    
    Returns:
        GitHub Token，如果未配置返回 None
    """
    try:
        if hasattr(st, 'secrets') and 'GITHUB_TOKEN' in st.secrets:
            return st.secrets['GITHUB_TOKEN']
        else:
            print("⚠️ 未配置 GITHUB_TOKEN")
            return None
    except Exception as e:
        print(f"⚠️ 获取 GitHub Token 失败: {str(e)}")
        return None


def upload_to_github_gist(html_content: str, filename: str) -> Optional[str]:
    """
    上传 HTML 到 GitHub Gist
    
    Args:
        html_content: HTML 内容
        filename: 文件名
        
    Returns:
        公开可访问的 HTML 预览 URL，失败返回 None
    """
    try:
        token = get_github_token()
        if not token:
            return None
        
        # 创建 Gist
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        payload = {
            'description': f'YouTube Translator Report - {filename}',
            'public': True,  # 公开 Gist
            'files': {
                filename: {
                    'content': html_content
                }
            }
        }
        
        response = requests.post(
            'https://api.github.com/gists',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        # 提取 Gist ID
        gist_id = data['id']
        
        # 获取原始 HTML URL
        raw_url = data['files'][filename]['raw_url']
        
        # 使用 HTMLPreview 服务来正确渲染 HTML
        # GitHub raw URL 默认是 text/plain，不会渲染 HTML
        # HTMLPreview 会将其转换为可渲染的网页
        preview_url = f"https://htmlpreview.github.io/?{raw_url}"
        
        print(f"✅ 文件已上传到 GitHub Gist")
        print(f"   Gist ID: {gist_id}")
        print(f"   Gist URL: {data['html_url']}")
        print(f"   预览 URL: {preview_url}")
        
        return {
            'url': preview_url,
            'gist_id': gist_id
        }
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(f"❌ GitHub Token 无效或已过期")
        elif e.response.status_code == 403:
            print(f"❌ GitHub API 限额已用完（每小时 5000 次）")
        else:
            print(f"❌ GitHub API 错误 [{e.response.status_code}]: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络错误: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ 上传失败: {str(e)}")
        return None


def create_shareable_link(html_content: str, video_id: str) -> dict:
    """
    创建可分享的 HTML 链接（使用 GitHub Gist）
    
    Args:
        html_content: HTML 内容
        video_id: 视频 ID
        
    Returns:
        包含链接信息的字典
    """
    timestamp = int(time.time())
    filename = f"yt_report_{video_id}_{timestamp}.html"
    
    # 上传到 GitHub Gist
    result = upload_to_github_gist(html_content, filename)
    
    if result:
        return {
            'success': True,
            'url': result['url'],
            'gist_id': result['gist_id'],
            'expires': '永久有效',
            'service': 'GitHub Gist',
            'message': '✅ 在线链接生成成功'
        }
    else:
        return {
            'success': False,
            'url': None,
            'gist_id': None,
            'expires': None,
            'service': None,
            'message': '❌ 链接生成失败，请检查网络或 GitHub Token'
        }


def delete_gist(gist_id: str) -> bool:
    """
    删除 Gist（可选功能，用于清理旧文件）
    
    Args:
        gist_id: Gist ID
        
    Returns:
        是否删除成功
    """
    try:
        token = get_github_token()
        if not token:
            return False
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.delete(
            f'https://api.github.com/gists/{gist_id}',
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        print(f"🗑️ 已删除 Gist: {gist_id}")
        return True
        
    except Exception as e:
        print(f"⚠️ 删除 Gist 失败: {str(e)}")
        return False
