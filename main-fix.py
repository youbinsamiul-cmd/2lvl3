# ==================== STANDARD IMPORTS ====================
import sys
import asyncio
import httpx
import random
import json
import socket
import struct
import time
import os
import uuid
import itertools
import secrets
import traceback
import base64
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ==================== ORIGINAL IMPORTS ====================
from google_play_scraper import app as play_scraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from protobuf_decoder.protobuf_decoder import Parser
from message_ids import MESSAGE_ID_TO_NAME
import CguTeam_pb2
import CguFF_pb2
import thunderFF_pb2

# ==================== WEB DASHBOARD ====================
from dashboard_server import bot_state, start_web_dashboard

# ==================== EMBEDDED DASHBOARD HTML (index.html) ====================
INDEX_HTML = r'''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>CGU TEAM | Real-Time Command Center</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&family=Noto+Sans+Arabic:wght@400;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css">
<style>
:root{
  --bg:#070918; --card:rgba(22,25,58,.62); --card-h:rgba(34,38,86,.8); --modal:#0d1030;
  --line:rgba(139,148,255,.16); --line-h:rgba(139,148,255,.4);
  --violet:#8b5cf6; --indigo:#6366f1; --blue:#3b82f6; --cyan:#38bdf8;
  --grad:linear-gradient(135deg,#8b5cf6,#3b82f6);
  --grad-soft:linear-gradient(135deg,rgba(139,92,246,.22),rgba(59,130,246,.22));
  --ok:#34d399; --warn:#fbbf24; --err:#f87171;
  --text:#eef0ff; --dim:#8f95c4;
  --ease:.35s cubic-bezier(.2,.8,.2,1);
}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent;scrollbar-width:thin;scrollbar-color:#4b4fa8 transparent}
html,body{height:100%}
body{font-family:'Plus Jakarta Sans','Noto Sans Arabic','Noto Sans Devanagari',system-ui,sans-serif;background:var(--bg);color:var(--text);overflow:hidden;display:flex;flex-direction:column}
button,input,select,textarea{font-family:inherit}
:focus-visible{outline:2px solid var(--cyan);outline-offset:2px}

.bg{position:fixed;inset:0;z-index:-1;background:radial-gradient(ellipse at 20% 0%,#1b1250 0%,transparent 55%),radial-gradient(ellipse at 90% 100%,#0b2a66 0%,transparent 55%),var(--bg)}
.orb{position:absolute;border-radius:50%;filter:blur(110px);opacity:.28;animation:drift 22s infinite alternate ease-in-out}
.orb.a{width:46vw;height:46vw;background:var(--violet);top:-12%;left:-12%}
.orb.b{width:50vw;height:50vw;background:var(--blue);bottom:-18%;right:-14%;animation-delay:-6s}
@keyframes drift{to{transform:translate(8%,-8%) scale(1.1)}}

/* TOPBAR */
.topbar{display:flex;align-items:center;gap:14px;padding:12px 20px;padding-top:max(12px,env(safe-area-inset-top));border-bottom:1px solid var(--line);background:rgba(10,12,34,.7);backdrop-filter:blur(16px);flex-shrink:0;z-index:20}
.menu-btn{width:42px;height:42px;border-radius:12px;border:1px solid var(--line);background:var(--card);color:var(--text);font-size:16px;cursor:pointer;transition:var(--ease);display:grid;place-items:center;flex-shrink:0}
.menu-btn:hover{border-color:var(--violet);background:var(--card-h)}
.top-title{font-weight:800;font-size:17px;letter-spacing:.3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.top-title small{display:block;font-size:11px;font-weight:500;color:var(--dim);letter-spacing:0;margin-top:1px}
.pill{margin-inline-start:auto;display:flex;align-items:center;gap:8px;padding:7px 12px;border-radius:99px;border:1px solid var(--line);background:var(--card);font-size:12px;font-weight:700;flex-shrink:0}
.dot{width:8px;height:8px;border-radius:50%;background:var(--ok);box-shadow:0 0 10px var(--ok)}
.pill.off .dot{background:var(--err);box-shadow:0 0 10px var(--err)}

/* SIDEBAR DRAWER */
.overlay{position:fixed;inset:0;z-index:40;background:rgba(3,4,16,.6);backdrop-filter:blur(4px);opacity:0;pointer-events:none;transition:opacity var(--ease)}
body.menu-open .overlay{opacity:1;pointer-events:all}
.sidebar{position:fixed;top:0;bottom:0;left:0;width:min(290px,84vw);z-index:50;display:flex;flex-direction:column;padding:26px 18px;padding-top:max(26px,env(safe-area-inset-top));background:rgba(12,14,42,.96);backdrop-filter:blur(20px);border-right:1px solid var(--line);transform:translateX(-102%);transition:transform var(--ease);box-shadow:20px 0 60px rgba(0,0,0,.5)}
body.menu-open .sidebar{transform:none}
.brand{display:flex;align-items:center;gap:14px;margin-bottom:34px;padding:0 6px}
.brand-icon{width:44px;height:44px;border-radius:13px;background:var(--grad);display:grid;place-items:center;font-size:19px;box-shadow:0 8px 24px rgba(99,102,241,.45)}
.brand-name{font-size:20px;font-weight:800;letter-spacing:1px;background:linear-gradient(90deg,#fff,var(--cyan));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.brand-sub{font-size:11px;color:var(--dim);margin-top:2px}
.nav{display:flex;flex-direction:column;gap:6px;flex:1}
.nav-item{display:flex;align-items:center;gap:14px;padding:13px 16px;border-radius:12px;color:var(--dim);font-weight:600;font-size:14.5px;cursor:pointer;border:1px solid transparent;transition:var(--ease);background:none;text-align:left;width:100%}
.nav-item i{width:22px;text-align:center;font-size:16px}
.nav-item:hover{color:#fff;background:rgba(139,92,246,.1)}
.nav-item.active{color:#fff;background:var(--grad-soft);border-color:var(--line-h)}
.nav-item.active i{color:var(--cyan)}
.side-foot{padding:16px 8px 0;border-top:1px solid var(--line);font-size:12px;color:var(--dim);line-height:1.5}
.side-foot b{display:block;color:var(--ok);font-size:13px}

/* PAGES */
.main{flex:1;position:relative;min-height:0}
.page{position:absolute;inset:0;padding:24px clamp(16px,4vw,40px) 40px;overflow-y:auto;display:none;flex-direction:column}
.page.active{display:flex;animation:fade .45s ease}
@keyframes fade{from{opacity:0;transform:translateY(10px)}}
.page-head{display:flex;justify-content:space-between;align-items:flex-end;gap:14px;flex-wrap:wrap;margin-bottom:22px}
.page-title{font-size:clamp(24px,4vw,32px);font-weight:800}
.page-sub{color:var(--dim);font-size:14px;margin-top:4px}
.row{display:flex;gap:10px;flex-wrap:wrap}

.btn{padding:10px 18px;border-radius:11px;border:1px solid var(--line);background:var(--card);color:var(--text);font-size:13px;font-weight:700;cursor:pointer;transition:var(--ease);display:inline-flex;align-items:center;gap:9px}
.btn:hover{border-color:var(--violet);background:var(--card-h);transform:translateY(-2px)}
.btn.primary{background:var(--grad);border:0;color:#fff;box-shadow:0 8px 24px rgba(99,102,241,.4)}
.btn.primary:hover{box-shadow:0 10px 32px rgba(99,102,241,.6)}

/* STATS */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:22px;backdrop-filter:blur(14px);transition:var(--ease)}
.stat:hover{transform:translateY(-4px);border-color:var(--line-h);background:var(--card-h)}
.stat-icon{width:42px;height:42px;border-radius:12px;background:var(--grad-soft);color:var(--cyan);display:grid;place-items:center;font-size:17px;margin-bottom:16px}
.stat-val{font-family:'JetBrains Mono',monospace;font-size:clamp(24px,3vw,30px);font-weight:700;word-break:break-all}
.stat-label{color:var(--dim);font-size:13px;font-weight:600;margin-top:4px}
.stat-foot{color:var(--cyan);font-size:12px;font-weight:600;margin-top:10px}

/* CONTROLS */
.controls{display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap}
.batch-box{margin-bottom:22px;padding:20px;border:1px solid var(--line);border-radius:16px;background:linear-gradient(135deg,rgba(99,102,241,.09),rgba(14,165,233,.05));box-shadow:0 14px 35px rgba(0,0,0,.18)}
.batch-head{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;flex-wrap:wrap;margin-bottom:16px}
.batch-title{font-size:16px;font-weight:800}.batch-sub{font-size:12px;color:var(--dim);margin-top:4px}
.batch-grid{display:grid;grid-template-columns:minmax(220px,1.8fr) 120px 120px auto;gap:12px;align-items:end}
.batch-box .field{margin-bottom:0}.batch-preview{margin-top:14px;padding:11px 13px;border-radius:10px;background:rgba(5,6,22,.45);border:1px solid var(--line);font-size:12px;color:var(--dim)}
.batch-preview strong{color:var(--text)}
.batch-danger{border-color:rgba(239,68,68,.3)}
@media(max-width:760px){.batch-grid{grid-template-columns:1fr 1fr}.batch-grid .file-field{grid-column:1/-1}.batch-grid .batch-actions{grid-column:1/-1}}
.search{flex:1;min-width:220px;position:relative}
.search i{position:absolute;left:15px;top:50%;transform:translateY(-50%);color:var(--dim)}
.search input{width:100%;padding:12px 14px 12px 40px;border-radius:11px;border:1px solid var(--line);background:rgba(5,6,22,.5);color:#fff;font-size:13px;outline:none;transition:var(--ease)}
.search input:focus{border-color:var(--violet);box-shadow:0 0 0 3px rgba(139,92,246,.18)}
.seg{display:flex;gap:4px;padding:4px;border-radius:11px;background:rgba(5,6,22,.5);border:1px solid var(--line);overflow-x:auto;max-width:100%}
.seg button{border:0;background:none;color:var(--dim);padding:8px 14px;border-radius:8px;cursor:pointer;font-size:12.5px;font-weight:700;white-space:nowrap;transition:var(--ease)}
.seg button:hover{color:#fff}
.seg button.active{color:#fff;background:var(--grad)}

/* NODES */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,340px),1fr));gap:16px}
.node{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:20px;backdrop-filter:blur(14px);transition:var(--ease);position:relative;overflow:hidden}
.node::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--grad)}
.node:hover{border-color:var(--line-h);transform:translateY(-3px);background:var(--card-h)}
.node-head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:16px}
.who{display:flex;align-items:center;gap:13px;min-width:0}
.avatar{position:relative;width:46px;height:46px;flex-shrink:0;border-radius:13px;background:var(--grad-soft);border:1px solid var(--line-h);display:grid;place-items:center;color:var(--cyan);font-size:19px}
.lvl{position:absolute;right:-7px;bottom:-7px;padding:2px 6px;border-radius:7px;font-size:9px;font-weight:800;font-family:'JetBrains Mono',monospace;background:var(--grad);border:2px solid var(--bg)}
.name{font-size:15px;font-weight:700;display:flex;align-items:center;gap:8px;min-width:0}
.name span:first-child{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.region{padding:2px 7px;border-radius:5px;font-size:9.5px;font-weight:800;color:var(--violet);background:rgba(139,92,246,.15);border:1px solid rgba(139,92,246,.3)}
.uid{display:flex;align-items:center;gap:8px;margin-top:4px;color:var(--dim);font-family:'JetBrains Mono',monospace;font-size:11px}
.uid i{cursor:pointer}.uid i:hover{color:#fff}
.badge{padding:6px 10px;border-radius:9px;font-size:10.5px;font-weight:800;display:flex;align-items:center;gap:6px;border:1px solid;flex-shrink:0}
.s-online{color:var(--ok);background:rgba(52,211,153,.1);border-color:rgba(52,211,153,.3)}
.s-match{color:var(--cyan);background:rgba(56,189,248,.12);border-color:rgba(56,189,248,.4);box-shadow:0 0 14px rgba(56,189,248,.25)}
.s-paused{color:var(--dim);background:rgba(143,149,196,.1);border-color:rgba(143,149,196,.3)}
.s-error{color:var(--warn);background:rgba(251,191,36,.1);border-color:rgba(251,191,36,.3)}
.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-bottom:16px}
.metric{padding:10px;border-radius:10px;background:rgba(5,6,22,.5);border:1px solid rgba(255,255,255,.05);min-width:0}
.metric span{display:block;color:var(--dim);font-size:10.5px;font-weight:600;margin-bottom:4px}
.metric strong{display:block;font-family:'JetBrains Mono',monospace;font-size:12.5px;overflow:hidden;text-overflow:ellipsis}
.metric.gain strong{color:var(--ok)}
.prog-top,.prog-bot{display:flex;justify-content:space-between;font-size:11px;color:var(--dim);font-weight:600}
.prog-bot{font-family:'JetBrains Mono',monospace;margin-top:6px}
.prog-bot .pct{color:var(--cyan);font-weight:700}
.track{height:7px;margin-top:7px;background:rgba(5,6,22,.7);border-radius:9px;overflow:hidden}
.fill{height:100%;background:linear-gradient(90deg,var(--violet),var(--blue),var(--cyan));transition:width .8s ease;border-radius:9px}
.node-foot{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:16px;padding-top:12px;border-top:1px solid rgba(255,255,255,.06)}
.time{color:var(--dim);font-size:11.5px;display:inline-flex;align-items:center;gap:6px;font-family:'JetBrains Mono',monospace}
.acts{display:flex;gap:7px}
.act{width:34px;height:34px;border-radius:9px;border:1px solid var(--line);background:rgba(5,6,22,.4);color:var(--dim);cursor:pointer;font-size:12px;transition:var(--ease);display:grid;place-items:center}
.act:disabled{opacity:.35;cursor:not-allowed;pointer-events:none}

.act:hover{color:#fff;border-color:var(--violet);background:rgba(139,92,246,.15);transform:translateY(-2px)}
.act.danger:hover{color:var(--err);border-color:var(--err);background:rgba(248,113,113,.1)}
.empty{grid-column:1/-1;text-align:center;padding:56px 16px;color:var(--dim)}
.empty i{font-size:30px;margin-bottom:14px;color:var(--violet);display:block}
.empty .btn{margin-top:18px}

/* TERMINAL */
.term{flex:1;min-height:320px;display:flex;flex-direction:column;border-radius:18px;border:1px solid var(--line);background:rgba(6,7,24,.82);overflow:hidden;backdrop-filter:blur(14px)}
.term-head{padding:12px 18px;border-bottom:1px solid var(--line);background:rgba(20,22,60,.7);font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--cyan)}
.term-body{padding:16px 18px;overflow-y:auto;flex:1;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.75;color:#d4d7f5}
.log{display:flex;gap:10px;margin-bottom:4px;word-break:break-word}
.log-ts{color:var(--violet);flex-shrink:0}
.log-msg.success{color:var(--ok)}.log-msg.warning{color:var(--warn)}.log-msg.error{color:var(--err)}

/* MODAL */
.modal{position:fixed;inset:0;z-index:100;background:rgba(3,4,16,.78);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;padding:16px;opacity:0;pointer-events:none;transition:var(--ease)}
.modal.active{opacity:1;pointer-events:all}
.card{width:100%;max-width:440px;max-height:92vh;overflow-y:auto;background:var(--modal);border:1px solid var(--line-h);border-radius:20px;padding:28px;transform:translateY(30px) scale(.96);transition:var(--ease);box-shadow:0 40px 100px rgba(0,0,0,.7),0 0 60px rgba(99,102,241,.2);position:relative}
.card::before{content:'';position:absolute;left:0;right:0;top:0;height:4px;background:var(--grad)}
.modal.active .card{transform:none}
.card h2{font-size:22px;font-weight:800;margin-bottom:6px}
.card p{color:var(--dim);font-size:13px;margin-bottom:22px}
.field{margin-bottom:18px}
.field label{display:block;font-size:12px;font-weight:700;color:var(--cyan);margin-bottom:8px}
.field input,.field select,.field textarea{width:100%;padding:13px;border-radius:10px;background:rgba(5,6,22,.6);border:1px solid var(--line);color:#fff;font-size:14px;outline:none;transition:var(--ease)}
.field textarea{min-height:100px;resize:vertical;font-family:'JetBrains Mono',monospace}
.field select option{background:#0d1030}
.field input:focus,.field select:focus,.field textarea:focus{border-color:var(--violet);box-shadow:0 0 0 3px rgba(139,92,246,.18)}
.card-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:26px}

/* PROFILE */
.hero{position:relative;border-radius:20px;border:1px solid var(--line);background:var(--card);backdrop-filter:blur(14px);overflow:hidden;margin-bottom:16px}
.hero-banner{height:110px;background:linear-gradient(120deg,#6d28d9,#4f46e5 50%,#0ea5e9);position:relative}
.hero-banner::after{content:'';position:absolute;inset:0;background:radial-gradient(circle at 80% 0%,rgba(255,255,255,.25),transparent 55%)}
.hero-body{display:flex;align-items:flex-end;gap:18px;padding:0 24px 22px;margin-top:-42px;flex-wrap:wrap;position:relative}
.hero-avatar{width:92px;height:92px;border-radius:24px;background:var(--grad);border:4px solid var(--bg);display:grid;place-items:center;font-size:30px;font-weight:800;letter-spacing:1px;box-shadow:0 12px 32px rgba(99,102,241,.5);flex-shrink:0}
.hero-name{font-size:clamp(22px,4vw,28px);font-weight:800}
.hero-tag{color:var(--dim);font-size:13.5px;margin-top:3px}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-inline-start:auto}
.chip{padding:7px 12px;border-radius:99px;font-size:12px;font-weight:700;border:1px solid var(--line-h);background:var(--grad-soft);display:inline-flex;align-items:center;gap:7px}
.chip i{color:var(--cyan)}
.info{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:6px 22px;backdrop-filter:blur(14px);margin-top:16px}
.info-row{display:flex;justify-content:space-between;gap:12px;padding:14px 0;border-bottom:1px solid rgba(255,255,255,.06);font-size:13.5px}
.info-row:last-child{border:0}
.info-row span{color:var(--dim)}.info-row b{font-weight:700;text-align:right}
@media(max-width:600px){.chips{margin-inline-start:0}.hero-body{padding:0 18px 20px}}

/* TOAST */
.toasts{position:fixed;bottom:max(20px,env(safe-area-inset-bottom));right:20px;left:20px;z-index:200;display:flex;flex-direction:column;align-items:flex-end;gap:10px;pointer-events:none}
.toast{max-width:100%;background:rgba(12,14,42,.96);border:1px solid var(--line);border-left:4px solid var(--violet);padding:13px 18px;border-radius:12px;display:flex;align-items:center;gap:11px;font-size:13px;font-weight:600;box-shadow:0 10px 30px rgba(0,0,0,.5);animation:tin .35s var(--ease) both;pointer-events:auto}
.toast.success{border-left-color:var(--ok)}.toast.error{border-left-color:var(--err)}.toast.hide{opacity:0;transform:translateX(30px);transition:.35s}
@keyframes tin{from{opacity:0;transform:translateX(40px)}}

@media(max-width:600px){
  .topbar{padding:10px 14px}.pill span{display:none}.pill{padding:9px}
  .metrics{grid-template-columns:1fr 1fr}.metric:last-child{grid-column:1/-1}
  .node-head{flex-wrap:wrap}.btn{padding:10px 14px}
  .page-head .row,.page-head .row .btn{width:100%}.page-head .row .btn{justify-content:center}
}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}

/* ===== UPGRADE: efek premium ===== */
@property --ang{syntax:'<angle>';initial-value:0deg;inherits:false}
@keyframes spin{to{--ang:360deg}}
@keyframes flow{to{background-position:200% 0}}
@keyframes rise{from{opacity:0;transform:translateY(26px) scale(.96)}}
@keyframes pulse{50%{box-shadow:0 0 24px rgba(56,189,248,.6)}}
@keyframes floaty{50%{transform:translateY(-5px)}}
@keyframes sweep{to{transform:translateX(260%) skewX(-20deg)}}

.bg::before{content:'';position:absolute;inset:0;background-image:linear-gradient(rgba(139,148,255,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(139,148,255,.07) 1px,transparent 1px);background-size:44px 44px;-webkit-mask-image:radial-gradient(ellipse at 50% 30%,#000 0%,transparent 72%);mask-image:radial-gradient(ellipse at 50% 30%,#000 0%,transparent 72%)}
.orb{opacity:.38}
.orb.c{width:30vw;height:30vw;background:var(--cyan);top:40%;left:45%;opacity:.14;animation-duration:28s;animation-delay:-12s}

.topbar{box-shadow:0 1px 0 rgba(139,92,246,.35),0 12px 40px rgba(0,0,0,.3)}
.top-title span{background:linear-gradient(90deg,#fff,#a5b4fc);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.dot{animation:pulse 2s infinite}

.brand-name{background:linear-gradient(90deg,#fff,#a78bfa,#38bdf8,#fff);background-size:200% 100%;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;animation:flow 6s linear infinite}
.brand-icon{animation:floaty 4s ease-in-out infinite}
.sidebar{background:linear-gradient(180deg,rgba(20,18,64,.97),rgba(9,12,38,.97))}
.nav-item{position:relative}
.nav-item:hover{transform:translateX(4px)}
.nav-item.active{box-shadow:0 8px 28px rgba(99,102,241,.25)}
.nav-item.active::before{content:'';position:absolute;left:-18px;top:20%;bottom:20%;width:4px;border-radius:0 4px 4px 0;background:var(--grad);box-shadow:0 0 14px var(--violet)}

.stat,.node,.hero,.info{position:relative}
.stat:hover,.node:hover,.hero:hover,.info:hover{background-image:radial-gradient(420px circle at var(--mx,50%) var(--my,50%),rgba(139,92,246,.18),transparent 45%)}
.stat::after,.node::after,.hero::after,.info::after{content:'';position:absolute;inset:0;border-radius:inherit;padding:1px;pointer-events:none;opacity:0;transition:opacity .4s;background:conic-gradient(from var(--ang),transparent 0 55%,#8b5cf6,#38bdf8,transparent);-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask:linear-gradient(#000 0 0) content-box exclude,linear-gradient(#000 0 0);animation:spin 3.5s linear infinite}
.stat:hover::after,.node:hover::after,.hero:hover::after,.info:hover::after{opacity:1}

.stat{padding:24px}
.stat-val{background:linear-gradient(90deg,#fff,#c4b5fd 60%,#7dd3fc);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;font-size:clamp(26px,3.2vw,34px)}
.stat-icon{box-shadow:0 0 26px rgba(99,102,241,.45),inset 0 0 0 1px rgba(165,180,252,.25);animation:floaty 5s ease-in-out infinite}
.stat:nth-child(2) .stat-icon{animation-delay:-1s}.stat:nth-child(3) .stat-icon{animation-delay:-2s}.stat:nth-child(4) .stat-icon{animation-delay:-3s}

.page.active .stat,.page.active .node,.page.active .hero,.page.active .info,.page.active .term{animation:rise .65s cubic-bezier(.2,.8,.2,1) backwards}
.page.active .stat:nth-child(2),.page.active .node:nth-child(2){animation-delay:.08s}
.page.active .stat:nth-child(3),.page.active .node:nth-child(3){animation-delay:.16s}
.page.active .stat:nth-child(4),.page.active .node:nth-child(4){animation-delay:.24s}
.page.active .node:nth-child(n+5){animation-delay:.3s}

.btn.primary{position:relative;overflow:hidden}
.btn.primary::after{content:'';position:absolute;top:0;bottom:0;left:-60%;width:40%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.35),transparent);transform:skewX(-20deg)}
.btn.primary:hover::after{animation:sweep .8s ease}

.s-match{animation:pulse 2s infinite}
.fill{background-size:200% 100%;animation:flow 3s linear infinite;box-shadow:0 0 14px rgba(99,102,241,.7)}
.avatar{box-shadow:0 0 22px rgba(99,102,241,.35)}

.hero-banner{background:linear-gradient(120deg,#6d28d9,#4f46e5,#0ea5e9,#6d28d9);background-size:200% 100%;animation:flow 10s linear infinite}
.hero-avatar{animation:floaty 5s ease-in-out infinite}
.hero-name{background:linear-gradient(90deg,#fff,#c4b5fd);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}

.seg button.active{box-shadow:0 6px 18px rgba(99,102,241,.45)}
.term{box-shadow:0 24px 60px rgba(0,0,0,.45),0 0 0 1px rgba(139,92,246,.08)}
.term-head::before{content:'';display:inline-block;width:9px;height:9px;border-radius:50%;background:#f87171;box-shadow:16px 0 0 #fbbf24,32px 0 0 #34d399;margin-right:50px}
.log:hover{background:rgba(139,92,246,.08)}

/* ===== DONASI ===== */
.gold{--gold:#f0b90b}
.donate{display:grid;grid-template-columns:1.2fr 1fr;gap:16px;align-items:start}
.d-card{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:28px;backdrop-filter:blur(14px);position:relative;overflow:hidden}
.d-card::before{content:'';position:absolute;right:-60px;top:-60px;width:220px;height:220px;border-radius:50%;background:radial-gradient(circle,rgba(240,185,11,.22),transparent 65%)}
.d-heart{width:58px;height:58px;border-radius:18px;display:grid;place-items:center;font-size:24px;color:#fff;background:linear-gradient(135deg,#ec4899,#8b5cf6);box-shadow:0 10px 30px rgba(236,72,153,.4);margin-bottom:18px;animation:floaty 4s ease-in-out infinite}
.d-card h2{font-size:clamp(20px,3vw,26px);font-weight:800;margin-bottom:8px}
.d-card p{color:var(--dim);font-size:14px;line-height:1.65}
.d-label{display:flex;align-items:center;gap:8px;margin:24px 0 10px;font-size:12px;font-weight:700;color:#f0b90b}
.d-id{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 16px;border-radius:14px;background:rgba(5,6,22,.6);border:1px solid rgba(240,185,11,.35);box-shadow:0 0 30px rgba(240,185,11,.08)}
.d-id code{font-family:'JetBrains Mono',monospace;font-size:clamp(20px,5vw,28px);font-weight:700;letter-spacing:2px;background:linear-gradient(90deg,#fde68a,#f0b90b);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.btn.gold{background:linear-gradient(135deg,#f0b90b,#f59e0b);color:#1a1300;border:0;box-shadow:0 8px 24px rgba(240,185,11,.35)}
.btn.gold:hover{background:linear-gradient(135deg,#fcd34d,#f0b90b);box-shadow:0 10px 30px rgba(240,185,11,.55)}
.steps{list-style:none;counter-reset:st;display:flex;flex-direction:column;gap:14px;margin-top:6px}
.steps li{counter-increment:st;display:flex;gap:14px;align-items:flex-start;font-size:13.5px;line-height:1.5}
.steps li::before{content:counter(st);flex-shrink:0;width:28px;height:28px;border-radius:9px;display:grid;place-items:center;font-size:12px;font-weight:800;background:var(--grad)}
.d-note{margin-top:20px;padding:12px 14px;border-radius:12px;font-size:12.5px;color:var(--warn);background:rgba(251,191,36,.08);border:1px solid rgba(251,191,36,.25);line-height:1.5}
.heart-btn{width:42px;height:42px;border-radius:12px;border:1px solid rgba(236,72,153,.4);background:rgba(236,72,153,.12);color:#f472b6;cursor:pointer;display:grid;place-items:center;font-size:16px;transition:var(--ease);flex-shrink:0}
.heart-btn:hover{background:rgba(236,72,153,.25);transform:translateY(-2px) scale(1.05)}
.heart-btn i{animation:beat 1.6s infinite}
@keyframes beat{0%,60%,100%{transform:scale(1)}20%{transform:scale(1.25)}40%{transform:scale(1.05)}}
@media(max-width:820px){.donate{grid-template-columns:1fr}.d-card{padding:22px}}

/* ===== BAHASA / RTL ===== */
.lang{height:42px;padding:0 10px;border-radius:12px;border:1px solid var(--line);background:var(--card);color:var(--text);font-size:13px;font-weight:600;cursor:pointer;outline:none;max-width:118px;flex-shrink:0;transition:var(--ease)}
.lang:hover,.lang:focus{border-color:var(--violet)}
.lang option{background:#0d1030;color:#fff}
.term-body,.term-head,.d-id code,.uid,.prog-bot,.metric strong,.time{direction:ltr}
.term-body,.term-head{text-align:left}
[dir=rtl] .sidebar{left:auto;right:0;transform:translateX(102%);border-right:0;border-left:1px solid var(--line);box-shadow:-20px 0 60px rgba(0,0,0,.5)}
[dir=rtl] body.menu-open .sidebar{transform:none}
[dir=rtl] .nav-item{text-align:right}
[dir=rtl] .nav-item:hover{transform:translateX(-4px)}
[dir=rtl] .nav-item.active::before{left:auto;right:-18px;border-radius:4px 0 0 4px}
[dir=rtl] .node::before{left:auto;right:0}
[dir=rtl] .search i{left:auto;right:15px}
[dir=rtl] .search input{padding:12px 40px 12px 14px}
[dir=rtl] .info-row b{text-align:left}
[dir=rtl] .d-card::before{right:auto;left:-60px}
[dir=rtl] .toasts{align-items:flex-start}
@media(max-width:600px){.lang{max-width:84px;padding:0 6px;font-size:12px}}
</style>
</head>
<body>
<div class="bg"><div class="orb a"></div><div class="orb b"></div><div class="orb c"></div></div>

<header class="topbar">
  <button class="menu-btn" id="menuBtn" aria-label="Buka menu" aria-expanded="false"><i class="fa-solid fa-bars"></i></button>
  <div class="top-title"><span id="topTitle">Command Core</span><small>CGU TEAM</small></div>
  <div class="pill" id="pill"><i class="dot"></i><span id="side-status">ONLINE</span></div>
  <select class="lang" id="lang" aria-label="Language"><option value="id">Indonesia</option><option value="ar">العربية</option><option value="ne">नेपाली</option><option value="en">English</option><option value="hi">हिन्दी</option></select>
  <button class="heart-btn" onclick="document.querySelector('[data-page=donate]').click()" aria-label="Donasi" title="Donasi"><i class="fa-solid fa-heart"></i></button>
</header>

<div class="overlay" id="overlay"></div>
<nav class="sidebar" id="sidebar" aria-label="Menu utama">
  <div class="brand">
    <div class="brand-icon"><i class="fa-solid fa-skull"></i></div>
    <div><div class="brand-name">CGU TEAM</div><div class="brand-sub">Real-Time Command Center</div></div>
  </div>
  <div class="nav">
    <button class="nav-item active" data-page="core" data-title="Command Core"><i class="fa-solid fa-gauge-high"></i>Command Core</button>
    <button class="nav-item" data-page="targets" data-title="Target Nodes"><i class="fa-solid fa-network-wired"></i>Target Nodes</button>
    <button class="nav-item" data-page="terminal" data-title="Uplink Terminal"><i class="fa-solid fa-terminal"></i>Uplink Terminal</button>
    <button class="nav-item" data-page="profile" data-title="Profil CGU TEAM"><i class="fa-solid fa-id-badge"></i>Profil CGU TEAM</button>
    <button class="nav-item" data-page="donate" data-title="Donasi"><i class="fa-solid fa-heart"></i>Donasi</button>
  </div>
  <div class="side-foot">Status mesin<b id="side-status-2">ONLINE</b></div>
</nav>

<main class="main">
  <section id="page-core" class="page active">
    <div class="page-head">
      <div><h1 class="page-title">Command Core</h1><p class="page-sub">Analitik sistem secara real-time</p></div>
      <button class="btn primary" onclick="fetchStats()"><i class="fa-solid fa-rotate"></i>Sinkronkan</button>
    </div>
    <div class="stats">
      <div class="stat"><div class="stat-icon"><i class="fa-solid fa-diagram-project"></i></div><div class="stat-val" id="stat-accounts">0</div><div class="stat-label">Total node terhubung</div><div class="stat-foot" id="stat-online">0 Online</div></div>
      <div class="stat"><div class="stat-icon"><i class="fa-solid fa-bolt"></i></div><div class="stat-val" id="stat-started">0</div><div class="stat-label">Eksekusi dimulai</div><div class="stat-foot" id="stat-per-hour">~0 / jam</div></div>
      <div class="stat"><div class="stat-icon"><i class="fa-solid fa-fire-flame-curved"></i></div><div class="stat-val" id="stat-exp">+0</div><div class="stat-label">Total EXP terkumpul</div><div class="stat-foot" id="stat-exp-rate">~0 EXP/jam</div></div>
      <div class="stat"><div class="stat-icon"><i class="fa-solid fa-clock"></i></div><div class="stat-val" id="stat-uptime">00:00:00</div><div class="stat-label">Uptime sistem</div><div class="stat-foot" id="stat-active-matches">0 Active</div></div>
    </div>
  </section>

  <section id="page-targets" class="page">
    <div class="page-head">
      <div><h1 class="page-title">Target Nodes</h1><p class="page-sub">Kelola akun yang terhubung</p></div>
      <div class="row">
        <button class="btn" id="btn-pause-all" onclick="togglePauseAll()"><i class="fa-solid fa-pause"></i> Pause All</button>
        <button class="btn primary" onclick="openAddModal()"><i class="fa-solid fa-plus"></i> Inject Node</button>
      </div>
    </div>
    <div class="batch-box">
      <div class="batch-head">
        <div><div class="batch-title"><i class="fa-solid fa-file-arrow-up"></i> JSON Batch Import</div><div class="batch-sub">একবার JSON upload করে Start + Count দিয়ে নির্দিষ্ট account range চালু করুন। JSON server-এ আলাদা করে রাখা হয় না।</div></div>
        <button class="btn" type="button" onclick="useNextBatch()"><i class="fa-solid fa-forward"></i> Next Batch</button>
      </div>
      <div class="batch-grid">
        <div class="field file-field"><label>Account JSON</label><input id="batch-file" type="file" accept=".json,application/json" onchange="previewBatchFile()"></div>
        <div class="field"><label>Start account #</label><input id="batch-start" type="number" min="1" value="1" oninput="updateBatchPreview()"></div>
        <div class="field"><label>How many</label><input id="batch-count" type="number" min="1" max="500" value="10" oninput="updateBatchPreview()"></div>
        <div class="row batch-actions">
          <button class="btn primary" type="button" onclick="submitBatchImport()"><i class="fa-solid fa-upload"></i> Import Range</button>
          <button class="btn batch-danger" type="button" onclick="deleteAllAccounts()"><i class="fa-solid fa-trash-can"></i> Delete All</button>
        </div>
      </div>
      <div class="batch-preview" id="batch-preview">JSON select করলে এখানে মোট account ও selected range দেখাবে। উদাহরণ: Start 1 + Count 10 → Accounts 1–10.</div>
    </div>
    <div class="controls">
      <div class="search"><i class="fa-solid fa-magnifying-glass"></i><input id="account-search" type="text" placeholder="Cari UID atau nickname..." oninput="filterAccounts()"></div>
      <div class="seg" id="node-filters">
        <button class="active" onclick="setFilter('all',this)">Semua</button>
        <button onclick="setFilter('in_match',this)">Match</button>
        <button onclick="setFilter('online',this)">Online</button>
        <button onclick="setFilter('paused',this)">Paused</button>
      </div>
    </div>
    <div class="grid" id="accounts-container">
      <div class="empty"><i class="fa-solid fa-circle-notch fa-spin"></i>Menghubungkan ke backend...</div>
    </div>
  </section>

  <section id="page-terminal" class="page">
    <div class="page-head">
      <div><h1 class="page-title">Uplink Terminal</h1><p class="page-sub">Log eksekusi backend langsung</p></div>
      <div class="row">
        <button class="btn" id="btn-autoscroll" onclick="toggleAutoScroll()"><i class="fa-solid fa-arrow-down"></i> Auto-scroll</button>
        <button class="btn primary" onclick="clearLogs()"><i class="fa-solid fa-trash"></i> Hapus log</button>
      </div>
    </div>
    <div class="controls">
      <div class="seg" id="log-filters">
        <button class="active" onclick="setLogFilter('all',this)">Semua</button>
        <button onclick="setLogFilter('match',this)">Match</button>
        <button onclick="setLogFilter('success',this)">EXP / Sukses</button>
        <button onclick="setLogFilter('error',this)">Error</button>
      </div>
    </div>
    <div class="term">
      <div class="term-head">CGU_TEAM@backend:~#</div>
      <div class="term-body" id="console-stream" onscroll="handleLogScroll()"></div>
    </div>
  </section>

  <section id="page-profile" class="page">
    <div class="page-head">
      <div><h1 class="page-title">Profil Tim</h1><p class="page-sub">Identitas dan ringkasan operasional</p></div>
    </div>
    <div class="hero">
      <div class="hero-banner"></div>
      <div class="hero-body">
        <div class="hero-avatar">CGU</div>
        <div>
          <div class="hero-name">CGU TEAM</div>
          <div class="hero-tag">Real-Time Command Center</div>
        </div>
        <div class="chips">
          <span class="chip"><i class="fa-solid fa-shield-halved"></i>Admin</span>
          <span class="chip"><i class="fa-solid fa-circle-check"></i><span id="p-status">Online</span></span>
        </div>
      </div>
    </div>
    <div class="stats">
      <div class="stat"><div class="stat-icon"><i class="fa-solid fa-diagram-project"></i></div><div class="stat-val" id="p-nodes">0</div><div class="stat-label">Node dikelola</div></div>
      <div class="stat"><div class="stat-icon"><i class="fa-solid fa-bolt"></i></div><div class="stat-val" id="p-matches">0</div><div class="stat-label">Eksekusi dimulai</div></div>
      <div class="stat"><div class="stat-icon"><i class="fa-solid fa-fire-flame-curved"></i></div><div class="stat-val" id="p-exp">+0</div><div class="stat-label">Total EXP terkumpul</div></div>
      <div class="stat"><div class="stat-icon"><i class="fa-solid fa-gauge-high"></i></div><div class="stat-val" id="p-rate">0</div><div class="stat-label">EXP per jam</div></div>
    </div>
    <div class="info">
      <div class="info-row"><span>Nama tim</span><b>CGU TEAM</b></div>
      <div class="info-row"><span>Dashboard</span><b>Command Center</b></div>
      <div class="info-row"><span>Peran</span><b>Administrator</b></div>
      <div class="info-row"><span>Uptime sesi</span><b id="p-uptime">00:00:00</b></div>
    </div>
  </section>

  <div class="modal" id="supportModal">
  <div class="card" style="text-align:center">
    <div class="d-heart" style="margin:0 auto 16px"><i class="fa-solid fa-heart"></i></div>
    <h2>SUPPORT CREATOR</h2>
    <p style="margin-bottom:0">Support the development of CGU TEAM through Binance Pay.</p>
    <div class="d-label" style="justify-content:center"><i class="fa-solid fa-circle-dollar-to-slot"></i>BINANCE PAY ID</div>
    <div class="d-id">
      <code>1282491012</code>
      <button class="btn gold" onclick="copyText('1282491012','Binance ID')"><i class="fa-regular fa-copy"></i>Salin</button>
    </div>
    <div class="card-actions" style="justify-content:center">
      <button type="button" class="btn" onclick="closeSupport()">Close</button>
    </div>
  </div>
  </div>

  <section id="page-donate" class="page">
    <div class="page-head">
      <div><h1 class="page-title">Donasi</h1><p class="page-sub">Dukung pengembangan CGU TEAM</p></div>
    </div>
    <div class="donate">
      <div class="d-card">
        <div class="d-heart"><i class="fa-solid fa-heart"></i></div>
        <h2>Terima kasih sudah mendukung</h2>
        <p>Donasi kamu membantu menjaga server tetap menyala dan mendorong pengembangan fitur baru. Berapa pun jumlahnya sangat berarti.</p>
        <div class="d-label"><i class="fa-solid fa-circle-dollar-to-slot"></i>BINANCE PAY ID</div>
        <div class="d-id">
          <code id="binance-id">1282491012</code>
          <button class="btn gold" onclick="copyText('1282491012','Binance ID')"><i class="fa-regular fa-copy"></i>Salin</button>
        </div>
      </div>
      <div class="d-card">
        <h2 style="font-size:18px;margin-bottom:18px">Cara donasi</h2>
        <ol class="steps">
          <li><span data-i="s1">Buka aplikasi <b>Binance</b> lalu pilih <b>Pay</b></span></li>
          <li><span data-i="s2">Pilih <b>Send</b> dan masukkan Binance ID di samping</span></li>
          <li><span data-i="s3">Isi jumlah donasi, lalu konfirmasi pembayaran</span></li>
        </ol>
        <div class="d-note"><i class="fa-solid fa-triangle-exclamation"></i> <span data-i="note">Periksa kembali ID sebelum mengirim. Transaksi kripto tidak bisa dibatalkan.</span></div>
      </div>
    </div>
  </section>
</main>

<div class="modal" id="addModal">
  <div class="card">
    <h2>Inject node baru</h2>
    <p>Masukkan kredensial untuk menjalankan instance baru di server.</p>
    <form onsubmit="submitAddAccount(event)">
      <div class="field"><label>Tipe autentikasi</label>
        <select id="acc-type" onchange="toggleFormType()">
          <option value="guest">Guest (UID / Password)</option>
          <option value="token">Access Token</option>
        </select></div>
      <div id="guest-inputs">
        <div class="field"><label>UID</label><input type="text" id="acc-uid" placeholder="Masukkan UID" autocomplete="off"></div>
        <div class="field"><label>Password / Key</label><input type="password" id="acc-password" placeholder="••••••••••••" autocomplete="off"></div>
      </div>
      <div id="token-inputs" style="display:none"><div class="field"><label>Access token</label><textarea id="acc-token" placeholder="Tempel token lengkap di sini..."></textarea></div></div>
      <div class="card-actions">
        <button type="button" class="btn" onclick="closeAddModal()">Batal</button>
        <button type="submit" class="btn primary"><i class="fa-solid fa-rocket"></i> Deploy node</button>
      </div>
    </form>
  </div>
</div>

<div class="toasts" id="toastBox"></div>

<script>
  function closeSupport(){ document.getElementById("supportModal").classList.remove("active"); }
document.getElementById("supportModal").addEventListener("click", e => { if(e.target.id === "supportModal") closeSupport(); });
setTimeout(() => document.getElementById("supportModal").classList.add("active"), 600);
</script>

<script>
const EXP_TABLE = {
1:0,2:48,3:202,4:544,5:1012,6:1844,7:2792,8:3800,9:4870,10:6004,
11:7192,12:8448,13:9760,14:11140,15:12566,16:14060,17:15610,18:17224,19:18902,20:20632,
21:22424,22:24278,23:26192,24:28166,25:30200,26:32294,27:34448,28:37804,29:41274,30:44870,
31:48582,32:53394,33:58566,34:64096,35:69994,36:76460,37:83506,38:91128,39:99322,40:108092,
41:120144,42:133266,43:147472,44:162760,45:179126,46:196572,47:215368,48:235516,49:257010,50:279860,
51:304056,52:348318,53:394982,54:444044,55:495508,56:549364,57:633756,58:721744,59:813336,60:908522,
61:1041438,62:1180352,63:1325266,64:1476184,65:1634300,66:1840946,67:2056594,68:2281242,69:2514880,70:2757530,
71:3059506,72:3372284,73:3699456,74:4041030,75:4397002,76:4829104,77:5282204,78:5756304,79:6251408,80:6776502,
81:7381324,82:8043154,83:8752982,84:9510808,85:10316338,86:11277190,87:12291748,88:13360304,89:14482858,90:15659418,
91:17026708,92:18453950,93:19941280,94:21488570,95:23095858,96:24763138,97:26490428,98:28378704,99:30124996,100:32032884
};
let cachedLogs = [], activeFilter = "all", activeLogFilter = "all", autoScroll = true, clientStart = Date.now();


/* ---------- BAHASA (i18n) ---------- */
const LG=["en","ar","ne","hi"], D={id:{},en:{},ar:{},ne:{},hi:{}};
const T=[
["Real-Time Command Center","Real-Time Command Center","مركز القيادة المباشر","रियल-टाइम कमान्ड सेन्टर","रियल-टाइम कमांड सेंटर"],
["Command Core","Command Core","مركز التحكم","कमान्ड कोर","कमांड कोर"],
["Target Nodes","Target Nodes","العقد المستهدفة","टार्गेट नोडहरू","टारगेट नोड्स"],
["Uplink Terminal","Uplink Terminal","طرفية الاتصال","अपलिङ्क टर्मिनल","अपलिंक टर्मिनल"],
["Profil CGU TEAM","CGU TEAM Profile","ملف CGU TEAM","CGU TEAM प्रोफाइल","CGU TEAM प्रोफ़ाइल"],
["Donasi","Donate","تبرّع","दान","दान करें"],
["Status mesin","Engine status","حالة المحرك","इन्जिन स्थिति","इंजन स्थिति"],
["Analitik sistem secara real-time","Real-time system analytics","تحليلات النظام المباشرة","रियल-टाइम प्रणाली विश्लेषण","रियल-टाइम सिस्टम एनालिटिक्स"],
["Sinkronkan","Sync","مزامنة","सिंक गर्नुहोस्","सिंक करें"],
["Total node terhubung","Total linked nodes","إجمالي العقد المتصلة","जोडिएका कुल नोडहरू","कुल जुड़े नोड्स"],
["Eksekusi dimulai","Executions started","عمليات التنفيذ المبدوءة","सुरु गरिएका कार्यान्वयन","शुरू किए गए निष्पादन"],
["Total EXP terkumpul","Total EXP harvested","إجمالي EXP المجمّع","जम्मा गरिएको कुल EXP","कुल एकत्रित EXP"],
["Uptime sistem","System uptime","مدة تشغيل النظام","प्रणाली अपटाइम","सिस्टम अपटाइम"],
["Kelola akun yang terhubung","Manage connected accounts","إدارة الحسابات المتصلة","जोडिएका खाताहरू व्यवस्थापन गर्नुहोस्","जुड़े हुए खातों को प्रबंधित करें"],
["Pause All","Pause All","إيقاف الكل مؤقتًا","सबै रोक्नुहोस्","सभी रोकें"],
["Resume All","Resume All","استئناف الكل","सबै सुचारु गर्नुहोस्","सभी फिर शुरू करें"],
["Inject Node","Inject Node","إضافة عقدة","नोड थप्नुहोस्","नोड जोड़ें"],
["Semua","All","الكل","सबै","सभी"],
["Match","Match","مباراة","म्याच","मैच"],
["Online","Online","متصل","अनलाइन","ऑनलाइन"],
["Paused","Paused","متوقف مؤقتًا","रोकिएको","रुका हुआ"],
["Menghubungkan ke backend...","Connecting to backend...","جارٍ الاتصال بالخادم...","ब्याकएन्डमा जडान हुँदैछ...","बैकएंड से कनेक्ट हो रहा है..."],
["Log eksekusi backend langsung","Live backend execution logs","سجلات تنفيذ الخادم المباشرة","ब्याकएन्ड कार्यान्वयन लाइभ लग","बैकएंड निष्पादन लॉग लाइव"],
["Auto-scroll","Auto-scroll","تمرير تلقائي","अटो-स्क्रोल","ऑटो-स्क्रॉल"],
["Hapus log","Clear logs","مسح السجلات","लग मेटाउनुहोस्","लॉग साफ़ करें"],
["EXP / Sukses","EXP / Success","EXP / نجاح","EXP / सफल","EXP / सफल"],
["Error","Error","أخطاء","त्रुटि","त्रुटि"],
["Profil Tim","Team Profile","ملف الفريق","टोली प्रोफाइल","टीम प्रोफ़ाइल"],
["Identitas dan ringkasan operasional","Identity and operational summary","الهوية وملخص العمليات","पहिचान र सञ्चालन सारांश","पहचान और संचालन सारांश"],
["Admin","Admin","مشرف","एडमिन","एडमिन"],
["Node dikelola","Nodes managed","العقد المُدارة","व्यवस्थापित नोडहरू","प्रबंधित नोड्स"],
["EXP per jam","EXP per hour","EXP في الساعة","प्रति घण्टा EXP","प्रति घंटा EXP"],
["Nama tim","Team name","اسم الفريق","टोलीको नाम","टीम का नाम"],
["Dashboard","Dashboard","لوحة التحكم","ड्यासबोर्ड","डैशबोर्ड"],
["Peran","Role","الدور","भूमिका","भूमिका"],
["Uptime sesi","Session uptime","مدة الجلسة","सत्र अपटाइम","सत्र अपटाइम"],
["Command Center","Command Center","مركز القيادة","कमान्ड सेन्टर","कमांड सेंटर"],
["Administrator","Administrator","مسؤول","प्रशासक","प्रशासक"],
["Dukung pengembangan CGU TEAM","Support CGU TEAM development","ادعم تطوير CGU TEAM","CGU TEAM को विकासमा सहयोग गर्नुहोस्","CGU TEAM के विकास में सहयोग करें"],
["Terima kasih sudah mendukung","Thank you for your support","شكرًا لدعمك","सहयोगका लागि धन्यवाद","सहयोग के लिए धन्यवाद"],
["Donasi kamu membantu menjaga server tetap menyala dan mendorong pengembangan fitur baru. Berapa pun jumlahnya sangat berarti.","Your donation helps keep the servers running and drives new feature development. Every amount means a lot.","تبرعك يساعد في إبقاء الخوادم تعمل ويدعم تطوير ميزات جديدة. كل مبلغ له قيمة كبيرة.","तपाईंको दानले सर्भर चलिरहन र नयाँ सुविधाहरू विकास गर्न मद्दत गर्छ। जतिसुकै रकम पनि अत्यन्त महत्त्वपूर्ण छ।","आपके दान से सर्वर चालू रहते हैं और नई सुविधाओं का विकास होता है। हर राशि बहुत मायने रखती है।"],
["Salin","Copy","نسخ","प्रतिलिपि","कॉपी करें"],
["Cara donasi","How to donate","طريقة التبرع","दान गर्ने तरिका","दान कैसे करें"],
["Inject node baru","Inject new node","إضافة عقدة جديدة","नयाँ नोड थप्नुहोस्","नया नोड जोड़ें"],
["Masukkan kredensial untuk menjalankan instance baru di server.","Enter credentials to run a new instance on the server.","أدخل بيانات الاعتماد لتشغيل نسخة جديدة على الخادم.","सर्भरमा नयाँ इन्स्ट्यान्स चलाउन क्रेडेन्सियल प्रविष्ट गर्नुहोस्।","सर्वर पर नया इंस्टेंस चलाने के लिए क्रेडेंशियल दर्ज करें।"],
["Tipe autentikasi","Authentication type","نوع المصادقة","प्रमाणीकरण प्रकार","प्रमाणीकरण प्रकार"],
["Guest (UID / Password)","Guest (UID / Password)","ضيف (UID / كلمة المرور)","गेस्ट (UID / पासवर्ड)","गेस्ट (UID / पासवर्ड)"],
["Access Token","Access Token","رمز الوصول","एक्सेस टोकन","एक्सेस टोकन"],
["Password / Key","Password / Key","كلمة المرور / المفتاح","पासवर्ड / की","पासवर्ड / की"],
["Access token","Access token","رمز الوصول","एक्सेस टोकन","एक्सेस टोकन"],
["Batal","Cancel","إلغاء","रद्द गर्नुहोस्","रद्द करें"],
["Deploy node","Deploy node","تشغيل العقدة","नोड डिप्लोय गर्नुहोस्","नोड डिप्लॉय करें"],
["Cari UID atau nickname...","Search UID or nickname...","ابحث عن UID أو الاسم...","UID वा उपनाम खोज्नुहोस्...","UID या निकनेम खोजें..."],
["Masukkan UID","Enter UID","أدخل UID","UID प्रविष्ट गर्नुहोस्","UID दर्ज करें"],
["Tempel token lengkap di sini...","Paste the full token here...","الصق الرمز كاملًا هنا...","पूरा टोकन यहाँ टाँस्नुहोस्...","पूरा टोकन यहाँ पेस्ट करें..."],
["ONLINE","ONLINE","متصل","अनलाइन","ऑनलाइन"],
["OFFLINE","OFFLINE","غير متصل","अफलाइन","ऑफ़लाइन"],
["Offline","Offline","غير متصل","अफलाइन","ऑफ़लाइन"],
["PAUSED","PAUSED","متوقف","रोकिएको","रुका हुआ"],
["IN MATCH","IN MATCH","في مباراة","म्याचमा","मैच में"],
["SEARCHING","SEARCHING","جارٍ البحث","खोजिँदैछ","खोज रहा है"],
["Base EXP","Base EXP","EXP الأساسي","आधार EXP","बेस EXP"],
["Current","Current","الحالي","हालको","वर्तमान"],
["Harvested","Harvested","المجمّع","संकलित","एकत्रित"],
["{0} EXP lagi","{0} EXP left","متبقي {0} EXP","{0} EXP बाँकी","{0} EXP शेष"],
["Salin UID","Copy UID","نسخ UID","UID कपी गर्नुहोस्","UID कॉपी करें"],
["Resume","Resume","استئناف","सुचारु गर्नुहोस्","फिर शुरू करें"],
["Pause","Pause","إيقاف مؤقت","रोक्नुहोस्","रोकें"],
["Restart","Restart","إعادة التشغيل","पुनः सुरु गर्नुहोस्","पुनः आरंभ करें"],
["Sync","Sync","مزامنة","सिंक","सिंक"],
["Hapus","Delete","حذف","मेटाउनुहोस्","हटाएं"],
["UID dan password wajib diisi","UID and password are required","UID وكلمة المرور مطلوبان","UID र पासवर्ड आवश्यक छ","UID और पासवर्ड आवश्यक हैं"],
["Token wajib diisi","Token is required","الرمز مطلوب","टोकन आवश्यक छ","टोकन आवश्यक है"],
["Node berhasil di-deploy","Node deployed successfully","تم تشغيل العقدة بنجاح","नोड सफलतापूर्वक डिप्लोय भयो","नोड सफलतापूर्वक डिप्लॉय हुआ"],
["Gagal deploy node","Failed to deploy node","فشل تشغيل العقدة","नोड डिप्लोय गर्न असफल","नोड डिप्लॉय करने में विफल"],
["Koneksi ke backend gagal","Backend connection failed","فشل الاتصال بالخادم","ब्याकएन्ड जडान असफल","बैकएंड कनेक्शन विफल"],
["Hapus node {0}? Tindakan ini tidak bisa dibatalkan.","Delete node {0}? This cannot be undone.","حذف العقدة {0}؟ لا يمكن التراجع عن هذا الإجراء.","नोड {0} मेटाउने? यो कार्य पूर्ववत गर्न सकिँदैन।","नोड {0} हटाएं? यह क्रिया पूर्ववत नहीं की जा सकती।"],
["Node {0} dihapus","Node {0} deleted","تم حذف العقدة {0}","नोड {0} मेटाइयो","नोड {0} हटा दिया गया"],
["Gagal menghapus","Failed to delete","فشل الحذف","मेटाउन असफल","हटाने में विफल"],
["Sinkronisasi {0}...","Syncing {0}...","جارٍ مزامنة {0}...","{0} सिंक हुँदैछ...","{0} सिंक हो रहा है..."],
["Sinkronisasi gagal","Sync failed","فشلت المزامنة","सिंक असफल","सिंक विफल"],
["Restart proses {0}...","Restarting process {0}...","جارٍ إعادة تشغيل {0}...","{0} प्रक्रिया पुनः सुरु हुँदैछ...","{0} प्रक्रिया पुनः आरंभ हो रही है..."],
["Restart gagal","Restart failed","فشلت إعادة التشغيل","पुनः सुरु असफल","पुनः आरंभ विफल"],
["{0} dijeda","{0} paused","تم إيقاف {0} مؤقتًا","{0} रोकियो","{0} रोका गया"],
["{0} dilanjutkan","{0} resumed","تم استئناف {0}","{0} सुचारु भयो","{0} फिर शुरू हुआ"],
["Aksi gagal","Action failed","فشل الإجراء","कार्य असफल","क्रिया विफल"],
["Semua node dijeda","All nodes paused","تم إيقاف كل العقد مؤقتًا","सबै नोड रोकिए","सभी नोड रोके गए"],
["Semua node berjalan","All nodes running","كل العقد تعمل","सबै नोड चलिरहेका छन्","सभी नोड चल रहे हैं"],
["Gagal","Failed","فشل","असफल","विफल"],
["Belum ada node aktif.","No active nodes yet.","لا توجد عقد نشطة بعد.","अहिलेसम्म कुनै सक्रिय नोड छैन।","अभी कोई सक्रिय नोड नहीं है।"],
["Inject node pertama","Inject your first node","أضف أول عقدة","पहिलो नोड थप्नुहोस्","पहला नोड जोड़ें"],
["Log server dibersihkan","Server logs cleared","تم مسح سجلات الخادم","सर्भर लग मेटाइयो","सर्वर लॉग साफ़ किए गए"],
["Gagal menghapus log di backend","Failed to clear logs on backend","فشل مسح السجلات على الخادم","ब्याकएन्डमा लग मेटाउन असफल","बैकएंड पर लॉग साफ़ करने में विफल"],
["{0} disalin: {1}","{0} copied: {1}","تم نسخ {0}: {1}","{0} कपी गरियो: {1}","{0} कॉपी किया गया: {1}"],
["{0} Node terhubung","{0} nodes connected","{0} عقدة متصلة","{0} नोड जोडिएका","{0} नोड जुड़े"],
["~{0} / jam","~{0} / hour","~{0} / ساعة","~{0} / घण्टा","~{0} / घंटा"],
["~{0} EXP/jam","~{0} EXP/hr","~{0} EXP/ساعة","~{0} EXP/घण्टा","~{0} EXP/घंटा"],
["{0} Aktif","{0} Active","{0} نشط","{0} सक्रिय","{0} सक्रिय"],
["s1","Open the <b>Binance</b> app and choose <b>Pay</b>","افتح تطبيق <b>Binance</b> واختر <b>Pay</b>","<b>Binance</b> एप खोल्नुहोस् र <b>Pay</b> छान्नुहोस्","<b>Binance</b> ऐप खोलें और <b>Pay</b> चुनें"],
["s2","Choose <b>Send</b> and enter the Binance ID shown beside","اختر <b>Send</b> وأدخل معرّف Binance الظاهر بجانبه","<b>Send</b> छान्नुहोस् र छेउमा देखाइएको Binance ID हाल्नुहोस्","<b>Send</b> चुनें और बगल में दिखाया गया Binance ID दर्ज करें"],
["s3","Enter the donation amount, then confirm the payment","أدخل مبلغ التبرع ثم أكّد الدفع","दान रकम राख्नुहोस्, त्यसपछि भुक्तानी पुष्टि गर्नुहोस्","दान की राशि दर्ज करें, फिर भुगतान की पुष्टि करें"],
["note","Double-check the ID before sending. Crypto transactions cannot be reversed.","تحقق من المعرّف جيدًا قبل الإرسال. لا يمكن التراجع عن معاملات العملات الرقمية.","पठाउनु अघि ID दोहोर्‍याएर जाँच गर्नुहोस्। क्रिप्टो लेनदेन फिर्ता गर्न सकिँदैन।","भेजने से पहले ID दोबारा जांच लें। क्रिप्टो लेनदेन वापस नहीं किए जा सकते।"]
];
T.forEach(r => LG.forEach((l,i) => D[l][r[0]] = r[i+1]));
const ID_HTML = {
  s1:"Buka aplikasi <b>Binance</b> lalu pilih <b>Pay</b>",
  s2:"Pilih <b>Send</b> dan masukkan Binance ID di samping",
  s3:"Isi jumlah donasi, lalu konfirmasi pembayaran",
  note:"Periksa kembali ID sebelum mengirim. Transaksi kripto tidak bisa dibatalkan."
};
const PH = {"account-search":"Cari UID atau nickname...","acc-uid":"Masukkan UID","acc-token":"Tempel token lengkap di sini..."};
let lang = "id";
function t(key, ...a){
  let s = lang === "id" ? (ID_HTML[key] ?? key) : ((D[lang] && D[lang][key]) ?? key);
  return s.replace(/\{(\d)\}/g, (m,i) => a[i] ?? m);
}
function walkText(root){
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {acceptNode: n =>
    n.parentElement && n.parentElement.closest("#console-stream,#toastBox,script,style") ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT});
  let n;
  while((n = w.nextNode())){
    const raw = n.nodeValue, key = n._k || raw.trim();
    if(!key || (!n._k && !(key in D.en))) continue;
    n._k = key;
    const tr = t(key), cur = raw.trim();
    n.nodeValue = raw.replace(cur, () => tr);
  }
}
function applyLang(l, refetch = true){
  if(!D[l] && l !== "id") l = "id";
  lang = l;
  try{ localStorage.setItem("lang", l); }catch(e){}
  document.documentElement.lang = l;
  document.documentElement.dir = l === "ar" ? "rtl" : "ltr";
  document.getElementById("lang").value = l;
  walkText(document.body);
  document.querySelectorAll("[data-i]").forEach(el => { el.innerHTML = t(el.dataset.i); });
  for(const id in PH){ const el = document.getElementById(id); if(el) el.placeholder = t(PH[id]); }
  const act = document.querySelector(".nav-item.active");
  if(act) document.getElementById("topTitle").textContent = t(act.dataset.title);
  setStatus(lastOn);
  if(refetch) fetchStats();
}
document.getElementById("lang").addEventListener("change", e => applyLang(e.target.value));

/* ---------- SIDEBAR: buka lewat tombol, tutup dengan klik di mana saja ---------- */
const menuBtn = document.getElementById("menuBtn");
function setMenu(open){
  document.body.classList.toggle("menu-open", open);
  menuBtn.setAttribute("aria-expanded", open);
}
menuBtn.addEventListener("click", e => { e.stopPropagation(); setMenu(!document.body.classList.contains("menu-open")); });
document.addEventListener("click", () => { if(document.body.classList.contains("menu-open")) setMenu(false); });
document.addEventListener("keydown", e => { if(e.key === "Escape"){ setMenu(false); closeAddModal(); } });
document.getElementById("addModal").addEventListener("click", e => { if(e.target.id === "addModal") closeAddModal(); });

document.querySelectorAll(".nav-item").forEach(btn => btn.addEventListener("click", () => {
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  btn.classList.add("active");
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  document.getElementById("page-" + btn.dataset.page).classList.add("active");
  document.getElementById("topTitle").textContent = t(btn.dataset.title);
}));

/* ---------- UI helpers ---------- */
function toast(message, type = "info"){
  message = t(message);
  const box = document.getElementById("toastBox"), el = document.createElement("div");
  el.className = "toast " + type;
  const ic = type === "success" ? '<i class="fa-solid fa-check" style="color:var(--ok)"></i>'
           : type === "error" ? '<i class="fa-solid fa-triangle-exclamation" style="color:var(--err)"></i>'
           : '<i class="fa-solid fa-circle-info" style="color:var(--violet)"></i>';
  el.innerHTML = `${ic}<span>${esc(message)}</span>`;
  box.appendChild(el);
  setTimeout(() => { el.classList.add("hide"); setTimeout(() => el.remove(), 400); }, 4000);
}
function openAddModal(){ document.getElementById("addModal").classList.add("active"); }
function closeAddModal(){ document.getElementById("addModal").classList.remove("active"); }
function toggleFormType(){
  const t = document.getElementById("acc-type").value;
  document.getElementById("guest-inputs").style.display = t === "guest" ? "block" : "none";
  document.getElementById("token-inputs").style.display = t === "token" ? "block" : "none";
}

/* ---------- API actions ---------- */
async function post(url, body){
  const r = await fetch(url, {method:"POST", headers:{"Content-Type":"application/json"}, body: body ? JSON.stringify(body) : undefined});
  return r.json();
}
async function submitAddAccount(e){
  e.preventDefault();
  const type = document.getElementById("acc-type").value;
  let payload;
  if(type === "guest"){
    const uid = document.getElementById("acc-uid").value.trim(), pass = document.getElementById("acc-password").value.trim();
    if(!uid || !pass){ toast("UID dan password wajib diisi", "error"); return; }
    payload = {uid, password: pass};
  } else {
    const token = document.getElementById("acc-token").value.trim();
    if(!token){ toast("Token wajib diisi", "error"); return; }
    payload = {token};
  }
  try{
    const d = await post("/api/account/add", payload);
    if(d.status === "ok"){ closeAddModal(); toast("Node berhasil di-deploy", "success"); fetchStats(); }
    else toast(d.error || "Gagal deploy node", "error");
  }catch(err){ toast("Koneksi ke backend gagal", "error"); }
}
let batchJsonTotal = 0;
let batchJsonValid = false;

function getBatchRange(){
  const start = Math.max(1, parseInt(document.getElementById("batch-start").value || "1", 10));
  const count = Math.max(1, Math.min(500, parseInt(document.getElementById("batch-count").value || "1", 10)));
  return {start, count};
}

async function previewBatchFile(){
  const input = document.getElementById("batch-file"), preview = document.getElementById("batch-preview");
  batchJsonTotal = 0; batchJsonValid = false;
  if(!input.files || !input.files[0]){ updateBatchPreview(); return; }
  try{
    const text = await input.files[0].text();
    const data = JSON.parse(text.replace(/^\uFEFF/, ""));
    const list = Array.isArray(data) ? data : (Array.isArray(data.accounts) ? data.accounts : (Array.isArray(data.data) ? data.data : data.users));
    if(!Array.isArray(list)) throw new Error("JSON array/account list পাওয়া যায়নি");
    batchJsonTotal = list.length; batchJsonValid = batchJsonTotal > 0;
    updateBatchPreview();
  }catch(e){
    preview.innerHTML = '<strong style="color:var(--err)">Invalid JSON:</strong> ' + esc(e.message || "Could not read JSON");
  }
}

function updateBatchPreview(){
  const preview = document.getElementById("batch-preview");
  const {start,count} = getBatchRange();
  if(!batchJsonTotal){
    preview.innerHTML = 'JSON select করলে এখানে মোট account ও selected range দেখাবে। উদাহরণ: Start 1 + Count 10 → Accounts 1–10.';
    return;
  }
  if(start > batchJsonTotal){
    preview.innerHTML = '<strong style="color:var(--err)">Start #' + start + ' is outside JSON.</strong> Total accounts: ' + batchJsonTotal;
    return;
  }
  const end = Math.min(batchJsonTotal, start + count - 1);
  preview.innerHTML = '<strong>Total: ' + batchJsonTotal + '</strong> · Selected: <strong>' + start + '–' + end + '</strong> (' + (end-start+1) + ' account' + ((end-start+1)!==1?'s':'') + ')';
}

function useNextBatch(){
  const d = window.lastImportState || {};
  const next = Number(d.last_end || 0) + 1;
  if(next > 1) document.getElementById("batch-start").value = next;
  updateBatchPreview();
  toast(next > 1 ? "Next batch start set to #" + next : "Start is already #1", "success");
}

async function submitBatchImport(){
  const input = document.getElementById("batch-file");
  if(!input.files || !input.files[0]){ toast("JSON file select করুন", "error"); return; }
  const {start,count} = getBatchRange();
  if(batchJsonTotal && start > batchJsonTotal){ toast("Start account JSON range-এর বাইরে", "error"); return; }
  const fd = new FormData();
  fd.append("file", input.files[0]); fd.append("start", String(start)); fd.append("count", String(count));
  try{
    const r = await fetch("/api/account/import", {method:"POST", body:fd});
    const d = await r.json();
    if(d.status === "ok"){
      window.lastImportState = d;
      toast(d.message + " — next start: " + (d.next_start || "done"), "success");
      if(d.next_start) document.getElementById("batch-start").value = d.next_start;
      updateBatchPreview(); fetchStats();
    }else toast(d.error || "Batch import failed", "error");
  }catch(e){ toast("কানেকশন/ব্যাকএন্ড সমস্যা", "error"); }
}

async function deleteAllAccounts(){
  if(!confirm("সব active account, worker এবং accounts.json থেকে সব account মুছে ফেলবেন? এই কাজ undo করা যাবে না.")) return;
  try{
    const d = await post("/api/account/delete-all", {});
    if(d.status === "ok"){
      window.lastImportState = {};
      toast("All accounts deleted: " + d.removed, "success");
      fetchStats();
    }else toast(d.error || "Delete All failed", "error");
  }catch(e){ toast("কানেকশন/ব্যাকএন্ড সমস্যা", "error"); }
}

async function deleteAccount(uid, authUid = ""){
  if(!confirm(t("Hapus node {0}? Tindakan ini tidak bisa dibatalkan.", uid))) return;
  try{
    const d = await post("/api/account/delete", {uid, auth_uid: authUid});
    if(d.status === "ok"){ toast(t("Node {0} dihapus", uid), "success"); const c = document.getElementById("acc-" + uid); if(c) c.remove(); fetchStats(); }
    else toast(d.error || "Gagal menghapus", "error");
  }catch(e){ toast("Koneksi ke backend gagal", "error"); }
}
async function switchMode(uid, mode){
  try{
    const d = await post("/api/account/mode", {uid, mode});
    if(d.status === "ok"){
      toast(t("{0} mode → {1}", uid, d.mode === "BR" ? "Battle Royale" : "Lone Wolf"), "success");
      fetchStats();
    }else{
      toast(d.error || "Mode change failed", "error");
    }
  }catch(e){ toast("Mode switch failed", "error"); }
}
async function refreshAcc(uid){
  try{ toast(t("Sinkronisasi {0}...", uid)); await post("/api/account/refresh", {uid}); setTimeout(fetchStats, 800); }
  catch(e){ toast("Sinkronisasi gagal", "error"); }
}
async function restartAcc(uid){
  try{ toast(t("Restart proses {0}...", uid)); await post("/api/account/restart", {uid}); setTimeout(fetchStats, 800); }
  catch(e){ toast("Restart gagal", "error"); }
}
async function togglePause(uid){
  try{
    const d = await post("/api/account/pause", {uid});
    if(d.status === "ok"){ toast(t(d.is_paused ? "{0} dijeda" : "{0} dilanjutkan", uid), d.is_paused ? "info" : "success"); fetchStats(); }
    else toast(d.error || "Aksi gagal", "error");
  }catch(e){ toast("Koneksi ke backend gagal", "error"); }
}
async function togglePauseAll(){
  try{
    const d = await post("/api/account/pause_all");
    if(d.status === "ok"){ toast(d.all_paused ? "Semua node dijeda" : "Semua node berjalan", d.all_paused ? "info" : "success"); fetchStats(); }
    else toast(d.error || "Gagal", "error");
  }catch(e){ toast("Koneksi ke backend gagal", "error"); }
}

/* ---------- Nodes ---------- */
function setFilter(f, btn){
  activeFilter = f;
  document.querySelectorAll("#node-filters button").forEach(x => x.classList.remove("active"));
  if(btn) btn.classList.add("active");
  filterAccounts();
}
function filterAccounts(){
  const q = (document.getElementById("account-search").value || "").toLowerCase().trim();
  document.querySelectorAll(".node").forEach(card => {
    const uid = (card.dataset.uid || "").toLowerCase(), nick = (card.dataset.nick || "").toLowerCase();
    const st = (card.dataset.status || "").toLowerCase(), paused = card.dataset.paused === "1";
    let ok = !q || uid.includes(q) || nick.includes(q);
    if(activeFilter === "in_match") ok = ok && st.includes("match") && !paused;
    else if(activeFilter === "online") ok = ok && (st.includes("online") || st.includes("match")) && !paused;
    else if(activeFilter === "paused") ok = ok && paused;
    card.style.display = ok ? "" : "none";
  });
}
function renderAccounts(accounts){
  const container = document.getElementById("accounts-container");
  const allPaused = accounts.length > 0 && accounts.every(a => a.is_paused || a.status === "PAUSED");
  document.getElementById("btn-pause-all").innerHTML = allPaused
    ? '<i class="fa-solid fa-play"></i> ' + t("Resume All") : '<i class="fa-solid fa-pause"></i> ' + t("Pause All");

  if(accounts.length === 0){
    container.innerHTML = `<div class="empty"><i class="fa-solid fa-ghost"></i>${t("Belum ada node aktif.")}<br><button class="btn primary" onclick="openAddModal()">${t("Inject node pertama")}</button></div>`;
    return;
  }
  container.querySelectorAll(".empty").forEach(e => e.remove());
  const uids = new Set(accounts.map(a => String(a.uid)));
  container.querySelectorAll(".node").forEach(c => { if(!uids.has(c.dataset.uid)) c.remove(); });

  accounts.forEach(acc => {
    const uid = String(acc.uid);
    const level = Math.max(1, parseInt(acc.level) || 1), nextLvl = Math.min(100, level + 1);
    const baseExp = EXP_TABLE[level] ?? 0, targetExp = EXP_TABLE[nextLvl] ?? baseExp + 50000;
    const needed = Math.max(1, targetExp - baseExp), curExp = Number(acc.current_exp || 0);
    const earned = Math.max(0, curExp - baseExp), remaining = Math.max(0, targetExp - curExp);
    const pct = level >= 100 ? 100 : Math.min(100, Math.max(0, earned / needed * 100));
    const paused = Boolean(acc.is_paused || acc.status === "PAUSED");
    const effectiveMode = level > 10 ? "LONE_WOLF" : (String(acc.mode || "BR").toUpperCase() === "LONE_WOLF" ? "LONE_WOLF" : "BR");
    const autoLw = level > 10;
    const status = paused ? "PAUSED" : (acc.status || "ONLINE");

    let cls = "s-online", icon = "fa-globe";
    if(paused){ cls = "s-paused"; icon = "fa-pause"; }
    else if(status === "IN_MATCH"){ cls = "s-match"; icon = "fa-crosshairs"; }
    else if(status === "SEARCHING"){ cls = "s-error"; icon = "fa-magnifying-glass"; }
    else if(status !== "ONLINE"){ cls = "s-error"; icon = "fa-triangle-exclamation"; }
    const stText = paused ? t("PAUSED") : status === "IN_MATCH" ? `${t("IN MATCH")} (${acc.active_matches || 1})` : status === "ONLINE" ? t("ONLINE") : status === "SEARCHING" ? t("SEARCHING") : status;

    let card = document.getElementById("acc-" + uid);
    if(!card){ card = document.createElement("div"); card.id = "acc-" + uid; card.className = "node"; container.appendChild(card); }
    card.dataset.uid = uid; card.dataset.nick = acc.nickname || "";
    card.dataset.status = cls.replace("s-", ""); card.dataset.paused = paused ? "1" : "0";

    card.innerHTML = `
      <div class="node-head">
        <div class="who">
          <div class="avatar"><i class="fa-solid fa-user-astronaut"></i><span class="lvl">L${level}</span></div>
          <div style="min-width:0">
            <div class="name"><span>${esc(acc.nickname || "Unknown")}</span><span class="region">${esc(acc.region || "BD")}</span></div>
            <div class="uid">UID: ${esc(uid)} <i class="fa-regular fa-copy" onclick="copyUid('${escAttr(uid)}')" title="${t("Salin UID")}"></i></div>
          </div>
        </div>
         <div style="display:flex;flex-direction:column;align-items:flex-end;gap:5px">
           <div class="badge ${cls}"><i class="fa-solid ${icon}"></i> ${esc(stText)}</div>
           <div class="badge" style="background:rgba(99,102,241,.12);color:var(--violet);border-color:rgba(99,102,241,.25)">
             <i class="fa-solid fa-gamepad"></i> ${esc(effectiveMode === "BR" ? "BR · DEFAULT" : (autoLw ? "LONE WOLF · AUTO" : "LONE WOLF"))}
           </div>
         </div>
      </div>
      <div class="metrics">
        <div class="metric"><span>${t("Base EXP")}</span><strong>${Number(acc.initial_exp || 0).toLocaleString()}</strong></div>
        <div class="metric"><span>${t("Current")}</span><strong>${curExp.toLocaleString()}</strong></div>
        <div class="metric gain"><span>${t("Harvested")}</span><strong>+${Number(acc.gained_exp || 0).toLocaleString()}</strong></div>
      </div>
      <div>
        <div class="prog-top"><span>LVL ${level} → LVL ${nextLvl}</span><span>${t("{0} EXP lagi", remaining.toLocaleString())}</span></div>
        <div class="track"><div class="fill" style="width:${pct.toFixed(1)}%"></div></div>
        <div class="prog-bot"><span>${earned.toLocaleString()} / ${needed.toLocaleString()}</span><span class="pct">${pct.toFixed(1)}%</span></div>
      </div>
      <div class="node-foot">
        <span class="time acc-time" data-uptime="${Math.floor(acc.uptime_seconds || 0)}" data-paused="${paused ? 1 : 0}"><i class="fa-solid fa-stopwatch"></i> ${fmtDur(acc.uptime_seconds || 0)}</span>
        <div class="acts">
          <button class="act" ${effectiveMode === "BR" ? "style=\"outline:1px solid var(--violet)\"" : ""} onclick="switchMode('${escAttr(uid)}','BR')" title="${t("Battle Royale")}"><i class="fa-solid fa-trophy"></i></button>
          <button class="act" ${level < 5 ? "disabled" : (effectiveMode === "LONE_WOLF" ? "style=\"outline:1px solid var(--violet)\"" : "")} onclick="switchMode('${escAttr(uid)}','LONE_WOLF')" title="${t(autoLw ? "Auto Lone Wolf: Level above 10" : (level < 5 ? "Lone Wolf locked until Level 5" : "Lone Wolf"))}"><i class="fa-solid fa-crosshairs"></i></button>
          <button class="act" onclick="togglePause('${escAttr(uid)}')" title="${t(paused ? "Resume" : "Pause")}"><i class="fa-solid ${paused ? "fa-play" : "fa-pause"}"></i></button>
          <button class="act" onclick="restartAcc('${escAttr(uid)}')" title="${t("Restart")}"><i class="fa-solid fa-rotate-right"></i></button>
          <button class="act" onclick="refreshAcc('${escAttr(uid)}')" title="${t("Sync")}"><i class="fa-solid fa-arrows-rotate"></i></button>
          <button class="act danger" onclick="deleteAccount('${escAttr(uid)}','${escAttr(acc.auth_uid || "")}')" title="${t("Hapus")}"><i class="fa-solid fa-trash"></i></button>
        </div>
      </div>`;
  });
  filterAccounts();
}

/* ---------- Terminal ---------- */
function setLogFilter(f, btn){
  activeLogFilter = f;
  document.querySelectorAll("#log-filters button").forEach(x => x.classList.remove("active"));
  if(btn) btn.classList.add("active");
  renderLogs(cachedLogs);
}
function renderLogs(logs){
  const stream = document.getElementById("console-stream");
  let list = logs || [];
  if(activeLogFilter === "match") list = list.filter(l => String(l.message || "").toLowerCase().includes("match"));
  else if(activeLogFilter === "success") list = list.filter(l => l.level === "success" || String(l.message || "").includes("EXP"));
  else if(activeLogFilter === "error") list = list.filter(l => l.level === "error" || l.level === "warning");
  stream.innerHTML = list.map(l => `<div class="log"><span class="log-ts">[${esc(l.time || "00:00:00")}]</span><span class="log-msg ${esc(l.level || "info")}">&gt; ${esc(l.message || "")}</span></div>`).join("");
  if(autoScroll) stream.scrollTop = stream.scrollHeight;
}
async function clearLogs(){
  try{ await fetch("/api/logs/clear", {method:"POST"}); cachedLogs = []; renderLogs([]); toast("Log server dibersihkan", "success"); }
  catch(e){ toast("Gagal menghapus log di backend", "error"); }
}
function styleAutoScroll(){
  const b = document.getElementById("btn-autoscroll");
  b.style.background = autoScroll ? "var(--grad-soft)" : ""; b.style.color = autoScroll ? "#fff" : "var(--dim)";
}
function toggleAutoScroll(){
  autoScroll = !autoScroll; styleAutoScroll();
  if(autoScroll) document.getElementById("console-stream").scrollTop = 999999;
}
function handleLogScroll(){
  const s = document.getElementById("console-stream");
  if(autoScroll && s.scrollHeight - s.scrollTop - s.clientHeight > 80){ autoScroll = false; styleAutoScroll(); }
}

/* ---------- Stats ---------- */
let lastOn = true;
function setStatus(on){
  lastOn = on;
  document.getElementById("side-status").innerText = t(on ? "ONLINE" : "OFFLINE");
  const s2 = document.getElementById("side-status-2");
  s2.innerText = t(on ? "ONLINE" : "OFFLINE"); s2.style.color = on ? "var(--ok)" : "var(--err)";
  document.getElementById("pill").classList.toggle("off", !on);
  setText("p-status", t(on ? "Online" : "Offline"));
}
async function fetchStats(){
  try{
    const r = await fetch("/api/stats");
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    const accs = Array.isArray(d.accounts) ? d.accounts : [], logs = Array.isArray(d.logs) ? d.logs : [];
    setText("stat-accounts", d.total_accounts ?? accs.length);
    setText("stat-started", d.total_matches_started || 0);
    setText("stat-exp", "+" + Number(d.total_gained_exp || 0).toLocaleString());
    setText("stat-active-matches", t("{0} Aktif", d.total_active_matches || 0));
    setText("stat-online", t("{0} Node terhubung", accs.filter(a => a.status === "ONLINE" || a.status === "IN_MATCH").length));
    const uptimeH = Math.max(0.016, (d.uptime || 60) / 3600);
    setText("stat-per-hour", t("~{0} / jam", Math.round((d.total_matches_started || 0) / uptimeH)));
    setText("stat-exp-rate", t("~{0} EXP/jam", Number(d.exp_per_hour || 0).toLocaleString()));
    setText("p-nodes", d.total_accounts ?? accs.length);
    setText("p-matches", d.total_matches_started || 0);
    setText("p-exp", "+" + Number(d.total_gained_exp || 0).toLocaleString());
    setText("p-rate", Number(d.exp_per_hour || 0).toLocaleString());
    window.lastImportState = d.import_state || window.lastImportState || {};
    cachedLogs = logs;
    renderAccounts(accs); renderLogs(logs); setStatus(true);
  }catch(e){ console.warn("Backend Sync Error:", e); setStatus(false); }
}

/* ---------- Utils ---------- */
function copyText(txt, label){
  const ok = () => toast(t("{0} disalin: {1}", label, txt), "success");
  if(navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(ok, () => toast(label + ": " + txt));
  else toast(label + ": " + txt);
}
function copyUid(uid){ copyText(uid, "UID"); }
const COUNT=new Set(["stat-accounts","stat-started","stat-exp","p-nodes","p-matches","p-exp","p-rate"]), tw={};
function setText(id, v){
  const el = document.getElementById(id); if(!el) return;
  const str = String(v ?? ""), m = COUNT.has(id) && str.match(/^(\+?)([\d,]+)$/);
  if(!m){ el.innerText = str; return; }
  const to = parseInt(m[2].replace(/,/g,"")), from = parseFloat(el.dataset.n || 0);
  if(from === to){ el.innerText = str; return; }
  el.dataset.n = to; const t0 = performance.now(); cancelAnimationFrame(tw[id]);
  const step = t => { const k = Math.min(1,(t-t0)/800), e = 1-Math.pow(1-k,3);
    el.innerText = m[1] + Math.round(from+(to-from)*e).toLocaleString();
    if(k<1) tw[id] = requestAnimationFrame(step); else el.innerText = str; };
  tw[id] = requestAnimationFrame(step);
}
document.addEventListener("pointermove", e => {
  const c = e.target.closest && e.target.closest(".stat,.node,.hero,.info"); if(!c) return;
  const r = c.getBoundingClientRect();
  c.style.setProperty("--mx",(e.clientX-r.left)+"px"); c.style.setProperty("--my",(e.clientY-r.top)+"px");
});
function esc(s){ return s == null ? "" : String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#039;"); }
function escAttr(s){ return esc(s); }
function fmtDur(sec){
  sec = Math.max(0, Math.floor(Number(sec) || 0));
  const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60;
  return h > 0 ? `${h}h ${String(m).padStart(2,"0")}m` : `${String(m).padStart(2,"0")}m ${String(s).padStart(2,"0")}s`;
}

setInterval(() => {
  const el = Math.floor((Date.now() - clientStart) / 1000), p = n => String(n).padStart(2, "0");
  const up = `${p(Math.floor(el / 3600))}:${p(Math.floor((el % 3600) / 60))}:${p(el % 60)}`;
  setText("stat-uptime", up); setText("p-uptime", up);
  document.querySelectorAll(".acc-time").forEach(u => {
    if(u.dataset.paused === "1") return;
    const v = parseInt(u.dataset.uptime || "0") + 1;
    u.dataset.uptime = v;
    u.innerHTML = `<i class="fa-solid fa-stopwatch"></i> ${fmtDur(v)}`;
  });
}, 1000);

styleAutoScroll();
let saved = "id"; try{ saved = localStorage.getItem("lang") || "id"; }catch(e){}
applyLang(saved, false);
fetchStats();
setInterval(fetchStats, 5000);
</script>
</body>
</html>'''


def write_embedded_index_html():
    """Write the embedded dashboard HTML to index.html (next to this script
    and in the working directory) so the web dashboard serves this version."""
    targets = {
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"),
        os.path.join(os.getcwd(), "index.html"),
    }
    for path in targets:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(INDEX_HTML)
        except Exception as e:
            print(f"[WARN] Could not write {path}: {e}")


# ==================== CONFIGURATION ====================
WEB_HOST = "0.0.0.0"
WEB_PORT = int(os.environ.get("PORT", "20333"))
ACCOUNTS_FILE = "accounts.json"
TOKEN_CACHE_FILE = "token_cache.json"
DEVICES_FILE = "devices.json"
TOKEN_CACHE_TTL = 21600  # 6h local cache; server-side rejection still forces re-login

# 🔥 Match control
START_MATCH_INTERVAL = 3.0
NEW_MATCH_DELAY = 3.0
# Lone Wolf uses a shorter search/requeue cycle.
LW_START_MATCH_INTERVAL = 1.5
LW_NEW_MATCH_DELAY = 1.0
MAX_MATCH_DURATION = 800
MATCH_IDLE_TIMEOUT = 20.0
MAX_CONCURRENT_MATCHES = 1
UDP_RECV_TIMEOUT = 0.35
UDP_TRANSIENT_ERROR_BACKOFF = 0.10

# 🔥 Cache invalidation thresholds
MAX_CONSECUTIVE_PARSE_FAILURES = 5.0
NON_MATCH_RECONNECT_DELAY = 1.0

FALLBACK_UID = ""
FALLBACK_PASSWORD = ""

# Runtime stability controls: keep the existing login protocol unchanged,
# but prevent burst-login and long-running match-task buildup.
LOGIN_CONCURRENCY = 3
LOGIN_VERSION_CACHE_TTL = 21600.0  # keep a good config for 6h
VERSION_CONFIG_CACHE_FILE = "version_config_cache.json"
PLAYSTORE_VERSION_CACHE_FILE = "playstore_version_cache.json"
VERSION_CONFIG_RETRIES = 3
VERSION_CONFIG_RETRY_BASE = 1.5
VERSION_CONFIG_DISK_MAX_AGE = 86400.0
PLAYSTORE_VERSION_CACHE_TTL = 21600.0
_LOGIN_SEMAPHORE = asyncio.Semaphore(LOGIN_CONCURRENCY)
_VERSION_CONFIG_CACHE = None
_VERSION_CONFIG_CACHE_AT = 0.0
_VERSION_CONFIG_LOCK = asyncio.Lock()
_REFRESH_SEMAPHORE = asyncio.Semaphore(3)
_REFRESH_LOCKS: Dict[str, asyncio.Lock] = {}

def _get_refresh_lock(uid: str) -> asyncio.Lock:
    uid = str(uid)
    lock = _REFRESH_LOCKS.get(uid)
    if lock is None:
        lock = asyncio.Lock()
        _REFRESH_LOCKS[uid] = lock
    return lock


# ==================== ULTRA SAFE PERSISTENT DEVICE RANDOMIZER ====================
def get_device_for_account(account_identifier: str) -> dict:
    devices = {}
    if os.path.exists(DEVICES_FILE):
        try:
            with open(DEVICES_FILE, "r", encoding="utf-8") as f:
                devices = json.load(f)
        except Exception:
            pass

    acc_key = str(account_identifier)

    if acc_key in devices:
        return devices[acc_key]

    device_list = [
        ("Samsung", "SM-G998B", "Adreno (TM) 660", "Android OS 12 / API-31"),
        ("Xiaomi", "2201122G", "Adreno (TM) 730", "Android OS 13 / API-33"),
        ("Realme", "RMX3700", "Mali-G710", "Android OS 14 / API-34"),
        ("OnePlus", "CPH2451", "Adreno (TM) 740", "Android OS 13 / API-33"),
        ("OPPO", "CPH2611", "Adreno (TM) 720", "Android OS 14 / API-34"),
        ("Vivo", "V2203", "Mali-G710", "Android OS 12 / API-31"),
        ("Poco", "M2102J20SG", "Adreno (TM) 660", "Android OS 13 / API-33"),
    ]
    brand, model, gpu, os_ver = random.choice(device_list)

    new_device = {
        "unique_device_id": f"Google|{str(uuid.uuid4())}",
        "brand": brand,
        "model": model,
        "gpu_renderer": gpu,
        "system_software": os_ver,
        "screen_width": random.choice([1080, 1440, 720, 1280]),
        "screen_height": random.choice([2400, 3200, 1600, 2400]),
        "screen_dpi": str(random.randint(300, 420)),
        "memory": random.randint(2800, 6500),
        "processor_details": f"ARM64 FP ASIMD AES VMH | {random.randint(2200, 3200)} | {random.randint(6, 12)}",
        "client_ip": f"{random.randint(103, 223)}.{random.randint(10, 250)}.{random.randint(10, 250)}.{random.randint(10, 250)}",
        "android_id": secrets.token_hex(8),
        "gsf_id": secrets.token_hex(8),
        "build_fingerprint": f"{brand.lower()}/{model.lower()}/{model.lower()}:{os_ver.split(' / ')[0].replace(' ', '_')}/user/release-keys",
        "serial_number": secrets.token_hex(8),
        "hardware_id": secrets.token_hex(8),
    }

    devices[acc_key] = new_device

    try:
        with open(DEVICES_FILE, "w", encoding="utf-8") as f:
            json.dump(devices, f, indent=4)
    except Exception as e:
        print_error(f"Failed to save device mapping: {e}")

    return new_device


# ==================== CLOUDFLARE DNS RESOLVER ====================
CLOUDFLARE_PRIMARY_DNS = "1.1.1.1"
CLOUDFLARE_SECONDARY_DNS = "1.0.0.1"
_DNS_CACHE: Dict[str, Tuple[str, float]] = {}
_DNS_CACHE_TTL = 300.0

async def resolve_host_cloudflare(hostname: str) -> str:
    if not hostname:
        return hostname

    parts = hostname.split('.')
    if len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
        return hostname

    now = time.time()
    if hostname in _DNS_CACHE:
        ip, exp = _DNS_CACHE[hostname]
        if now < exp:
            return ip

    def _query_cloudflare(server_ip: str) -> Optional[str]:
        s = None
        try:
            tx_id = random.randint(1000, 65535)
            header = struct.pack(">HHHHHH", tx_id, 0x0100, 1, 0, 0, 0)
            qname = b"".join(bytes([len(part)]) + part.encode('ascii') for part in hostname.split('.')) + b"\x00"
            query_pkt = header + qname + struct.pack(">HH", 1, 1)

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1.2)
            s.sendto(query_pkt, (server_ip, 53))
            resp, _ = s.recvfrom(1024)

            if len(resp) >= 12:
                ancount = struct.unpack(">H", resp[6:8])[0]
                if ancount > 0:
                    offset = 12 + len(qname) + 4
                    for _ in range(ancount):
                        if offset >= len(resp):
                            break
                        if (resp[offset] & 0xC0) == 0xC0:
                            offset += 2
                        else:
                            while offset < len(resp) and resp[offset] != 0:
                                offset += 1 + resp[offset]
                            offset += 1
                        if offset + 10 > len(resp):
                            break
                        rtype, rclass, ttl, rdlen = struct.unpack(">HHIH", resp[offset:offset+10])
                        offset += 10
                        if rtype == 1 and rdlen == 4 and offset + 4 <= len(resp):
                            return socket.inet_ntoa(resp[offset:offset+4])
                        offset += rdlen
        except Exception:
            pass
        finally:
            if s:
                try:
                    s.close()
                except Exception:
                    pass
        return None

    loop = asyncio.get_running_loop()
    ip = await loop.run_in_executor(None, _query_cloudflare, CLOUDFLARE_PRIMARY_DNS)
    if not ip:
        ip = await loop.run_in_executor(None, _query_cloudflare, CLOUDFLARE_SECONDARY_DNS)
    if not ip:
        try:
            ip_info = await loop.getaddrinfo(hostname, None, family=socket.AF_INET)
            if ip_info:
                ip = ip_info[0][4][0]
        except Exception:
            ip = hostname

    if ip:
        _DNS_CACHE[hostname] = (ip, now + _DNS_CACHE_TTL)
    return ip or hostname


def optimize_tcp_socket(sock: socket.socket):
    try:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
    except Exception:
        pass


def optimize_udp_socket(sock: socket.socket):
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 131072)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 131072)
        if hasattr(socket, 'SIO_UDP_CONNRESET') and os.name == 'nt':
            try:
                sock.ioctl(socket.SIO_UDP_CONNRESET, False)
            except Exception:
                pass
    except Exception:
        pass


# ==================== NETWORK & CRYPTO ====================
client = httpx.AsyncClient(
    verify=False,
    timeout=10.0,
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=50)
)

headers = {
    'User-Agent': 'UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Expect': '100-continue',
    'X-Unity-Version': '2018.4.12f1',
    'X-GA-SV': '1789535859',
    'X-GA': 'v1 1',
    'ReleaseVersion': 'OB55'
}

AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'

CRC7_TABLE = bytes([
    0, 9, 18, 27, 36, 45, 54, 63, 72, 65, 90, 83, 108, 101, 126, 119,
    25, 16, 11, 2, 61, 52, 47, 38, 81, 88, 67, 74, 117, 124, 103, 110,
    50, 59, 32, 41, 22, 31, 4, 13, 122, 115, 104, 97, 94, 87, 76, 69,
    43, 34, 57, 48, 15, 6, 29, 20, 99, 106, 113, 120, 71, 78, 85, 92,
    100, 109, 118, 127, 64, 73, 82, 91, 44, 37, 62, 55, 8, 1, 26, 19,
    125, 116, 111, 102, 89, 80, 75, 66, 53, 60, 39, 46, 17, 24, 3, 10,
    86, 95, 68, 77, 114, 123, 96, 105, 30, 23, 12, 5, 58, 51, 40, 33,
    79, 70, 93, 84, 107, 98, 121, 112, 7, 14, 21, 28, 35, 42, 49, 56,
    65, 72, 83, 90, 101, 108, 119, 126, 9, 0, 27, 18, 45, 36, 63, 54,
    88, 81, 74, 67, 124, 117, 110, 103, 16, 25, 2, 11, 52, 61, 38, 47,
    115, 122, 97, 104, 87, 94, 69, 76, 59, 50, 41, 32, 31, 22, 13, 4,
    106, 99, 120, 113, 78, 71, 92, 85, 34, 43, 48, 57, 6, 15, 20, 29,
    37, 44, 55, 62, 1, 8, 19, 26, 109, 100, 127, 118, 73, 64, 91, 82,
    60, 53, 46, 39, 24, 17, 10, 3, 116, 125, 102, 111, 80, 89, 66, 75,
    23, 30, 5, 12, 51, 58, 33, 40, 95, 86, 77, 68, 123, 114, 105, 96,
    14, 7, 28, 21, 42, 35, 56, 49, 70, 79, 84, 93, 98, 107, 112, 121,
])

_DELTA = 0x9E3779B9
_ROUNDS = 16
_FIELD_SIZES = {0: 1, 1: 2, 2: 2, 3: 1, 4: 2}
_FIELD_NAMES = {0: "sendOption", 1: "cmd", 2: "orderId", 3: "flags", 4: "length"}


class Colors:
    HEADER = '\033[95m'
    GREEN = '\033[92m'
    FAIL = '\033[91m'
    WARNING = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'

def print_colored(text, color=Colors.WHITE):
    try:
        print(f"{color}{text}{Colors.ENDC}")
    except Exception:
        try:
            print(f"{color}{text.encode('ascii', errors='replace').decode('ascii')}{Colors.ENDC}")
        except Exception:
            pass

def print_success(text):
    print_colored(f"[+] {text}", Colors.GREEN)
    try:
        bot_state.log(text, "success")
    except Exception:
        pass

def print_error(text):
    print_colored(f"[-] {text}", Colors.FAIL)
    try:
        bot_state.log(text, "error")
    except Exception:
        pass

def print_warning(text):
    print_colored(f"[!] {text}", Colors.WARNING)
    try:
        bot_state.log(text, "warning")
    except Exception:
        pass

def print_info(text):
    print_colored(f"[i] {text}", Colors.CYAN)
    try:
        bot_state.log(text, "info")
    except Exception:
        pass

def get_proto_field(d, key, default=None):
    if not d or not isinstance(d, dict):
        return default
    if key in d:
        val = d[key].get('data')
        return val if val is not None else default
    if str(key) in d:
        val = d[str(key)].get('data')
        return val if val is not None else default
    return default


# ==================== PER-ACCOUNT MATCH COUNTER ====================
_match_counters: Dict[str, int] = {}
_match_counter_lock = asyncio.Lock()

async def _inc_match(uid: str) -> int:
    async with _match_counter_lock:
        _match_counters[uid] = _match_counters.get(uid, 0) + 1
        return _match_counters[uid]

async def _dec_match(uid: str) -> int:
    async with _match_counter_lock:
        if uid in _match_counters and _match_counters[uid] > 0:
            _match_counters[uid] -= 1
        return _match_counters.get(uid, 0)

async def _get_match_count(uid: str) -> int:
    async with _match_counter_lock:
        return _match_counters.get(uid, 0)

async def _get_total_match_count() -> int:
    async with _match_counter_lock:
        return sum(_match_counters.values())


# ==================== TOKEN CACHE ====================
_token_cache_memo: Dict[str, Any] = {}
_token_cache_memo_time: float = 0.0
_TOKEN_CACHE_MEMO_TTL = 5.0

def _json_serializer(obj):
    if isinstance(obj, (bytes, bytearray)):
        return {"__bytes_hex__": bytes(obj).hex()}
    raise TypeError(f"Type {type(obj)} not serializable")

def _json_deserializer(obj):
    if isinstance(obj, dict):
        if "__bytes_hex__" in obj and len(obj) == 1:
            try:
                return bytes.fromhex(obj["__bytes_hex__"])
            except Exception:
                return b""
        return {k: _json_deserializer(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_deserializer(x) for x in obj]
    return obj

def _load_token_cache() -> Dict[str, Any]:
    global _token_cache_memo, _token_cache_memo_time
    now = time.time()
    if _token_cache_memo and (now - _token_cache_memo_time) < _TOKEN_CACHE_MEMO_TTL:
        return _token_cache_memo

    if not os.path.exists(TOKEN_CACHE_FILE):
        return {}
    try:
        with open(TOKEN_CACHE_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            return {}
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError("Cache root must be dict")
        parsed = _json_deserializer(data)
        _token_cache_memo = parsed
        _token_cache_memo_time = now
        return parsed
    except Exception as e:
        print_error(f"Token cache corrupt → deleting: {e}")
        try:
            os.remove(TOKEN_CACHE_FILE)
        except Exception:
            pass
        return {}

def _save_token_cache(cache: Dict[str, Any]):
    global _token_cache_memo, _token_cache_memo_time
    try:
        tmp_file = TOKEN_CACHE_FILE + ".tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, default=_json_serializer)
        os.replace(tmp_file, TOKEN_CACHE_FILE)
        _token_cache_memo = cache
        _token_cache_memo_time = time.time()
    except Exception as e:
        print_error(f"Token cache save error: {e}")

def cache_get(uid: str) -> Optional[Dict]:
    cache = _load_token_cache()
    entry = cache.get(str(uid))
    if not entry:
        return None
    if time.time() - entry.get("cached_at", 0) > TOKEN_CACHE_TTL:
        print_info(f"[CACHE] UID {uid} expired. Re-login needed.")
        cache_invalidate(uid)
        return None
    if str(entry.get("account_id", "")).isdigit():
        entry["account_id"] = int(entry["account_id"])
    if not isinstance(entry.get("login_payload_data"), (bytes, bytearray)):
        print_warning(f"[CACHE] UID {uid} missing payload → invalidating")
        cache_invalidate(uid)
        return None
    return entry

def cache_set(uid: str, account_data: Dict):
    cache = _load_token_cache()
    entry = dict(account_data)
    entry["cached_at"] = time.time()
    cache[str(uid)] = entry
    _save_token_cache(cache)
    print_success(f"[CACHE] Saved credentials for UID {uid}")

def cache_invalidate(uid: str):
    cache = _load_token_cache()
    if str(uid) in cache:
        del cache[str(uid)]
        _save_token_cache(cache)
        print_warning(f"[CACHE] Invalidated: {uid}")


# ==================== ENCRYPTION & PROTOBUF ====================

async def aes_encrypt(payload, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(payload, AES.block_size))

def _read_json_cache(path: str, max_age: float):
    try:
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        saved_at = float(obj.get("cached_at", 0))
        if saved_at <= 0 or (time.time() - saved_at) > max_age:
            return None
        return obj
    except Exception:
        return None


def _write_json_cache(path: str, obj: dict):
    try:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception as e:
        print_warning(f"[LOGIN] Could not save cache {path}: {e}")


async def get_playstore_version():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: play_scraper('com.dts.freefireth', lang='hi', country='id')
    )
    return result.get("version")

async def version_config():
    global _VERSION_CONFIG_CACHE, _VERSION_CONFIG_CACHE_AT
    now = time.monotonic()
    if _VERSION_CONFIG_CACHE and (now - _VERSION_CONFIG_CACHE_AT) < LOGIN_VERSION_CACHE_TTL:
        return _VERSION_CONFIG_CACHE

    async with _VERSION_CONFIG_LOCK:
        now = time.monotonic()
        if _VERSION_CONFIG_CACHE and (now - _VERSION_CONFIG_CACHE_AT) < LOGIN_VERSION_CACHE_TTL:
            return _VERSION_CONFIG_CACHE

        app_version = await get_playstore_version()
        api_url = (
            "https://version.ggwhitehawk.com/live/ver.php"
            f"?version={app_version}"
            "&lang=hi&device=android&channel=android"
            "&appstore=googleplay&region=ID"
            "&whitelist_version=1.3.0&whitelist_sp_version=1.0.0"
        )
        try:
            response = await client.get(api_url)
            response.raise_for_status()
            data = response.json()
            server_url = data.get("server_url")
            remote_version = data.get("remote_version")
            latest_release_version = data.get("latest_release_version")
            if not server_url or not remote_version or not latest_release_version:
                return None
            _VERSION_CONFIG_CACHE = (latest_release_version, remote_version, server_url)
            _VERSION_CONFIG_CACHE_AT = time.monotonic()
            return _VERSION_CONFIG_CACHE
        except Exception:
            return None

async def get_access_token(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    hdrs = {
        "Host": "100067.connect.garena.com",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; SM-G998B Build/SP1A.210812.016)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }
    for attempt in range(5):
        try:
            response = await client.post(url, headers=hdrs, data=data)
            if response.status_code == 200:
                response_data = response.json()
                open_id = response_data.get("open_id")
                access_token = response_data.get("access_token")
                platform = response_data.get("platform", 4)
                if open_id and access_token:
                    return open_id, access_token, platform
            if response.status_code == 429:
                await asyncio.sleep(1)
                continue
        except Exception:
            pass
        await asyncio.sleep(0.5)
    return None

async def parse_results(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {"wire_type": result.wire_type}
        if result.wire_type == "varint":
            field_data["data"] = result.data
        elif result.wire_type == "string":
            field_data["data"] = result.data
        elif result.wire_type == "bytes":
            field_data["data"] = result.data
        elif result.wire_type == "length_delimited":
            field_data["data"] = await parse_results(result.data.results)
        result_dict[result.field] = field_data
    return result_dict

async def decode_protobuf(data):
    parsed_results = Parser().parse(data)
    parsed_results_dict = await parse_results(parsed_results)
    return json.dumps(parsed_results_dict)


# ==================== MANUAL PROTOBUF WIRE FORMAT (USER VERSION) ====================

def encode_varint(n):
    if n < 0:
        return b''
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            b |= 0x80
        out.append(b)
        if not n:
            break
    return bytes(out)


def build_proto(fields):
    parts = []
    for k, v in fields.items():
        if isinstance(v, dict):
            nested = build_proto(v)
            parts.append(encode_varint((k << 3) | 2) + encode_varint(len(nested)) + nested)
        elif isinstance(v, int):
            parts.append(encode_varint((k << 3) | 0) + encode_varint(v))
        elif isinstance(v, (str, bytes)):
            ev = v.encode() if isinstance(v, str) else v
            parts.append(encode_varint((k << 3) | 2) + encode_varint(len(ev)) + ev)
    return b''.join(parts)


def encrypt_api(plain_hex):
    return AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(
        pad(bytes.fromhex(plain_hex), AES.block_size)
    ).hex()


def encrypt_api_bytes(plain_bytes):
    return AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(
        pad(plain_bytes, AES.block_size)
    )


# ==================== 🔥 build_majorlogin_payload ====================
async def build_majorlogin_payload(open_id, access_token, platform, client_version, device_info):
    try:
        payload_dict = {
            3:   str(datetime.now())[:-7],
            4:   "free fire",
            5:   "1",
            7:   str(client_version) if client_version else "1.132.8",
            8:   str(device_info.get(
                     "system_software",
                     "Android OS 15 / API-35 (AP3A.240905.015.A2/OS2.0.202.0.VGTIDXM)"
                 )),
            9:   "Handheld",
            10:  "Telkomsel",
            11:  "CarrierDataNetwork",
            12:  str(device_info.get("screen_width", 1639)),
            13:  str(device_info.get("screen_height", 720)),
            14:  str(device_info.get("screen_dpi", 320)),
            15:  str(device_info.get("processor_details", "ARM64 FP ASIMD AES | 2000 | 8")),
            16:  str(device_info.get("memory", 5653)),
            17:  str(device_info.get("gpu_renderer", "Mali-G52 MC2")),
            18:  "OpenGL ES 3.2 v1.r49p1-03bet0.19498e0ae1d5dac223383c39a2e58f04",
            19:  str(device_info.get("unique_device_id", f"Google|{uuid.uuid4()}")),
            20:  str(device_info.get("client_ip", "182.5.135.225")),
            21:  "en",
            22:  str(open_id),
            23:  str(platform),
            24:  "Handheld",
            25:  str(device_info.get("model", "Xiaomi 2409BRN2CY")),
            26:  "ID",
            29:  str(access_token),
            30:  "1",
            41:  "Telkomsel",
            42:  "4G",
            57:  "7428b253defc164018c604a1ebbfebdf",
            60:  "109278",
            61:  "55402",
            62:  "868",
            64:  "55927",
            65:  "109278",
            66:  "55927",
            67:  "109278",
            73:  "2",
            74:  "/data/app/~~6Cw028g_ld-8Z0z2qhrOLA==/com.dts.freefireth-i3wiaEmpx8CbiRVhUMx_ag==/lib/arm64",
            76:  "1",
            77:  "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~6Cw028g_ld-8Z0z2qhrOLA==/com.dts.freefireth-i3wiaEmpx8CbiRVhUMx_ag==/base.apk",
            78:  "3",
            79:  "2",
            81:  "64",
            83:  "2019121229",
            85:  "3",
            86:  "OpenGLES2",
            87:  "8191",
            88:  str(platform),
            90:  "Cirebon",
            91:  "JB",
            92:  "14466",
            93:  "android",
            94:  "KqsHTyb7yHjsAiyNWUUZa0DSOD6U0AhDQ76smAo1WeHHHpSmJ8KMRyRrxb2ttgJqO9YOqO/K6AORAvDMAX/qBS8+JahIkrM7kHfzlfULbgRAoZ9r",
            95:  "111207",
            96:  "{\"cur_rate\":[60,90,120],\"support_etc2\":false}",
            97:  "1",
            98:  "1",
            99:  str(platform),
            100: str(platform),
            102: "D]C\x15\x05T\x0eU3",
            103: "1",
            104: "52837",
            105: "1",
            106: "https://dl.gmc.freefiremobile.com/live/ABHotUpdates/|https://core-gmc.freefiremobile.com/live/ABHotUpdates/|211c933168f55902c7dfbfd8c4e2957d",
            107: "1.3fb8adbf45f44ce9",
        }

        raw_proto = build_proto(payload_dict)
        encrypted = encrypt_api_bytes(raw_proto)
        return encrypted

    except Exception as e:
        print_error(f"Error building MajorLogin payload: {e}")
        traceback.print_exc()
        return None


# ==================== 🔥 FIXED: send_majorlogin ====================
async def send_majorlogin(data, release_version, server_url):
    try:
        # 🛡️ Guard: payload must exist
        if not data:
            print_error("[MajorLogin] Empty payload — aborting request")
            return None

        # 🛡️ Guard: server_url must exist
        if not server_url:
            print_error("[MajorLogin] Missing server_url — aborting request")
            return None

        # 🔧 FIX: normalize base URL so we never get "...comMajorLogin"
        base = server_url.rstrip('/')
        url = f"{base}/MajorLogin"

        req_headers = headers.copy()
        req_headers["ReleaseVersion"] = release_version
        response = await client.post(url, headers=req_headers, data=data)

        if response.status_code != 200:
            print_error(f"[MajorLogin] HTTP {response.status_code} from {url}")
            return None

        response_content = response.content
        if len(response_content) < 40:
            print_error(f"[MajorLogin] Response too small ({len(response_content)} bytes)")
            return None

        res_proto = CguTeam_pb2.MajorLoginRes()
        try:
            res_proto.ParseFromString(response_content)
            if res_proto.region and res_proto.token:
                return res_proto
        except Exception:
            pass

        if len(response_content) > 64:
            try:
                res_proto = CguTeam_pb2.MajorLoginRes()
                res_proto.ParseFromString(response_content[64:])
                if res_proto.region and res_proto.token:
                    return res_proto
            except Exception:
                pass

        for offset in range(min(128, len(response_content))):
            try:
                candidate = CguTeam_pb2.MajorLoginRes()
                candidate.ParseFromString(response_content[offset:])
                if candidate.region and candidate.token:
                    return candidate
            except Exception:
                pass

        res_proto = CguTeam_pb2.MajorLoginRes()
        res_proto.ParseFromString(response_content)
        return res_proto
    except Exception as e:
        print_error(f"[MajorLogin] Exception: {e}")
        return None


# ==================== FIXED: send_getlogin ====================
async def send_getlogin(data, base_url, token, release_version):
    try:
        # 🛡️ Guard: payload must exist
        if not data:
            print_error("[GetLoginData] Empty payload — aborting request")
            return None

        # 🔧 FIX: normalize base URL (same style as MajorLogin)
        base = base_url.rstrip('/')
        url = f"{base}/GetLoginData"

        req_headers = headers.copy()
        req_headers["ReleaseVersion"] = release_version
        req_headers['Authorization'] = f"Bearer {token}"
        req_headers['Host'] = "clientbp.ppmainecoonghj.com"
        response = await client.post(url, headers=req_headers, data=data)

        if response.status_code != 200:
            print_error(f"[GetLoginData] HTTP {response.status_code} from {url}")
            return None

        response_content = response.content

        res_proto = CguTeam_pb2.GetLoginDataRes()
        parsed_successfully = False
        try:
            res_proto.ParseFromString(response_content)
            if res_proto.functional_addrs or res_proto.informational_addrs:
                parsed_successfully = True
        except Exception:
            pass

        if not parsed_successfully:
            for offset in range(min(128, len(response_content))):
                try:
                    candidate = CguTeam_pb2.GetLoginDataRes()
                    candidate.ParseFromString(response_content[offset:])
                    if candidate.functional_addrs or candidate.informational_addrs:
                        res_proto = candidate
                        break
                except Exception:
                    pass

        dict_res = {}
        try:
            parsed = Parser().parse(response_content.hex())
            dict_res = await parse_results(parsed)
        except Exception:
            pass

        return res_proto, dict_res
    except Exception as e:
        print_error(f"[GetLoginData] Exception: {e}")
        return None


async def build_tcp_startup_packet(account_id, token, server_time, key, iv, region="ID", typ='OnLine'):
    uid_hex = f"{int(account_id):016x}"
    timestamp_hex = f"{int(server_time):08x}"
    encode_token = token.encode()
    encrypted_packet = (await aes_encrypt(encode_token, key, iv)).hex()
    encrypted_packet_length = f"{len(encrypted_packet) // 2:08x}"
    reg = str(region).upper() if region else "ID"
    if typ == 'OnLine':
        prefix = '7119' if reg == 'ID' else ('7114' if reg == 'IND' else '7115')
        return f"{prefix}{uid_hex}{timestamp_hex}00000000{encrypted_packet_length}{encrypted_packet}"
    else:
        prefix = '9219' if reg == 'ID' else ('9214' if reg == 'IND' else '9215')
        return f"{prefix}{uid_hex}{timestamp_hex}{encrypted_packet_length}{encrypted_packet}"

async def send_keep_alive(region="ID"):
    try:
        reg = str(region).upper() if region else "ID"
        ka_hex = "0219" if reg == "ID" else ("0214" if reg == "IND" else "0215")
        return bytes.fromhex(ka_hex)
    except Exception:
        return bytes.fromhex("0219")


async def start_game_battle_royale(region, client_version, writer, key, iv):
    packet = bytes.fromhex("080112800a0a010110013a110a044944433110aa011a064555524f50453a100a044944433210311a064555524f504540014a0801090a0b1219202758016291090a8001303838463832424630324139363736373032303130313030303030303030303030303136303030313030313530303032323246393745454530463030303030303436373632353134303030303030303030303030303030303030303030303030303030303030303030303030303066663030303030303030636163666131366410241afb02735d5e571400024a775d45414d1a041b1c001f11010449715f4243481a001e1d071c1703004b1a4066785c524570735c51486775421b5c5a4c07504042685a63610816054e19025e75196001477c015165406370195f5547404e4550640103020f1304064863754268676c755f65576e40467e5f0a417a4701026d675d6e73670b1108495a4c6a0b78470b740065645e525a057258425f584a447d4e6759440c11044e7c596d7f4b625f7d04055a47505c4e1d6b5b4107447d7201057d7f0f14084e430457674f7e517d72015172415d027473577c4d615f79535256780911030f4d5e027a797f614165067806505d53777750475e75064257076500460817014e741e7e5078487e7a7c465e7669767153497064605a7376677773550d160148037e18675966787f4c42607a645f577e7b441b460776026b18685d0b110205490060020f70676175654674706671797f41067346677c4e06585e780f15074c57047b40517075415f6364027259674b5b0166407f7340600407770a22047a5d5c52300b3a0a167305067162727516134208312e3133302e3232480350015ae90403626253513635686e556f4e36416456324b796f566c636f477776484f624e56526c4d727073504b4f43654177616848494176795556497273743752737149734a7a786b3247525268377a2f637664626d504f6a73552f79626d38547a4c69586d2f474351696d494b53486833447955726f39515152756c34545350626d6d624b7949565937545671577059455372323646572f59624578507338514f706d317372785455736c30796a434144444d4f34616a654b615753366361496c554b4963797a494e396d52516f715277687939797257476d337a644345337a6a61436f492f5a585233656f65365a42647a64677654636b6b665733356e4d4c6a6a565072564b6433523172756174394e50514150724a5546627859696c4c5a3859707336654d5447666b6649793574666a526c314d4648706b51774c6373374439656378566c41636f374e664f6d2b30654756466c4434744478706771385533595973587645384842502f70666c767a737138316a32524f4d7857437556445442492f684735625462773166456e4249725162762b636144775147696f74554e316d4c4b77734379456f4766706746614251457645672b736a764c4c78704743334c304a5344532f74526169504354553344374e6249306547516651622f5a466f4c36455630775a324d6f583932414c572f5049752f56634663584e70596b356f7966326151416a536971486a2f363276354843644f525551303578754e6171795251625653704654303137655237675255636b4966366c6f447476342b514e4a4670766d74757077707774396a5a5974437a4b56743657726d6e36785837706658456251555434684f3758a201050803108703a201050804108103a20105080510c001a20105081d10cc01a2010408161078a20105080e10af01a201020815")
    proto = thunderFF_pb2.StartMatch()
    proto.ParseFromString(packet)
    if hasattr(proto.main, 'region_list') and len(proto.main.region_list) > 0:
        proto.main.region_list[0].region = region
        if len(proto.main.region_list) > 1:
            proto.main.region_list[1].region = region
    if hasattr(proto.main, 'client_version'):
        proto.main.client_version.remote_version = client_version
    packet = proto.SerializeToString()
    encrypted_packet = (await aes_encrypt(packet, key, iv)).hex()
    packet_length = len(encrypted_packet) // 2
    hex_length = hex(packet_length)[2:]
    hex_length = hex_length if len(hex_length) > 1 else "0" + hex_length
    reg = str(region).upper() if region else "BD"
    reg_prefix = "031900" if reg == "BD" else ("031400" if reg == "IND" else "031500")
    final_packet = reg_prefix + "0" * (6 - len(hex_length)) + hex_length + encrypted_packet
    writer.write(bytes.fromhex(final_packet))
    await writer.drain()
    print_info(f"[⚔] Battle Royale Match Search Packet Sent ({packet_length} bytes, prefix: {reg_prefix}) | Region: {reg}")

async def start_game_lone_wolf(region, client_version, writer, key, iv):
    packet = bytes.fromhex("080112800a0a010b102b3a110a044944433110aa011a064555524f50453a100a044944433210311a064555524f504540014a0801090a0b1219202758016291090a8001303838463832424630324139363736373032303130313030303030303030303030303136303030313030313530303032323246393745454530463030303030303436373632353134303030303030303030303030303030303030303030303030303030303030303030303030303066663030303030303030636163666131366410241afb02735d5e571400024a775d45414d1a041b1c001f11010449715f4243481a001e1d071c1703004b1a4066785c524570735c51486775421b5c5a4c07504042685a63610816054e19025e75196001477c015165406370195f5547404e4550640103020f1304064863754268676c755f65576e40467e5f0a417a4701026d675d6e73670b1108495a4c6a0b78470b740065645e525a057258425f584a447d4e6759440c11044e7c596d7f4b625f7d04055a47505c4e1d6b5b4107447d7201057d7f0f14084e430457674f7e517d72015172415d027473577c4d615f79535256780911030f4d5e027a797f614165067806505d53777750475e75064257076500460817014e741e7e5078487e7a7c465e7669767153497064605a7376677773550d160148037e18675966787f4c42607a645f577e7b441b460776026b18685d0b110205490060020f70676175654674706671797f41067346677c4e06585e780f15074c57047b40517075415f6364027259674b5b0166407f7340600407770a22047a5d5c52300b3a0a167305067162727516134208312e3133302e3232480350015ae90403626253513635686e556f4e36416456324b796f566c636f477776484f624e56526c4d727073504b4f43654177616848494176795556497273743752737149734a7a786b3247525268377a2f637664626d504f6a73552f79626d38547a4c69586d2f474351696d494b53486833447955726f39515152756c34545350626d6d624b7949565937545671577059455372323646572f59624578507338514f706d317372785455736c30796a434144444d4f34616a654b615753366361496c554b4963797a494e396d52516f715277687939797257476d337a644345337a6a61436f492f5a585233656f65365a42647a64677654636b6b665733356e4d4c6a6a565072564b6433523172756174394e50514150724a5546627859696c4c5a3859707336654d5447666b6649793574666a526c314d4648706b51774c6373374439656378566c41636f374e664f6d2b30654756466c4434744478706771385533595973587645384842502f70666c767a737138316a32524f4d7857437556445442492f684735625462773166456e4249725162762b636144775147696f74554e316d4c4b77734379456f4766706746614251457645672b736a764c4c78704743334c304a5344532f74526169504354553344374e6249306547516651622f5a466f4c36455630775a324d6f583932414c572f5049752f56634663584e70596b356f7966326151416a536971486a2f363276354843644f525551303578754e6171795251625653704654303137655237675255636b4966366c6f447476342b514e4a4670766d74757077707774396a5a5974437a4b56743657726d6e36785837706658456251555434684f3758a201050803108703a201050804108103a20105080510c001a20105081d10cc01a2010408161078a20105080e10af01a201020815")
    proto = CguTeam_pb2.StartMatch()
    proto.ParseFromString(packet)
    if hasattr(proto.main, 'region_list') and len(proto.main.region_list) > 0:
        proto.main.region_list[0].region = region
        if len(proto.main.region_list) > 1:
            proto.main.region_list[1].region = region
    if hasattr(proto.main, 'client_version'):
        proto.main.client_version.remote_version = client_version
    packet = proto.SerializeToString()
    encrypted_packet = (await aes_encrypt(packet, key, iv)).hex()
    packet_length = len(encrypted_packet) // 2
    hex_length = hex(packet_length)[2:]
    hex_length = hex_length if len(hex_length) > 1 else "0" + hex_length
    reg = str(region).upper() if region else "ID"
    reg_prefix = "031400"
    final_packet = reg_prefix + "0" * (6 - len(hex_length)) + hex_length + encrypted_packet
    writer.write(bytes.fromhex(final_packet))
    await writer.drain()
    print_info(f"[⚔] Lone Wolf Match Search Packet Sent ({packet_length} bytes, prefix: {reg_prefix}) | Region: {reg}")

async def has_ssan_zig(n):
    z = (n << 1) & 0xFFFFFFFFFFFFFFFF
    out = bytearray()
    while z >= 0x80:
        out.append((z & 0x7F) | 0x80)
        z >>= 7
    out.append(z)
    return bytes(out)

async def uleb_encode(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            b |= 0x80
        out.append(b)
        if not n:
            break
    return bytes(out)

async def tea_enc(v0, v1, k0, k1, k2, k3):
    s = 0
    for _ in range(_ROUNDS):
        s = (s + _DELTA) & 0xFFFFFFFF
        v0 = (v0 + (((((v1 << 4) & 0xFFFFFFFF) + k0) & 0xFFFFFFFF ^
                      ((v1 + s) & 0xFFFFFFFF) ^
                      (((v1 >> 5) + k1) & 0xFFFFFFFF)))) & 0xFFFFFFFF
        v1 = (v1 + (((((v0 << 4) & 0xFFFFFFFF) + k2) & 0xFFFFFFFF ^
                      ((v0 + s) & 0xFFFFFFFF) ^
                      (((v0 >> 5) + k3) & 0xFFFFFFFF)))) & 0xFFFFFFFF
    return v0, v1

async def tea_dec(v0, v1, k0, k1, k2, k3):
    s = (_DELTA * _ROUNDS) & 0xFFFFFFFF
    for _ in range(_ROUNDS):
        v1 = (v1 - (((((v0 << 4) & 0xFFFFFFFF) + k2) & 0xFFFFFFFF ^
                      ((v0 + s) & 0xFFFFFFFF) ^
                      (((v0 >> 5) + k3) & 0xFFFFFFFF)))) & 0xFFFFFFFF
        v0 = (v0 - (((((v1 << 4) & 0xFFFFFFFF) + k0) & 0xFFFFFFFF ^
                      ((v1 + s) & 0xFFFFFFFF) ^
                      (((v1 >> 5) + k1) & 0xFFFFFFFF)))) & 0xFFFFFFFF
        s = (s - _DELTA) & 0xFFFFFFFF
    return v0, v1

async def tea_cbc_encrypt(padded, key_bytes):
    k0, k1, k2, k3 = (struct.unpack_from("<I", key_bytes, o)[0] for o in (0, 4, 8, 12))
    out = bytearray(len(padded))
    prev_cipher = bytearray(8)
    prev_intermediate = bytearray(8)
    for i in range(0, len(padded), 8):
        xored = bytearray(8)
        for j in range(8):
            xored[j] = padded[i + j] ^ prev_cipher[j]
        e0, e1 = await tea_enc(
            struct.unpack_from("<I", xored, 0)[0],
            struct.unpack_from("<I", xored, 4)[0],
            k0, k1, k2, k3,
        )
        enc = bytearray(8)
        struct.pack_into("<I", enc, 0, e0)
        struct.pack_into("<I", enc, 4, e1)
        for j in range(8):
            out[i + j] = enc[j] ^ prev_intermediate[j]
        prev_cipher[:] = out[i:i + 8]
        prev_intermediate[:] = xored
    return bytes(out)

async def build_padded(content):
    pad_len = (8 - (len(content) + 10) % 8) % 8
    return bytes([pad_len, 0, 0]) + b"\x00" * pad_len + content + b"\x00" * 7

async def encode_header(layout, send_option, cmd, order_id, flags, length, k, v80):
    out = bytearray()
    for code in layout:
        value = {0: send_option, 1: cmd, 2: order_id, 3: flags, 4: length}[code]
        if _FIELD_SIZES[code] == 1:
            out.append((value & 0xFF) ^ k)
        else:
            v = ((value & 0xFFFF) ^ v80) & 0xFFFF
            out.append(v & 0xFF)
            out.append((v >> 8) & 0xFF)
    return bytes(out)

async def crc7_buff(crc, buf):
    c = crc & 0x7F
    for b in buf:
        c = CRC7_TABLE[((2 * (c & 0xFF)) ^ (b & 0xFF)) & 0xFF] & 0x7F
    return c & 0x7F

async def sv_frame(msg_key, layout, send_option, cmd, order_id, flags, content, key, encrypted=True):
    k = key[0]
    v80 = ((k << 8) | k) & 0xFFFF
    body = await tea_cbc_encrypt(await build_padded(content), key) if encrypted else content
    hdr = bytearray([msg_key, 0]) + await encode_header(layout, send_option, cmd, order_id, flags, len(body), k, v80)
    packet = bytearray(hdr + body)
    packet[1] = await crc7_buff(0, bytes(packet[2:])) & 0x7F
    return bytes(packet)

async def build_match_startup_packets(token, udp_key, match_code, account_id, block_val,
                                      server_ip="", region="ID", client_version="1.132.6",
                                      client_version_code="2019121229", access_token="", mode_id=43, map_id=11):
    token = token.strip()
    udp_key = bytes.fromhex(udp_key)
    match_code = [int(ch) for ch in str(match_code).strip()]

    thunder_jwt = token[:660] if len(token) > 660 else token
    sharma_jwt = token[660:] if len(token) > 660 else ""
    encoded_thunder_jwt = thunder_jwt.encode() if isinstance(thunder_jwt, str) else thunder_jwt
    encoded_sharma_jwt = sharma_jwt.encode() if isinstance(sharma_jwt, str) else sharma_jwt

    garena420 = await has_ssan_zig(len(encoded_thunder_jwt)) + encoded_thunder_jwt

    reg = str(region).upper() if region else "ID"
    csoversea_block = bytes.fromhex(
        "ca0163736f7665727365612e7374726f6e67686f6c642e66726565666972656d6f62696c652e636f6d"
        "3b302e302e302e303b33342e3132362e37362e34353b33342e38372e3137372e31343b33342e38372e"
        "3137302e3233303b33352e3138352e3138332e35370000000000000100000000000000000000000001"
        "00000800000100000000000100a8a2d7bebd8d8bdf110200"
    )

    mid = bytes.fromhex('0000000001000102030101') + await has_ssan_zig(len(reg)) + reg.encode()
    mid += bytes.fromhex('0001030003000004')
    mid += await has_ssan_zig(len(client_version)) + client_version.encode()
    mid += await has_ssan_zig(len(client_version_code)) + client_version_code.encode()
    mid += csoversea_block

    clean_ip = server_ip.split(':')[0] if server_ip else "0.0.0.0"
    mid += await has_ssan_zig(len(clean_ip)) + clean_ip.encode()

    clean_acc_tok = access_token.strip() if access_token else ""
    if clean_acc_tok:
        mid += await has_ssan_zig(len(clean_acc_tok)) + clean_acc_tok.encode()

    mid += await has_ssan_zig(len(encoded_sharma_jwt)) + encoded_sharma_jwt

    tg_garena420 = (
        await uleb_encode(int(account_id)) +
        await uleb_encode(int(block_val)) +
        await uleb_encode(1) +
        await uleb_encode(int(mode_id)) +
        await uleb_encode(int(block_val)) +
        await uleb_encode(int(map_id)) +
        mid
    )

    process = await sv_frame(0x5E, match_code, 2, 447, 0, 1, garena420, udp_key)
    loading = await sv_frame(0x5A, match_code, 2, 448, 1, 1, tg_garena420, udp_key)
    return process.hex(), loading.hex()

async def produce_xor_key(secret_key):
    k = secret_key[0] if secret_key and len(secret_key) > 0 else 10
    return k, ((k << 8) | k) & 0xFFFF

async def parse_layout(layout):
    if isinstance(layout, str):
        return [int(ch) for ch in layout.strip()]
    return list(layout)

async def tea_cbc_decrypt(body, key_bytes):
    k0, k1, k2, k3 = (struct.unpack_from("<I", key_bytes, o)[0] for o in (0, 4, 8, 12))
    out = bytearray(len(body))
    prev_intermediate = bytearray(8)
    prev_cipher = bytearray(8)
    xored = bytearray(8)
    dec = bytearray(8)
    for i in range(0, len(body), 8):
        for j in range(8):
            xored[j] = body[i + j] ^ prev_intermediate[j]
        d0, d1 = await tea_dec(
            struct.unpack_from("<I", xored, 0)[0],
            struct.unpack_from("<I", xored, 4)[0],
            k0, k1, k2, k3
        )
        struct.pack_into("<I", dec, 0, d0)
        struct.pack_into("<I", dec, 4, d1)
        for j in range(8):
            out[i + j] = dec[j] ^ prev_cipher[j]
        prev_cipher[:] = body[i:i + 8]
        prev_intermediate[:] = dec
    return bytes(out)

async def build_hello_packet(text, key, layout):
    data = text.encode("utf-8")
    if len(data) > 25:
        raise ValueError(f"Text is too long ({len(data)} bytes)")
    content = b"\x10\x00\x00\x00" + data + b"\x00" * (29 - 4 - len(data))
    k, v80 = await produce_xor_key(key)
    layout = await parse_layout(layout)
    padded = await build_padded(content)
    enc_body = await tea_cbc_encrypt(padded, key)
    header_bytes = await encode_header(layout, 1, 1, 0, 1, len(enc_body), k, v80)
    packet = bytearray([0x63, 0x00]) + header_bytes + enc_body
    packet[1] = await crc7_buff(0, packet[2:]) & 0x7F
    return bytes(packet).hex()

async def classify(frame):
    cmd = frame["cmd"]
    msg_name = MESSAGE_ID_TO_NAME.get(cmd, f"UNKNOWN_{cmd}")
    if msg_name == "UDP_HELLO":
        return "HELLO"
    if msg_name == "UDP_ACK":
        return "ACK"
    if msg_name == "UDP_PING":
        return "PING"
    if msg_name == "RUDP_JOIN_MATCH":
        return "JOIN_MATCH"
    if msg_name.startswith("RUDP_"):
        return msg_name
    if msg_name.startswith("UDP_"):
        return msg_name
    return "DATA"

async def build_packet(msg_key, layout, send_option, cmd, order_id, flags, content, key, encrypted=True):
    k = key[0]
    v80 = ((k << 8) | k) & 0xFFFF
    body = await tea_cbc_encrypt(await build_padded(content), key) if encrypted else content
    hdr = bytearray([msg_key, 0])
    for code in layout:
        value = {0: send_option, 1: cmd, 2: order_id, 3: flags, 4: len(body)}[code]
        if _FIELD_SIZES[code] == 1:
            hdr.append((value & 0xFF) ^ k)
        else:
            v = ((value & 0xFFFF) ^ v80) & 0xFFFF
            hdr.append(v & 0xFF)
            hdr.append((v >> 8) & 0xFF)
    packet = bytearray(hdr + body)
    packet[1] = await crc7_buff(0, bytes(packet[2:])) & 0x7F
    return bytes(packet)

async def layouts_from_mask(mask):
    ru = [int(c) for c in str(mask).strip()]
    nr = [c for c in ru if c != 2]
    return ru, nr

async def reply_for(frame, key, mask, ack_key=0x68, ping_key=0x6D, hello_key=0x5B, ack_style="short"):
    ru, nr = await layouts_from_mask(mask)
    typ = await classify(frame)
    if typ == "HELLO":
        if ack_style == "echo":
            content = frame["content"] if frame["content"] else b"\x10\x00\x00\x00"
            return typ, await build_packet(hello_key, nr, 1, 1, None, 1, content, key)
        return typ, await build_packet(ack_key, nr, 0, 2, None, 1, b"\x01\x00", key)
    if typ == "ACK":
        content = frame["content"] if frame["content"] else b"\x01\x00"
        return typ, await build_packet(ack_key, nr, 0, 2, None, 1, content, key)
    if typ == "PING":
        c = frame["content"]
        counter = c[:4] if len(c) >= 4 else c
        return typ, await build_packet(ping_key, nr, 0, 3, None, 0, counter + b"\x00\x00\x00", key, encrypted=False)
    if typ == "JOIN_MATCH":
        return typ, await build_packet(ack_key, nr, 0, 2, None, 1, b"\x02\x00", key)
    return typ, None

async def keepalive_ping(sock, ip, port, key_bytes, mask, stop_event):
    nr = (await layouts_from_mask(mask))[1]
    ping_keys = [0x66, 0x6D, 0x69, 0x6C, 0x6B, 0x6E, 0x6F, 0x70]
    loop = asyncio.get_event_loop()
    i = 0
    while not stop_event.is_set():
        pk = ping_keys[i % len(ping_keys)]
        counter = int(time.time() * 1000) & 0xFFFFFFFF
        pkt = await build_packet(pk, nr, 0, 3, None, 0, struct.pack("<I", counter) + b"\x00\x00\x00", key_bytes, encrypted=False)
        try:
            await loop.sock_sendto(sock, pkt, (ip, port))
        except Exception:
            pass
        i += 1
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass

async def try_header(buf, layout, k, v80):
    off = 2
    out = {}
    for code in layout:
        size = _FIELD_SIZES[code]
        if off + size > len(buf):
            return None
        out[_FIELD_NAMES[code]] = (buf[off] ^ k) if size == 1 else ((buf[off] | (buf[off + 1] << 8)) ^ v80) & 0xFFFF
        off += size
    out["headerLen"] = off
    return out

async def oicq_unpad(padded):
    if not padded or len(padded) < 8:
        return None
    if not all(padded[-1 - i] == 0 for i in range(7)):
        return None
    pad_len = padded[0] & 0x07
    s = 3 + pad_len
    e = len(padded) - 7
    return padded[s:e] if s < e else b""

async def decode_packet(packet, key, mask=None):
    data = bytes(packet) if isinstance(packet, bytes) else bytes.fromhex(packet)
    if len(data) < 8:
        return None
    k = key[0]
    v80 = ((k << 8) | k) & 0xFFFF
    crc_ok = (data[1] & 0x7F) == await crc7_buff(0, data[2:])
    candidates = []
    if mask:
        ru, nr = await layouts_from_mask(mask)
        layouts = [("RUDP", ru), ("nonRUDP", nr)]
    else:
        layouts = [("RUDP", list(p)) for p in itertools.permutations([0, 1, 2, 3, 4])]
        layouts += [("nonRUDP", list(p)) for p in itertools.permutations([0, 1, 3, 4])]
    for kind, layout in layouts:
        f = await try_header(data, layout, k, v80)
        if not f:
            continue
        if f["flags"] > 7 or f["sendOption"] > 7:
            continue
        if f["length"] != len(data) - f["headerLen"]:
            continue
        body = data[f["headerLen"]:f["headerLen"] + f["length"]]
        content = None
        padded = None
        if f["flags"] & 1:
            if len(body) < 8 or len(body) % 8 != 0:
                continue
            padded = await tea_cbc_decrypt(body, key)
            content = await oicq_unpad(padded)
            if content is None:
                continue
        else:
            content = body
        score = (1 if crc_ok else 0) + (1 if content is not None else 0)
        candidates.append({
            "kind": kind, "layout": layout, "headerLen": f["headerLen"],
            "msgKey": data[0], "cmd": f["cmd"], "flags": f["flags"],
            "sendOption": f["sendOption"], "orderId": f.get("orderId"),
            "length": f["length"], "content": content, "crcOk": crc_ok,
            "padded": padded, "score": score, "total": len(data),
        })
    if not candidates:
        return None
    candidates.sort(key=lambda c: (c["kind"] == "RUDP" or c["kind"] == "nonRUDP", c["score"]), reverse=True)
    return candidates[0]


# ============================================================
# play_game — UDP MATCH
# ============================================================
async def play_game(server_ip_port, thunder, sharma, udp_key, match_code,
                    account_id, player_region, client_version, key, iv,
                    match_index: int):
    match_start_time = time.time()
    ping_task = None
    sock = None
    ping_stop = asyncio.Event()
    uid_str = str(account_id)
    completed_cleanly = False

    try:
        ip, port = server_ip_port.split(":")
        port = int(port)
        resolved_ip = await resolve_host_cloudflare(ip)

        loop = asyncio.get_event_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        optimize_udp_socket(sock)
        sock.setblocking(False)

        udp_key_bytes = bytes.fromhex(udp_key)
        hello_packet = await build_hello_packet(f"{account_id}_2585", udp_key_bytes, match_code)
        await loop.sock_sendto(sock, bytes.fromhex(hello_packet), (resolved_ip, port))

        ack_state = "waiting_for_hello_reply"
        thunder_sent = False
        sharma_sent = False
        join_match_received = False
        local_closed = False
        send_lock = asyncio.Lock()
        packet_layout = (await layouts_from_mask(match_code))[1]

        ping_task = asyncio.create_task(
            keepalive_ping(sock, resolved_ip, port, udp_key_bytes, match_code, ping_stop)
        )
        last_activity = time.time()
        MAX_IDLE_BEFORE_HELLO_RESEND = 7.0

        print_colored(
            f"🎮 [MATCH #{match_index}] UDP started → {server_ip_port} (DNS: {resolved_ip})",
            Colors.MAGENTA
        )

        async def send_thunder_sharma_inline():
            nonlocal ack_state, thunder_sent, sharma_sent
            if thunder_sent:
                return
            async with send_lock:
                if thunder_sent:
                    return
                try:
                    await loop.sock_sendto(sock, bytes.fromhex(thunder), (resolved_ip, port))
                    thunder_sent = True
                    await asyncio.sleep(0.1)
                    prepare_ack = await build_packet(
                        0x68, packet_layout,
                        0, 2, None, 1, b"\x01\x00", udp_key_bytes
                    )
                    await loop.sock_sendto(sock, prepare_ack, (resolved_ip, port))
                    await asyncio.sleep(0.2)
                    await loop.sock_sendto(sock, bytes.fromhex(sharma), (resolved_ip, port))
                    sharma_sent = True
                    ack_state = "thunder_sharma_sent"
                    print_success(f"[MATCH #{match_index}] Thunder+Sharma sent!")
                except Exception as e:
                    print_error(f"[MATCH #{match_index}] send error: {e}")

        while not local_closed:
            if time.time() - match_start_time > MAX_MATCH_DURATION:
                break
            try:
                response, server_addr = await asyncio.wait_for(
                    loop.sock_recvfrom(sock, 65535), timeout=UDP_RECV_TIMEOUT
                )
                if response:
                    last_activity = time.time()
                    frame = await decode_packet(response, udp_key_bytes, match_code)
                    if frame:
                        ptype = await classify(frame)

                        if frame['cmd'] in [103, 107]:
                            print_success(
                                f"[MATCH #{match_index}] Completed (cmd {frame['cmd']})"
                            )
                            completed_cleanly = True
                            local_closed = True
                            continue

                        if frame['cmd'] == 101:
                            try:
                                ack_pkt = await build_packet(
                                    0x68, packet_layout,
                                    0, 2, None, 1, b"\x01\x00", udp_key_bytes
                                )
                                await loop.sock_sendto(sock, ack_pkt, server_addr)
                            except Exception:
                                pass
                            continue

                        if ptype in ["ACK", "PING", "HELLO", "JOIN_MATCH"]:
                            if ptype == "HELLO" and ack_state == "waiting_for_hello_reply":
                                typ, reply = await reply_for(
                                    frame, udp_key_bytes, match_code, ack_style="short"
                                )
                                if reply:
                                    await loop.sock_sendto(sock, reply, server_addr)
                                ack_state = "ack_sent_waiting"
                            elif ptype == "ACK":
                                if ack_state == "waiting_for_hello_reply":
                                    typ, reply = await reply_for(frame, udp_key_bytes, match_code)
                                    if reply:
                                        await loop.sock_sendto(sock, reply, server_addr)
                                    ack_state = "ready_to_send_thunder"
                                elif ack_state == "ack_sent_waiting":
                                    ack_state = "ready_to_send_thunder"
                                else:
                                    typ, reply = await reply_for(frame, udp_key_bytes, match_code)
                                    if reply:
                                        await loop.sock_sendto(sock, reply, server_addr)
                            elif ptype == "PING":
                                typ, reply = await reply_for(frame, udp_key_bytes, match_code)
                                if reply:
                                    await loop.sock_sendto(sock, reply, server_addr)
                            elif ptype == "JOIN_MATCH" and not join_match_received:
                                typ, reply = await reply_for(frame, udp_key_bytes, match_code)
                                if reply:
                                    await loop.sock_sendto(sock, reply, server_addr)
                                    join_match_received = True
            except asyncio.TimeoutError:
                if ack_state == "ready_to_send_thunder" and not thunder_sent:
                    await send_thunder_sharma_inline()
                elif ack_state == "waiting_for_hello_reply":
                    if (time.time() - last_activity) > MAX_IDLE_BEFORE_HELLO_RESEND:
                        try:
                            pkt = await build_hello_packet(
                                f"{account_id}_2585", udp_key_bytes, match_code
                            )
                            await loop.sock_sendto(sock, bytes.fromhex(pkt), (resolved_ip, port))
                        except Exception:
                            pass
                        last_activity = time.time()
                    if (time.time() - match_start_time) > 25.0:
                        print_warning(f"[MATCH #{match_index}] Handshake timeout")
                        break
                elif ack_state == "thunder_sharma_sent":
                    if (time.time() - last_activity) > MATCH_IDLE_TIMEOUT:
                        print_success(f"[MATCH #{match_index}] Finished naturally")
                        completed_cleanly = True
                        break
                continue
            except BlockingIOError:
                await asyncio.sleep(0.05)
            except OSError:
                await asyncio.sleep(UDP_TRANSIENT_ERROR_BACKOFF)
                continue
            except Exception:
                await asyncio.sleep(UDP_TRANSIENT_ERROR_BACKOFF)
                continue

            if ack_state == "ready_to_send_thunder" and not thunder_sent:
                await send_thunder_sharma_inline()

        return f"match #{match_index} finished"
    except Exception as e:
        print_error(f"[MATCH #{match_index}] error: {e}")
        return f"match #{match_index} error"
    finally:
        if completed_cleanly:
            try:
                bot_state.increment_match(uid_str)
            except Exception:
                pass
        ping_stop.set()
        if ping_task:
            ping_task.cancel()
            try:
                await ping_task
            except asyncio.CancelledError:
                pass
        if sock:
            try:
                sock.close()
            except Exception:
                pass
        remaining = await _dec_match(uid_str)
        total = await _get_total_match_count()
        print_info(
            f"[MATCH #{match_index}] Closed. "
            f"UID active: {remaining} | Total active: {total}"
        )
        try:
            bot_state.update_status(uid_str, "IN_MATCH" if remaining > 0 else "ONLINE", remaining)
        except Exception:
            pass


# ============================================================
# functional_lone_wolf — TCP + Match handler
# ============================================================
async def functional_lone_wolf(addrs, starter_packet, account_region, client_version,
                                key, iv, account_id="", account_data=None,
                                max_reconnects=10):
    reconnects = 0
    ip, port = addrs.split(":")
    play_matches: List[asyncio.Task] = []
    no_response_count = 0
    search_attempts = 0
    last_start_time = 0.0
    uid_str = str(account_id)

    consecutive_parse_failures = 0

    current_token = starter_packet
    current_key = key
    current_iv = iv
    current_account_data = account_data

    try:
        while True:
            writer = None
            try:
                if current_account_data:
                    fresh = None
                    if current_account_data.get('auth_type') == 'guest' and current_account_data.get('auth_uid'):
                        fresh = cache_get(str(current_account_data['auth_uid']))
                    elif current_account_data.get('auth_type') == 'token' and current_account_data.get('auth_token'):
                        fresh = cache_get(f"tok_{current_account_data['auth_token'][:20]}")

                    if fresh:
                        current_account_data = fresh
                        current_key = fresh['aes_ak']
                        current_iv = fresh['iv_i']
                        current_token = await build_tcp_startup_packet(
                            fresh['account_id'],
                            fresh['token'],
                            fresh['server_time'],
                            current_key,
                            current_iv,
                            region=fresh.get('region', account_region),
                            typ='OnLine'
                        )
                    else:
                        print_warning(f"[FUNCTIONAL] Cache miss for {uid_str} → re-login needed")
                        try:
                            if current_account_data.get('auth_uid'):
                                cache_invalidate(str(current_account_data['auth_uid']))
                            if current_account_data.get('auth_token'):
                                cache_invalidate(f"tok_{current_account_data['auth_token'][:20]}")
                        except Exception:
                            pass
                        raise ConnectionError("Cache expired, triggering fresh login")

                resolved_ip = await resolve_host_cloudflare(ip)
                reader, writer = await asyncio.open_connection(resolved_ip, int(port))

                raw_sock = writer.get_extra_info('socket')
                if raw_sock:
                    optimize_tcp_socket(raw_sock)

                writer.write(bytes.fromhex(current_token))
                await writer.drain()

                try:
                    init_ka = await send_keep_alive(account_region)
                    if init_ka and writer and not writer.is_closing():
                        writer.write(init_ka)
                        await asyncio.wait_for(writer.drain(), timeout=3)
                except Exception:
                    pass

                print_success(f"[FUNCTIONAL] TCP Gateway Connected for UID: {uid_str} (DNS: {resolved_ip})")
                reconnects = 0
                no_response_count = 0
                last_start_time = 0.0

                def get_effective_mode():
                    # BR is the default through Level 10. Above Level 10,
                    # automatically use Lone Wolf; below that, respect dashboard mode.
                    try:
                        level_now = int(bot_state.get_account_level(uid_str) or 0)
                    except (TypeError, ValueError):
                        level_now = 0
                    try:
                        dashboard_mode = str(bot_state.get_account_mode(uid_str) or "BR").upper().strip()
                    except Exception:
                        dashboard_mode = "BR"
                    if level_now > 10:
                        return "LW", level_now
                    if dashboard_mode in {"LW", "LONEWOLF", "LONE-WOLF", "LONE_WOLF"}:
                        return "LW", level_now
                    return "BR", level_now

                async def send_start_match():
                    nonlocal search_attempts, last_start_time
                    search_attempts += 1
                    selected_mode, level_now = get_effective_mode()
                    current_region = "BD" if selected_mode == "BR" else "ID"
                    mode_label = "BR" if selected_mode == "BR" else "LW"
                    print_info(
                        f"[{mode_label} MODE] Sending StartMatch #{search_attempts} "
                        f"region: {current_region} | Level: {level_now}"
                    )
                    try:
                        await asyncio.sleep(random.uniform(0.3, 0.6))
                        if selected_mode == "BR":
                            await start_game_battle_royale(
                                current_region, client_version, writer,
                                current_key, current_iv
                            )
                        else:
                            await start_game_lone_wolf(
                                current_region, client_version, writer,
                                current_key, current_iv
                            )
                        print_success(f"[{mode_label} MODE] StartMatch packet sent")
                        active = await _get_match_count(uid_str)
                        try:
                            bot_state.update_status(uid_str, f"SEARCHING ({mode_label})", active)
                        except Exception:
                            pass
                    except Exception as e:
                        print_error(f"StartMatch ({mode_label}) error: {e}")
                    last_start_time = asyncio.get_running_loop().time()

                await send_start_match()

                while True:
                    play_matches[:] = [m for m in play_matches if not m.done()]

                    active_count = await _get_match_count(uid_str)
                    try:
                        bot_state.update_status(
                            uid_str,
                            "ONLINE" if active_count == 0 else "IN_MATCH",
                            active_count
                        )
                    except Exception:
                        pass

                    now = asyncio.get_running_loop().time()
                    effective_mode, _ = get_effective_mode()
                    match_search_interval = (
                        LW_START_MATCH_INTERVAL if effective_mode == "LW"
                        else START_MATCH_INTERVAL
                    )
                    if now - last_start_time >= match_search_interval:
                        # Never let long-running UDP matches accumulate. The old
                        # loop could create a new background task every 3s even
                        # when previous matches were still alive.
                        if len(play_matches) < MAX_CONCURRENT_MATCHES:
                            await send_start_match()
                        else:
                            last_start_time = now
                            try:
                                bot_state.update_status(uid_str, "IN_MATCH", len(play_matches))
                            except Exception:
                                pass

                    try:
                        data = await asyncio.wait_for(reader.read(8192), timeout=1.0)
                    except asyncio.TimeoutError:
                        no_response_count += 1
                        if no_response_count > 90:
                            print_warning(f"[FUNCTIONAL] Gateway silent ({uid_str}). Reconnecting...")
                            raise ConnectionError("Gateway idle timeout")
                        continue

                    if not data:
                        raise ConnectionError("Connection closed by server")

                    hex_data = data.hex()
                    packet_length = len(data)
                    no_response_count = 0

                    if hex_data.startswith("0300") and 10 < packet_length < 30:
                        print_info("Match starting, please wait...")
                        continue

                    if hex_data.startswith("0300") and packet_length >= 300:
                        print_colored("=" * 60, Colors.GREEN)
                        print_colored(f"MATCH FOUND! Loading...", Colors.GREEN)
                        print_colored("=" * 60, Colors.GREEN)

                        try:
                            res = json.loads(await decode_protobuf(hex_data[10:]))
                            token = None
                            udp_key = None
                            match_code = None
                            server_ip_port = None
                            match_account_id = None
                            block_val = None

                            if '42' in res and 'data' in res['42']:
                                match_code = res['42']['data']
                            if '5' in res and 'data' in res['5']:
                                res_field5 = res['5']['data']
                                server_ip_port = res_field5.get('2', {}).get('data')
                                udp_key = res_field5.get('3', {}).get('data')
                                token = res_field5.get('4', {}).get('data')
                                if '42' in res_field5:
                                    match_code = res_field5['42']['data']
                            if '1' in res and 'data' in res['1']:
                                match_account_id = res['1']['data']
                            if '5' in res and 'data' in res['5']:
                                block_val = res['5']['data'].get('1', {}).get('data')

                            effective_acc_id = match_account_id or account_id or "BD_BOT"

                            if token and udp_key and match_code and server_ip_port:
                                acc_tok = ""
                                if current_account_data:
                                    acc_tok = current_account_data.get('access_token', '') or ""
                                match_mode, level_now = get_effective_mode()
                                mode_id, map_id = (1, 1) if match_mode == "BR" else (43, 11)
                                thunder, sharma = await build_match_startup_packets(
                                    token, udp_key, match_code, effective_acc_id, block_val or 0,
                                    server_ip=server_ip_port,
                                    region=account_region,
                                    client_version=client_version,
                                    access_token=acc_tok,
                                    mode_id=mode_id,
                                    map_id=map_id
                                )

                                match_index = await _inc_match(uid_str)
                                total = await _get_total_match_count()
                                print_colored(
                                    f"🚀 [{match_mode}] [MATCH #{match_index}] UDP starting → {server_ip_port} (background)",
                                    Colors.CYAN
                                )
                                print_success(
                                    f"[FUNCTIONAL] UDP task started. "
                                    f"UID active: {match_index} | Total: {total}"
                                )

                                new_match = asyncio.create_task(
                                    play_game(
                                        server_ip_port,
                                        thunder,
                                        sharma,
                                        udp_key,
                                        match_code,
                                        effective_acc_id,
                                        "ID",
                                        client_version,
                                        current_key,
                                        current_iv,
                                        match_index=match_index
                                    )
                                )
                                play_matches.append(new_match)

                                consecutive_parse_failures = 0

                                try:
                                    writer.close()
                                    await writer.wait_closed()
                                except Exception:
                                    pass

                                effective_mode, _ = get_effective_mode()
                                offline_wait = (
                                    LW_NEW_MATCH_DELAY if effective_mode == "LW"
                                    else NEW_MATCH_DELAY
                                )
                                print_info(
                                    f"[OFFLINE] {offline_wait}s offline → "
                                    f"reload token → new StartMatch"
                                )
                                await asyncio.sleep(offline_wait)
                                reconnects = 0
                                break

                            else:
                                consecutive_parse_failures += 1
                                print_warning(
                                    f"[FUNCTIONAL] Non-match big packet "
                                    f"(#{consecutive_parse_failures}/{MAX_CONSECUTIVE_PARSE_FAILURES}) "
                                    f"→ reconnecting"
                                )

                                if consecutive_parse_failures >= MAX_CONSECUTIVE_PARSE_FAILURES:
                                    print_error(
                                        f"[FUNCTIONAL] {MAX_CONSECUTIVE_PARSE_FAILURES}x parse failures "
                                        f"→ invalidating cache for fresh login"
                                    )
                                    if current_account_data:
                                        try:
                                            if current_account_data.get('auth_uid'):
                                                cache_invalidate(str(current_account_data['auth_uid']))
                                            if current_account_data.get('auth_token'):
                                                cache_invalidate(f"tok_{current_account_data['auth_token'][:20]}")
                                        except Exception:
                                            pass
                                    consecutive_parse_failures = 0

                                try:
                                    writer.close()
                                    await writer.wait_closed()
                                except Exception:
                                    pass
                                await asyncio.sleep(NON_MATCH_RECONNECT_DELAY)
                                break

                        except Exception as e:
                            print_error(f"[FUNCTIONAL] Match packet error: {e}")
                            consecutive_parse_failures += 1
                            if consecutive_parse_failures >= MAX_CONSECUTIVE_PARSE_FAILURES:
                                if current_account_data:
                                    try:
                                        if current_account_data.get('auth_uid'):
                                            cache_invalidate(str(current_account_data['auth_uid']))
                                        if current_account_data.get('auth_token'):
                                            cache_invalidate(f"tok_{current_account_data['auth_token'][:20]}")
                                    except Exception:
                                        pass
                                consecutive_parse_failures = 0
                            try:
                                writer.close()
                                await writer.wait_closed()
                            except Exception:
                                pass
                            await asyncio.sleep(NON_MATCH_RECONNECT_DELAY)
                            break

                    if 30 <= packet_length <= 40:
                        continue

            except asyncio.CancelledError:
                print_warning(f"[FUNCTIONAL] Cancelled — cancelling {len(play_matches)} UDP matches")
                for m in play_matches:
                    if not m.done():
                        m.cancel()
                if play_matches:
                    await asyncio.gather(*play_matches, return_exceptions=True)
                play_matches.clear()
                raise
            except Exception as e:
                print_error(f"[FUNCTIONAL] TCP state ({uid_str}): {e}")

                play_matches[:] = [m for m in play_matches if not m.done()]

                if writer:
                    try:
                        writer.close()
                        await writer.wait_closed()
                    except Exception:
                        pass

                if "Cache expired" in str(e):
                    print_warning(f"[FUNCTIONAL] Triggering re-login for {uid_str}")
                    break

                reconnects += 1
                if reconnects > max_reconnects:
                    print_error("[FUNCTIONAL] Max reconnects reached, retrying...")
                    reconnects = 0
                    await asyncio.sleep(3)
                    continue

                await asyncio.sleep(min(reconnects, 2))

    except asyncio.CancelledError:
        print_warning(f"[FUNCTIONAL] Outer cancelled. {len(play_matches)} UDP matches still running.")
        for m in play_matches:
            if not m.done():
                m.cancel()
        if play_matches:
            await asyncio.gather(*play_matches, return_exceptions=True)
        play_matches.clear()
        raise


async def informational(addrs, starter_packet, key, iv, region="ID", max_reconnects=3):
    reconnects = 0
    ip, port = addrs.split(":")
    while True:
        writer = None
        ping_task = None
        try:
            resolved_ip = await resolve_host_cloudflare(ip)
            reader, writer = await asyncio.open_connection(resolved_ip, int(port))

            raw_sock = writer.get_extra_info('socket')
            if raw_sock:
                optimize_tcp_socket(raw_sock)

            writer.write(bytes.fromhex(starter_packet))
            await writer.drain()
            reconnects = 0

            try:
                init_ka = await send_keep_alive(region)
                if init_ka and writer and not writer.is_closing():
                    writer.write(init_ka)
                    await asyncio.wait_for(writer.drain(), timeout=3)
            except Exception:
                pass

            async def info_keepalive():
                ka_bytes = await send_keep_alive(region)
                while True:
                    await asyncio.sleep(5)
                    try:
                        if writer and not writer.is_closing():
                            writer.write(ka_bytes)
                            await writer.drain()
                    except Exception:
                        break

            ping_task = asyncio.create_task(info_keepalive())

            while True:
                data = await reader.read(8192)
                if not data:
                    raise ConnectionError("Connection closed")
        except asyncio.CancelledError:
            if ping_task:
                ping_task.cancel()
            if writer:
                try:
                    writer.close()
                    await writer.wait_closed()
                except Exception:
                    pass
            raise
        except Exception:
            if ping_task:
                ping_task.cancel()
            if writer:
                try:
                    writer.close()
                    await writer.wait_closed()
                except Exception:
                    pass
            reconnects += 1
            if reconnects > max_reconnects:
                await asyncio.sleep(3)
                reconnects = 0
            else:
                await asyncio.sleep(1)


# ==================== ACCOUNT PROCESSORS ====================

def _register_credentials(account_data: Dict):
    try:
        acc_id = str(account_data['account_id'])
        bot_state.account_credentials[acc_id] = account_data
        if account_data.get('auth_uid'):
            bot_state.account_credentials[str(account_data['auth_uid'])] = account_data
        if account_data.get('auth_token'):
            bot_state.account_credentials[f"tok_{account_data['auth_token'][:20]}"] = account_data
    except Exception:
        pass


async def refresh_account_profile(account_data_or_uid: Any):
    """Refresh one account's profile/EXP without overlapping requests for the same UID."""
    try:
        if isinstance(account_data_or_uid, str):
            uid = str(account_data_or_uid)
            account_data = bot_state.account_credentials.get(uid)
        else:
            account_data = account_data_or_uid
            uid = str(account_data.get('account_id')) if account_data else ''

        if not account_data or not uid:
            return False

        url = account_data.get('server_url')
        token = account_data.get('token')
        release_version = account_data.get('release_version')
        payload = account_data.get('login_payload_data')
        if not (url and token and release_version and payload):
            return False

        async with _get_refresh_lock(uid):
            async with _REFRESH_SEMAPHORE:
                res = await send_getlogin(payload, url, token, release_version)

            if not res:
                return False

            res_proto, dict_res = res
            level = int(get_proto_field(dict_res, 6, account_data.get('level', 1)) or 1)
            exp = int(get_proto_field(dict_res, 7, account_data.get('exp', 0)) or 0)
            likes = int(get_proto_field(dict_res, 8, account_data.get('likes', 0)) or 0)
            nickname = res_proto.nickname or get_proto_field(dict_res, 4, account_data.get('nickname', ''))

            acc_id = str(account_data['account_id'])
            # Keep the in-memory credential/cache snapshot fresh as well as the dashboard.
            account_data['level'] = level
            account_data['exp'] = exp
            account_data['likes'] = likes
            if nickname:
                account_data['nickname'] = nickname
            account_data['cached_at'] = time.time()

            bot_state.update_exp(acc_id, exp, level)
            if acc_id in bot_state.accounts:
                bot_state.accounts[acc_id]['likes'] = likes
                if nickname:
                    bot_state.accounts[acc_id]['nickname'] = nickname

            # Keep the hot path in memory. Writing token_cache.json on every refresh
            # would add unnecessary disk I/O when many accounts are active.

            print_info(f"[EXP-REFRESH] UID {acc_id} -> Level: {level}, EXP: {exp}")
            return True
    except asyncio.CancelledError:
        raise
    except Exception as e:
        print_warning(f"[EXP-REFRESH] UID {uid if 'uid' in locals() else '?'} temporary error: {e}")
        return False


async def _process_account_uid_pass(uid: str, password: str) -> Optional[Dict]:
    cached = cache_get(uid)
    if cached:
        print_success(f"[CACHE HIT] UID {uid} loaded from token_cache.json (no login)")
        acc_id = str(cached['account_id'])
        bot_state.register_account(
            uid=acc_id,
            nickname=cached.get('nickname', f"Player_{acc_id}"),
            region=cached.get('region', 'ID'),
            level=cached.get('level', 1),
            exp=cached.get('exp', 0),
            likes=cached.get('likes', 0)
        )
        _register_credentials(cached)
        return cached

    print_info(f"[LOGIN] Full login for UID {uid}...")
    try:
        verconfig_res = await version_config()
        if verconfig_res is None:
            print_error(f"[LOGIN] version_config failed for UID {uid}")
            return None
        release_version, client_version, server_url = verconfig_res

        tokengrant_response = await get_access_token(uid, password)
        if tokengrant_response is None:
            print_error(f"[LOGIN] get_access_token failed for UID {uid}")
            return None
        open_id, access_token, platform = tokengrant_response

        device_info = get_device_for_account(uid)

        # 🔧 FIX: guard against empty payload
        login_payload_data = await build_majorlogin_payload(
            open_id, access_token, platform, client_version, device_info
        )
        if not login_payload_data:
            print_error(f"[LOGIN] Failed to build MajorLogin payload for UID {uid}")
            return None

        majorlogin_response = await send_majorlogin(
            login_payload_data, release_version, server_url
        )
        if majorlogin_response is None:
            print_error(f"[LOGIN] MajorLogin rejected for UID {uid}")
            return None

        getlogin_result = await send_getlogin(
            login_payload_data,
            majorlogin_response.url,
            majorlogin_response.token,
            release_version
        )
        if getlogin_result is None:
            print_error(f"[LOGIN] GetLoginData failed for UID {uid}")
            return None
        res_proto, dict_res = getlogin_result

        acc_id = str(majorlogin_response.account_id)
        level = int(get_proto_field(dict_res, 6, 1))
        exp = int(get_proto_field(dict_res, 7, 0))
        likes = int(get_proto_field(dict_res, 8, 0))
        nickname = res_proto.nickname or get_proto_field(dict_res, 4, f"Player_{acc_id}")
        region = majorlogin_response.region or get_proto_field(dict_res, 3, "ID")

        bot_state.register_account(uid=acc_id, nickname=nickname, region=region, level=level, exp=exp, likes=likes)

        account_data = {
            'account_id': majorlogin_response.account_id,
            'nickname': nickname,
            'region': region,
            'level': level,
            'exp': exp,
            'likes': likes,
            'open_id': open_id,
            'access_token': access_token,
            'platform': str(platform),
            'token': majorlogin_response.token,
            'server_time': majorlogin_response.server_time,
            'aes_ak': majorlogin_response.aes_ak,
            'iv_i': majorlogin_response.iv_i,
            'functional_addrs': res_proto.functional_addrs or get_proto_field(dict_res, 14),
            'informational_addrs': res_proto.informational_addrs or get_proto_field(dict_res, 32),
            'release_version': release_version,
            'client_version': client_version,
            'server_url': majorlogin_response.url,
            'login_payload_data': login_payload_data,
            'auth_type': 'guest',
            'auth_uid': uid,
            'auth_password': password
        }
        _register_credentials(account_data)
        cache_set(uid, account_data)
        return account_data
    except Exception as e:
        print_error(f"process_account_uid_pass error: {e}")
        traceback.print_exc()
        return None


async def _process_account_token(access_token: str) -> Optional[Dict]:
    cache_key = f"tok_{access_token[:20]}"
    cached = cache_get(cache_key)
    if cached:
        print_success(f"[CACHE HIT] Token {access_token[:10]}... loaded from cache")
        acc_id = str(cached['account_id'])
        bot_state.register_account(
            uid=acc_id,
            nickname=cached.get('nickname', f"Player_{acc_id}"),
            region=cached.get('region', 'ID'),
            level=cached.get('level', 1),
            exp=cached.get('exp', 0),
            likes=cached.get('likes', 0)
        )
        _register_credentials(cached)
        return cached

    print_info("[LOGIN] Full login with Access Token...")
    try:
        verconfig_res = await version_config()
        if verconfig_res is None:
            print_error("[LOGIN] version_config failed (token flow)")
            return None
        release_version, client_version, server_url = verconfig_res

        import requests
        url = f"https://100067.connect.garena.com/oauth/token/inspect?token={access_token}"
        hdrs = {
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "100067.connect.garena.com",
            "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)"
        }
        resp = await asyncio.to_thread(requests.get, url, headers=hdrs, timeout=10)
        data = resp.json()

        if 'error' in data:
            print_error(f"[LOGIN] Token inspect error: {data.get('error')}")
            return None

        open_id = data.get('open_id')
        platform = data.get('platform', 4)

        if not open_id:
            print_error("[LOGIN] No open_id in token inspect response")
            return None

        device_info = get_device_for_account(open_id)

        # 🔧 FIX: guard against empty payload
        login_payload_data = await build_majorlogin_payload(
            open_id, access_token, str(platform), client_version, device_info
        )
        if not login_payload_data:
            print_error("[LOGIN] Failed to build MajorLogin payload (token flow)")
            return None

        majorlogin_response = await send_majorlogin(
            login_payload_data, release_version, server_url
        )
        if majorlogin_response is None:
            print_error("[LOGIN] MajorLogin rejected (token flow)")
            return None

        getlogin_result = await send_getlogin(
            login_payload_data,
            majorlogin_response.url,
            majorlogin_response.token,
            release_version
        )
        if getlogin_result is None:
            print_error("[LOGIN] GetLoginData failed (token flow)")
            return None

        res_proto, dict_res = getlogin_result
        acc_id = str(majorlogin_response.account_id)
        level = int(get_proto_field(dict_res, 6, 1))
        exp = int(get_proto_field(dict_res, 7, 0))
        likes = int(get_proto_field(dict_res, 8, 0))
        nickname = res_proto.nickname or get_proto_field(dict_res, 4, f"Player_{acc_id}")
        region = majorlogin_response.region or get_proto_field(dict_res, 3, "ID")

        bot_state.register_account(uid=acc_id, nickname=nickname, region=region, level=level, exp=exp, likes=likes)

        account_data = {
            'account_id': majorlogin_response.account_id,
            'nickname': nickname,
            'region': region,
            'level': level,
            'exp': exp,
            'likes': likes,
            'open_id': open_id,
            'access_token': access_token,
            'platform': str(platform),
            'token': majorlogin_response.token,
            'server_time': majorlogin_response.server_time,
            'aes_ak': majorlogin_response.aes_ak,
            'iv_i': majorlogin_response.iv_i,
            'functional_addrs': res_proto.functional_addrs or get_proto_field(dict_res, 14),
            'informational_addrs': res_proto.informational_addrs or get_proto_field(dict_res, 32),
            'release_version': release_version,
            'client_version': client_version,
            'server_url': majorlogin_response.url,
            'login_payload_data': login_payload_data,
            'auth_type': 'token',
            'auth_token': access_token
        }
        _register_credentials(account_data)
        cache_set(cache_key, account_data)
        return account_data
    except Exception as e:
        print_error(f"process_account_token error: {e}")
        traceback.print_exc()
        return None


async def process_account_uid_pass(uid: str, password: str) -> Optional[Dict]:
    # Cache hits return immediately; only real login work is rate-limited.
    cached = cache_get(uid)
    if cached:
        acc_id = str(cached['account_id'])
        bot_state.register_account(
            uid=acc_id, nickname=cached.get('nickname', f"Player_{acc_id}"),
            region=cached.get('region', 'ID'), level=cached.get('level', 1),
            exp=cached.get('exp', 0), likes=cached.get('likes', 0)
        )
        _register_credentials(cached)
        print_success(f"[CACHE HIT] UID {uid} loaded from token_cache.json (no login)")
        return cached
    async with _LOGIN_SEMAPHORE:
        return await _process_account_uid_pass(uid, password)


async def process_account_token(access_token: str) -> Optional[Dict]:
    cache_key = f"tok_{access_token[:20]}"
    cached = cache_get(cache_key)
    if cached:
        acc_id = str(cached['account_id'])
        bot_state.register_account(
            uid=acc_id, nickname=cached.get('nickname', f"Player_{acc_id}"),
            region=cached.get('region', 'ID'), level=cached.get('level', 1),
            exp=cached.get('exp', 0), likes=cached.get('likes', 0)
        )
        _register_credentials(cached)
        print_success(f"[CACHE HIT] Token {access_token[:10]}... loaded from cache")
        return cached
    async with _LOGIN_SEMAPHORE:
        return await _process_account_token(access_token)


async def run_account_worker(account_data: Dict, label: str):
    acc_id = str(account_data['account_id'])
    informational_task = None
    exp_task = None
    try:
        reg = account_data.get('region', 'ID')
        tcp_packet_online = await build_tcp_startup_packet(
            account_data['account_id'],
            account_data['token'],
            account_data['server_time'],
            account_data['aes_ak'],
            account_data['iv_i'],
            region=reg,
            typ='OnLine'
        )

        tcp_packet_chat = await build_tcp_startup_packet(
            account_data['account_id'],
            account_data['token'],
            account_data['server_time'],
            account_data['aes_ak'],
            account_data['iv_i'],
            region=reg,
            typ='ChaT'
        )

        informational_task = asyncio.create_task(
            informational(
                account_data['informational_addrs'],
                tcp_packet_chat,
                account_data['aes_ak'],
                account_data['iv_i'],
                region=reg
            )
        )

        async def exp_refresher():
            # Stagger refreshes so dozens of accounts do not hit GetLoginData
            # at the same moment. Keep the refresher alive even when one request
            # fails, otherwise EXP updates silently stop after a transient error.
            await asyncio.sleep(random.uniform(10.0, 35.0))
            while True:
                fresh = bot_state.account_credentials.get(acc_id)
                if fresh:
                    await refresh_account_profile(fresh)
                # Jitter prevents 20–25 accounts from refreshing in one burst.
                await asyncio.sleep(random.uniform(55.0, 85.0))

        exp_task = asyncio.create_task(exp_refresher())

        functional_task = asyncio.create_task(
            functional_lone_wolf(
                account_data['functional_addrs'],
                tcp_packet_online,
                account_data['region'],
                account_data['client_version'],
                account_data['aes_ak'],
                account_data['iv_i'],
                account_id=acc_id,
                account_data=account_data
            )
        )

        await functional_task

    except asyncio.CancelledError:
        raise
    except Exception as e:
        print_error(f"run_account_worker error for {label}: {e}")
    finally:
        for t in (informational_task, exp_task):
            if t and not t.done():
                t.cancel()
        for t in (informational_task, exp_task):
            if t:
                try:
                    await t
                except (asyncio.CancelledError, Exception):
                    pass


async def account_loop_guest(uid: str, password: str):
    while True:
        try:
            print_info(f"[LOGIN] Starting login for Guest UID: {uid}...")
            try:
                bot_state.update_status(str(uid), "CONNECTING")
            except Exception:
                pass
            account_data = await process_account_uid_pass(uid, password)
            if not account_data:
                print_error(f"Login failed for UID: {uid}. Retrying in 15 seconds...")
                try:
                    bot_state.update_status(str(uid), "ERROR")
                except Exception:
                    pass
                await asyncio.sleep(15)
                continue

            await run_account_worker(account_data, uid)
            print_warning(f"Session finished for {uid}. Reconnecting in 3s...")
            await asyncio.sleep(3)
        except asyncio.CancelledError:
            print_warning(f"Worker for {uid} stopped.")
            try:
                bot_state.update_status(str(uid), "OFFLINE")
            except Exception:
                pass
            break
        except Exception as e:
            print_error(f"Error for UID {uid}: {e}. Retrying in 10s...")
            await asyncio.sleep(10)


async def account_loop_token(token: str):
    token_label = token[:10]
    while True:
        try:
            print_info("[LOGIN] Starting login with Access Token...")
            account_data = await process_account_token(token)
            if not account_data:
                print_error("Login failed for Token. Retrying in 15 seconds...")
                await asyncio.sleep(15)
                continue

            acc_id = str(account_data['account_id'])
            await run_account_worker(account_data, acc_id)
            print_warning("Token session finished. Reconnecting in 3s...")
            await asyncio.sleep(3)
        except asyncio.CancelledError:
            print_warning(f"Worker for token {token_label} stopped.")
            break
        except Exception as e:
            print_error(f"Token error: {e}. Retrying in 10s...")
            await asyncio.sleep(10)


# ==================== ACCOUNTS LOADER ====================

def load_accounts():
    accounts = []
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    accounts = data
        except Exception as e:
            print_error(f"Could not load {ACCOUNTS_FILE}: {e}")

    if not accounts and FALLBACK_UID and FALLBACK_PASSWORD:
        accounts.append({"uid": FALLBACK_UID, "password": FALLBACK_PASSWORD})

    return accounts


# ==================== MAIN ====================

async def main():
    print_colored("=" * 60, Colors.CYAN)
    print_colored("    TEAM 84FF - FreeFire Level Up Bot (Web Dashboard Mode)", Colors.GREEN)
    print_colored("   Persistent Device ID + TRUE Parallel + Smart DNS", Colors.WHITE)
    print_colored("=" * 60, Colors.CYAN)
    print_info(f"Start Match Interval: {START_MATCH_INTERVAL}s")
    print_info(f"Offline Wait: {NEW_MATCH_DELAY}s (after match found)")
    print_info(f"Non-match Reconnect: {NON_MATCH_RECONNECT_DELAY}s")
    print_info(f"Cache Invalidation Threshold: {MAX_CONSECUTIVE_PARSE_FAILURES}x")
    print_info(f"Max active matches/account: {MAX_CONCURRENT_MATCHES}")
    print_info(f"Cache TTL: {TOKEN_CACHE_TTL}s ({TOKEN_CACHE_TTL//60} min)")
    print_info("Device System: 1 ID = 1 Persistent Device ID (devices.json)")
    print_colored("=" * 60, Colors.CYAN)

    write_embedded_index_html()
    try:
        await start_web_dashboard(host=WEB_HOST, port=WEB_PORT)
        print_success(f"Web Dashboard live at http://localhost:{WEB_PORT}")
    except Exception as e:
        print_error(f"Could not start web dashboard: {e}")

    async def on_account_added_handler(data):
        if "token" in data and data["token"]:
            t = str(data["token"]).strip()
            key = t[:10]
            existing = bot_state.account_workers.get(key)
            if existing and not existing.done():
                bot_state.log(f"Account worker already running: {key}", "warning")
                return
            task = asyncio.create_task(account_loop_token(t))
            bot_state.account_workers[key] = task
        elif "uid" in data and "password" in data:
            u = str(data["uid"]).strip()
            p = str(data["password"]).strip()
            existing = bot_state.account_workers.get(u)
            if existing and not existing.done():
                bot_state.log(f"Account worker already running: {u}", "warning", u)
                return
            task = asyncio.create_task(account_loop_guest(u, p))
            bot_state.account_workers[u] = task

    async def on_refresh_account_handler(uid):
        await refresh_account_profile(uid)

    bot_state.refresh_callbacks["on_account_added"] = on_account_added_handler
    bot_state.refresh_callbacks["on_refresh_account"] = on_refresh_account_handler

    accounts = load_accounts()

    if not accounts:
        print_warning(f"No accounts found in {ACCOUNTS_FILE}! Add accounts from Web Dashboard.")
        print_warning(f"Open: http://localhost:{WEB_PORT}")

    # Stagger initial worker startup. This avoids 20-30 accounts opening/login
    # bursts at the exact same instant while preserving the existing login flow.
    for index, acc in enumerate(accounts):
        if index:
            await asyncio.sleep(random.uniform(1.0, 2.5))
        if "token" in acc and acc["token"]:
            t = asyncio.create_task(account_loop_token(acc["token"]))
            bot_state.account_workers[acc["token"][:10]] = t
        elif "uid" in acc and "password" in acc and acc["uid"]:
            u = str(acc["uid"])
            t = asyncio.create_task(account_loop_guest(u, acc["password"]))
            bot_state.account_workers[u] = t

    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print_warning("\n[STOP] Shutting down all accounts...")
        for t in list(bot_state.account_workers.values()):
            if not t.done():
                t.cancel()
        await asyncio.gather(*bot_state.account_workers.values(), return_exceptions=True)
        try:
            await client.aclose()
        except Exception:
            pass
        print_success("All sessions cleanly closed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_warning("\nProgram stopped by user.")