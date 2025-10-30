# -*- coding: utf-8 -*-

"""
HTML 报告生成模块：
- 生成带时间轴的交互式字幕列表
- 内嵌 YouTube 播放器
- 点击字幕跳转到对应时间点
"""

from __future__ import annotations

import html
from typing import List, Dict, Optional
from string import Template


def _format_time(seconds: float) -> str:
    """将秒格式化为 mm:ss 或 hh:mm:ss。"""
    s = int(seconds)
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    if h:
        return f"{h:02d}:{m:02d}:{sec:02d}"
    return f"{m:02d}:{sec:02d}"


class HtmlReportGenerator:
    """生成 HTML 报告文件，支持英文/中文双轨切换。"""

    def generate(self, output_path: str, video_id: str, title: Optional[str], title_cn: str, items_en: List[Dict], items_cn: List[Dict], chapters: List[Dict], summary: str, source_language: Optional[str], target_language: Optional[str]) -> None:
        safe_title = title or f"YouTube 视频 {video_id}"
        # 英文轨
        rows_en: List[str] = []
        for it in items_en:
            start = float(it.get('start', 0))
            duration = float(it.get('duration', 5.0))
            text = html.escape(it.get('text', ''))
            rows_en.append(
                f'<div class="cue" data-start="{start}" data-duration="{duration}">'
                f'<div class="time">{_format_time(start)}</div>'
                f'<div class="orig">{text}</div>'
                f'</div>'
            )
        # 中文轨
        rows_cn: List[str] = []
        for it in items_cn:
            start = float(it.get('start', 0))
            duration = float(it.get('duration', 5.0))
            translated = html.escape(it.get('translated_text', ''))
            rows_cn.append(
                f'<div class="cue" data-start="{start}" data-duration="{duration}">'
                f'<div class="time">{_format_time(start)}</div>'
                f'<div class="tran">{translated}</div>'
                f'</div>'
            )
        
        # 生成章节导航
        chapters_html: List[str] = []
        for ch in chapters:
            ch_start = float(ch.get('start_time', 0))
            ch_title = html.escape(ch.get('title', '未命名章节'))
            ch_title_cn = html.escape(ch.get('title_cn', ''))
            # 如果有中文翻译，用括号连接
            if ch_title_cn:
                display_title = f'{ch_title} ({ch_title_cn})'
            else:
                display_title = ch_title
            chapters_html.append(
                f'<div class="chapter" data-start="{ch_start}">'
                f'<div class="ch-time">{_format_time(ch_start)}</div>'
                f'<div class="ch-title">{display_title}</div>'
                f'</div>'
            )

        template = Template(
            """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$page_title - 字幕翻译报告</title>
<style>
*{box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,Noto Sans SC,sans-serif;margin:0;background:#f6f6f6;color:#1a1a1a;min-height:100vh;padding-top:100px}
.header{position:fixed;top:0;left:0;right:0;background:rgba(255,255,255,0.98);backdrop-filter:blur(12px);border-bottom:1px solid #ebebeb;z-index:10;box-shadow:0 1px 3px rgba(26,26,26,0.1)}
.container{max-width:1200px;margin:0 auto;padding:0 40px}
.hdr-title{font-size:20px;line-height:1.4;margin:16px 0 8px;font-weight:600;color:#0084ff}
.meta{color:#8590a6;font-size:13px;margin-bottom:16px}
.content-wrapper{height:calc(100vh - 120px);display:flex;flex-direction:column;padding-top:16px}
.main{display:grid;grid-template-columns:1fr 460px;gap:20px;flex:1;min-height:0;height:100%}
.left-col{display:flex;flex-direction:column;gap:12px;height:100%;min-height:0}
.video-title-cn{color:#1a1a1a;font-size:17px;line-height:1.4;padding:10px 20px;background:#fff;border:1px solid #ebebeb;border-radius:6px;margin:0 0 16px 0;font-weight:600;box-shadow:0 1px 3px rgba(26,26,26,0.05);flex-shrink:0}
.player{position:relative;width:100%;height:0;padding-top:56.25%;border:1px solid #ebebeb;border-radius:6px;overflow:hidden;flex-shrink:0;box-shadow:0 2px 8px rgba(26,26,26,0.08);transition:box-shadow 0.3s ease;background:#fff}
.player:hover{box-shadow:0 4px 12px rgba(26,26,26,0.12)}
.player iframe{position:absolute;left:0;top:0;width:100%;height:100%}
.chapters-box{background:#fff;border:1px solid #ebebeb;border-radius:6px;padding:16px;overflow-y:auto;flex:1;min-height:0;box-shadow:0 1px 3px rgba(26,26,26,0.05)}
.chapters-title{color:#8590a6;font-weight:600;margin-bottom:12px;font-size:12px;text-transform:uppercase;letter-spacing:0.5px}
.chapter{display:flex;gap:10px;padding:10px 12px;cursor:pointer;border-radius:4px;transition:all 0.2s ease;background:transparent}
.chapter:hover{background:#f6f6f6}
.chapter.active{background:#f0f7ff;border-left:3px solid #0084ff;padding-left:9px}
.ch-time{color:#8590a6;font-size:12px;flex-shrink:0;width:48px;font-weight:500}
.ch-title{color:#1a1a1a;font-size:13px;font-weight:400}
.right-col{display:flex;flex-direction:column;gap:12px;height:100%;min-height:0}
.tabs{display:flex;gap:6px;flex-shrink:0;align-items:center;justify-content:space-between;padding:6px;background:#fff;border-radius:6px;border:1px solid #ebebeb;box-shadow:0 1px 3px rgba(26,26,26,0.05)}
.tabs-left{display:flex;gap:4px}
.sync-toggle{display:flex;align-items:center;gap:8px;font-size:12px;color:#8590a6;font-weight:400;padding-right:4px}
.switch{position:relative;display:inline-block;width:40px;height:22px}
.switch input{opacity:0;width:0;height:0}
.slider{position:absolute;cursor:pointer;top:0;left:0;right:0;bottom:0;background:#d4d4d4;transition:0.3s;border-radius:22px}
.slider:before{position:absolute;content:"";height:16px;width:16px;left:3px;bottom:3px;background:#fff;transition:0.3s;border-radius:50%;box-shadow:0 1px 3px rgba(0,0,0,0.2)}
input:checked+.slider{background:#0084ff}
input:checked+.slider:before{transform:translateX(18px)}
.tab{padding:6px 14px;border:none;border-radius:4px;background:transparent;color:#8590a6;cursor:pointer;font-size:13px;font-weight:500;transition:all 0.2s ease}
.tab:hover{background:#f6f6f6;color:#1a1a1a}
.tab.active{background:#0084ff;color:#fff}
.cues{background:#fff;border:1px solid #ebebeb;border-radius:6px;overflow:hidden;overflow-y:auto;flex:1 1 0;min-height:0;box-shadow:0 1px 3px rgba(26,26,26,0.05)}
.cue{display:grid;grid-template-columns:60px 1fr;gap:12px;padding:12px 16px;border-top:1px solid #f6f6f6;cursor:pointer;transition:all 0.2s ease}
.cue:first-child{border-top:none}
.cue:hover{background:#fafafa}
.cue.active{background:#f0f7ff;border-left:3px solid #0084ff;padding-left:13px}
.time{color:#8590a6;font-variant-numeric:tabular-nums;font-size:12px;font-weight:500;transition:opacity 0.2s ease}
.time-hidden .time{display:none}
.time-hidden .cue{grid-template-columns:1fr}
.orig{color:#1a1a1a;font-size:14px;line-height:1.7;font-weight:400}
.tran{color:#1a1a1a;font-size:14px;line-height:1.7;font-weight:400}
.badge{display:inline-block;padding:3px 8px;border-radius:3px;background:#f0f7ff;color:#0084ff;font-size:12px;font-weight:500;border:1px solid #d4e8ff}
.summary-box{background:#fff;border:1px solid #ebebeb;border-radius:6px;padding:20px;overflow-y:auto;flex:1 1 0;min-height:0;box-shadow:0 1px 3px rgba(26,26,26,0.05)}
.summary-content{color:#1a1a1a;font-size:14px;line-height:1.9;white-space:pre-wrap}
.view-btn{position:absolute;top:16px;right:16px;padding:8px 16px;background:#0084ff;color:#fff;border:none;border-radius:4px;font-size:13px;font-weight:500;cursor:pointer;box-shadow:0 2px 6px rgba(0,132,255,0.3);transition:all 0.2s ease;z-index:1}
.view-btn:hover{background:#0066cc;box-shadow:0 4px 10px rgba(0,132,255,0.4)}
.modal{display:none;position:fixed;z-index:1000;left:0;top:0;width:100%;height:100%;background:rgba(26,26,26,0.75);backdrop-filter:blur(4px);animation:fadeIn 0.2s ease}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.modal-content{position:relative;background:#fff;margin:5vh auto;padding:0;width:90%;max-width:900px;max-height:85vh;border-radius:12px;box-shadow:0 8px 32px rgba(26,26,26,0.3);animation:slideIn 0.3s ease;display:flex;flex-direction:column}
@keyframes slideIn{from{transform:translateY(-30px);opacity:0}to{transform:translateY(0);opacity:1}}
.modal-header{padding:20px 24px;border-bottom:1px solid #ebebeb;display:flex;justify-content:space-between;align-items:center;flex-shrink:0}
.modal-title{font-size:18px;font-weight:600;color:#1a1a1a;margin:0}
.close{color:#8590a6;font-size:28px;font-weight:300;line-height:1;cursor:pointer;border:none;background:transparent;padding:0;width:32px;height:32px;display:flex;align-items:center;justify-content:center;border-radius:4px;transition:all 0.2s ease}
.close:hover{background:#f6f6f6;color:#1a1a1a}
.modal-body{padding:24px;overflow-y:auto;flex:1;color:#1a1a1a;font-size:14px;line-height:1.9;white-space:pre-wrap}
.modal-body-subtitle{color:#1a1a1a;font-size:14px;line-height:1.9;white-space:normal}
.modal-body-subtitle .cue-item{padding:12px 0;border-bottom:1px solid #f6f6f6}
.modal-body-subtitle .cue-item:last-child{border-bottom:none}
.modal-body-subtitle .cue-time{color:#0084ff;font-weight:500;font-size:13px;margin-bottom:4px}
.modal-body-subtitle .cue-text{color:#1a1a1a}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:#f6f6f6}
::-webkit-scrollbar-thumb{background:#d4d4d4;border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:#b4b4b4}
</style>
</head>
<body>
<div class="header">
  <div class="container">
    <h1 class="hdr-title">$page_title - 字幕翻译报告</h1>
    <div class="meta">源语言 <span class="badge">$source_language</span> → 目标语言 <span class="badge">$target_language</span></div>
  </div>
</div>
<div class="container">
  <div class="content-wrapper">
    $title_cn_html
    <div class="main">
      <div class="left-col">
        <div class="player"><iframe id="player" src="https://www.youtube.com/embed/$video_id?enablejsapi=1" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>
        <div class="chapters-box">
          <div class="chapters-title">章节导航</div>
          <div id="chapters">$chapters_html</div>
        </div>
      </div>
      <div class="right-col">
      <div class="tabs">
        <div class="tabs-left">
          <div class="tab active" id="tab-en">原文 EN</div>
          <div class="tab" id="tab-cn">中文</div>
          <div class="tab" id="tab-summary">总结</div>
        </div>
        <div class="sync-toggle">
          <span>时间轴同步</span>
          <label class="switch">
            <input type="checkbox" id="sync-switch" checked>
            <span class="slider"></span>
          </label>
        </div>
      </div>
      <div class="cues" id="cues-en">$rows_en</div>
      <div class="cues" id="cues-cn" style="display:none;position:relative">
        <button class="view-btn" id="view-cn-btn">查看全文</button>
        $rows_cn
      </div>
      <div class="summary-box" id="summary-box" style="display:none;position:relative">
        <button class="view-btn" id="view-summary-btn">查看全文</button>
        <div class="summary-content">$summary_text</div>
      </div>
    </div>
  </div>
  </div>
</div>

<!-- 模态框：中文字幕 -->
<div id="modal-cn" class="modal">
  <div class="modal-content">
    <div class="modal-header">
      <h2 class="modal-title">查看全文</h2>
      <button class="close" id="close-cn-modal">&times;</button>
    </div>
    <div class="modal-body modal-body-subtitle" id="modal-cn-body"></div>
  </div>
</div>

<!-- 模态框：总结 -->
<div id="modal-summary" class="modal">
  <div class="modal-content">
    <div class="modal-header">
      <h2 class="modal-title">查看全文</h2>
      <button class="close" id="close-summary-modal">&times;</button>
    </div>
    <div class="modal-body" id="modal-summary-body"></div>
  </div>
</div>

<script>
// YouTube Iframe API
var tag=document.createElement('script');tag.src='https://www.youtube.com/iframe_api';document.body.appendChild(tag);
var ytPlayer=null;
var syncTimer=null;
var currentActiveCue=null;
var syncEnabled=true;
function onYouTubeIframeAPIReady(){
  ytPlayer=new YT.Player('player',{
    events:{
      'onReady':function(){if(syncEnabled){startSync();}},
      'onStateChange':function(e){
        if(e.data===YT.PlayerState.PLAYING&&syncEnabled){startSync();}
        else if(e.data===YT.PlayerState.PAUSED||e.data===YT.PlayerState.ENDED){stopSync();}
      }
    }
  });
}
function seekToTime(t){if(ytPlayer&&ytPlayer.seekTo){ytPlayer.seekTo(t,true);ytPlayer.playVideo();}}
function bindCues(container){
  Array.from(container.querySelectorAll('.cue')).forEach(function(el){
    el.addEventListener('click',function(){
      var t=parseFloat(el.getAttribute('data-start')||'0');
      seekToTime(t);
    });
  });
}
bindCues(document.getElementById('cues-en'));
bindCues(document.getElementById('cues-cn'));
// 字幕同步功能
function startSync(){
  if(!syncEnabled||syncTimer)return;
  syncTimer=setInterval(updateActiveCue,200);
}
function stopSync(){
  if(syncTimer){clearInterval(syncTimer);syncTimer=null;}
}
function updateActiveCue(){
  if(!syncEnabled||!ytPlayer||!ytPlayer.getCurrentTime)return;
  var currentTime=ytPlayer.getCurrentTime();
  var activeContainer=boxEn.style.display!=='none'?boxEn:(boxCn.style.display!=='none'?boxCn:null);
  if(!activeContainer)return;
  var allCues=Array.from(activeContainer.querySelectorAll('.cue'));
  var targetCue=null;
  for(var i=0;i<allCues.length;i++){
    var startTime=parseFloat(allCues[i].getAttribute('data-start')||'0');
    var duration=parseFloat(allCues[i].getAttribute('data-duration')||'999');
    if(currentTime>=startTime&&currentTime<startTime+duration){
      targetCue=allCues[i];
      break;
    }
    if(currentTime>=startTime&&(!targetCue||startTime>parseFloat(targetCue.getAttribute('data-start')||'0'))){
      targetCue=allCues[i];
    }
  }
  if(targetCue&&targetCue!==currentActiveCue){
    if(currentActiveCue){currentActiveCue.classList.remove('active');}
    targetCue.classList.add('active');
    targetCue.scrollIntoView({block:'center',behavior:'smooth'});
    currentActiveCue=targetCue;
  }
}
// 轨道容器引用（全局）
var boxEn=document.getElementById('cues-en');
var boxCn=document.getElementById('cues-cn');
var boxSummary=document.getElementById('summary-box');
// 同步开关控制
var syncSwitch=document.getElementById('sync-switch');
syncSwitch.addEventListener('change',function(){
  syncEnabled=this.checked;
  if(syncEnabled){
    boxEn.classList.remove('time-hidden');
    boxCn.classList.remove('time-hidden');
    if(ytPlayer&&ytPlayer.getPlayerState&&ytPlayer.getPlayerState()===YT.PlayerState.PLAYING){
      startSync();
    }
  }else{
    stopSync();
    boxEn.classList.add('time-hidden');
    boxCn.classList.add('time-hidden');
    if(currentActiveCue){
      currentActiveCue.classList.remove('active');
      currentActiveCue=null;
    }
  }
});
// 章节点击跳转
Array.from(document.querySelectorAll('.chapter')).forEach(function(el){el.addEventListener('click',function(){var t=parseFloat(el.getAttribute('data-start')||'0');seekToTime(t);});});
// 轨道切换
var tabEn=document.getElementById('tab-en'), tabCn=document.getElementById('tab-cn'), tabSummary=document.getElementById('tab-summary');
var currentTab='en';
function activate(tab){
  // 清除所有容器的活动状态
  if(currentActiveCue){
    currentActiveCue.classList.remove('active');
    currentActiveCue=null;
  }
  boxEn.style.display='none';
  boxCn.style.display='none';
  boxSummary.style.display='none';
  tabEn.classList.remove('active');
  tabCn.classList.remove('active');
  tabSummary.classList.remove('active');
  currentTab=tab;
  if(tab==='en'){
    boxEn.style.display='block';
    tabEn.classList.add('active');
    updateActiveCue();
  }else if(tab==='cn'){
    boxCn.style.display='block';
    tabCn.classList.add('active');
    updateActiveCue();
  }else if(tab==='summary'){
    boxSummary.style.display='block';
    tabSummary.classList.add('active');
  }
}
tabEn.addEventListener('click',function(){activate('en')});
tabCn.addEventListener('click',function(){activate('cn')});
tabSummary.addEventListener('click',function(){activate('summary')});
// 模态框控制
var modalCn=document.getElementById('modal-cn');
var modalSummary=document.getElementById('modal-summary');
var viewCnBtn=document.getElementById('view-cn-btn');
var viewSummaryBtn=document.getElementById('view-summary-btn');
var closeCnModal=document.getElementById('close-cn-modal');
var closeSummaryModal=document.getElementById('close-summary-modal');
// 点击查看中文字幕按钮
viewCnBtn.addEventListener('click',function(e){
  e.stopPropagation();
  var modalBody=document.getElementById('modal-cn-body');
  modalBody.innerHTML='';
  var cnCues=Array.from(document.getElementById('cues-cn').querySelectorAll('.cue'));
  cnCues.forEach(function(cue){
    var time=cue.querySelector('.time').textContent;
    var text=cue.querySelector('.tran').textContent;
    var item=document.createElement('div');
    item.className='cue-item';
    item.innerHTML='<div class="cue-time">'+time+'</div><div class="cue-text">'+text+'</div>';
    modalBody.appendChild(item);
  });
  modalCn.style.display='block';
  document.body.style.overflow='hidden';
});
// 点击查看总结按钮
viewSummaryBtn.addEventListener('click',function(e){
  e.stopPropagation();
  var modalBody=document.getElementById('modal-summary-body');
  var summaryText=document.querySelector('.summary-content').textContent;
  modalBody.innerHTML='';
  modalBody.textContent=summaryText;
  modalSummary.style.display='block';
  document.body.style.overflow='hidden';
});
// 关闭模态框
function closeModal(modal){
  modal.style.display='none';
  document.body.style.overflow='auto';
}
closeCnModal.addEventListener('click',function(){closeModal(modalCn);});
closeSummaryModal.addEventListener('click',function(){closeModal(modalSummary);});
// 点击模态框背景关闭
modalCn.addEventListener('click',function(e){if(e.target===modalCn){closeModal(modalCn);}});
modalSummary.addEventListener('click',function(e){if(e.target===modalSummary){closeModal(modalSummary);}});
// ESC键关闭模态框
document.addEventListener('keydown',function(e){
  if(e.key==='Escape'){
    if(modalCn.style.display==='block'){closeModal(modalCn);}
    if(modalSummary.style.display==='block'){closeModal(modalSummary);}
  }
});
</script>
</body>
</html>
"""
        )
        # 处理总结内容
        safe_summary = html.escape(summary or '暂无总结内容')
        
        # 处理标题翻译
        safe_title_cn = html.escape(title_cn or '')
        if safe_title_cn:
            title_cn_html = f'<div class="video-title-cn">{safe_title_cn}</div>'
        else:
            title_cn_html = ''
        
        doc = template.substitute(
            page_title=html.escape(safe_title),
            source_language=html.escape(source_language or '未知'),
            target_language=html.escape(target_language or 'zh-CN'),
            video_id=video_id,
            title_cn_html=title_cn_html,
            rows_en=''.join(rows_en),
            rows_cn=''.join(rows_cn),
            summary_text=safe_summary,
            chapters_html=''.join(chapters_html) if chapters_html else '<div style="color:#8b949e;font-size:13px;">暂无章节信息</div>',
        )
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(doc)




