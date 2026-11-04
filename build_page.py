# -*- coding: utf-8 -*-
"""Build a single-file Chinese landing page for the Bilibili creator CabbageTimil."""
import json, datetime, html
import base64, io, os
from PIL import Image

DATA = json.load(open("bili_data.json", encoding="utf-8"))
P = DATA["profile"]

def square_data_uri(path, size, quality=86):
    """Center-crop to square, resize, return a base64 data URI (keeps the page self-contained)."""
    try:
        im = Image.open(path).convert("RGB")
        w, h = im.size
        s = min(w, h)
        im = im.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
        im = im.resize((size, size), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=quality, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return P["face"]

LOGO_URI = square_data_uri("avatar.jpg", 128)
FAVICON_URI = square_data_uri("avatar.jpg", 64, 80)

def esc(s):
    return html.escape(s or "", quote=True)

def views(n):
    try:
        n = int(n or 0)
    except Exception:
        return "—"
    if n >= 100000000:
        return f"{n/100000000:.1f}亿"
    if n >= 10000:
        return f"{n/10000:.1f}万"
    return f"{n:,}"

def vnum(n):
    return f"{int(n):,}"

def date(ts):
    if not ts:
        return ""
    return datetime.datetime.fromtimestamp(int(ts)).strftime("%Y.%m.%d")

def img(url):
    if not url:
        return ""
    return url.replace("http://", "https://")

def href(bv):
    return f"https://www.bilibili.com/video/{bv}"

latest = DATA["latest"]
featured = sorted(latest, key=lambda v: -(v["play"] or 0))[:9]
recent = sorted(latest, key=lambda v: -(v["pub"] or 0))[:5]
collections = DATA["collections"]

BLURB = {
    "DC联盟战斗合集": "从 DC 联盟时代一路存档到 WWW 世界大战，欧服华人视角的完整战役库。",
    "瞎编EVE": "不严肃的新伊甸观察：局势推演、脑洞与吐槽，聊点正史之外的东西。",
    "DC联盟会议记录": "联盟会议实录，听指挥层如何讨论战略、分配舰队、决定下一场战役。",
    "EVE宇宙记者第三方会战视角": "不在任何一方的舰队里，只把战场本身记录下来。",
    "EVE欧服 帝国北伐": "帝国北上的一条战线：X47、EX6-AO、SNFV-I 与沿途的每一场结构战。",
    "EVE快讯": "三分钟讲清楚这几天新伊甸发生了什么——适合没时间看战报的人。",
    "燃烧低安": "低安势力版图重划，小航队、联合围剿与低安战争的连锁反应。",
    "PanFam系列": "PanFam 阵营的来路与当下，理解欧服权力结构绕不开的一块拼图。",
    "EVE帝国东线战场": "东线战事档案，帝国与凛冬在东部星域的攻防切片。",
}
DEFAULT_BLURB = "欧服战场的一手记录。"

def vcard(v):
    return f"""      <a class="vcard" href="{href(v['bvid'])}" target="_blank" rel="noopener" data-reveal>
        <div class="thumb">
          <img src="{img(v['cover'])}" alt="{esc(v['title'])}" referrerpolicy="no-referrer" loading="lazy" onerror="this.closest('.thumb').classList.add('noimg')">
          <span class="chip play">▶ {views(v['play'])}</span>
          <span class="chip dur">{esc(v['dur'] or '')}</span>
          <span class="thumb-veil"></span>
        </div>
        <div class="vbody">
          <h3>{esc(v['title'])}</h3>
          <div class="vmeta"><span>{date(v['pub'])}</span><span>{vnum(v['play'] or 0)} 播放</span></div>
        </div>
      </a>"""

def ccard(c):
    sid = c["id"]
    name = (c["name"] or "").replace("合集·", "").strip()
    link = f"https://space.bilibili.com/{P['mid']}/lists/{sid}?type=season"
    cover = img(c["cover"])
    if not cover or "templar" in cover or "york-static" in cover:
        cover = img((c["videos"][0]["cover"] if c["videos"] else ""))
    return f"""      <a class="ccard" href="{link}" target="_blank" rel="noopener" data-reveal>
        <div class="cthumb"><img src="{cover}" alt="{esc(name)}" referrerpolicy="no-referrer" loading="lazy" onerror="this.parentElement.classList.add('noimg')"></div>
        <div class="cinfo">
          <div class="ctop"><span class="tag">合集</span><span class="ccount">{c['count']} 部</span></div>
          <h3>{esc(name)}</h3>
          <p>{esc(BLURB.get(name, DEFAULT_BLURB))}</p>
        </div>
      </a>"""

def recent_row(v):
    return f"""        <a class="row" href="{href(v['bvid'])}" target="_blank" rel="noopener">
          <span class="rdate">{date(v['pub'])}</span>
          <span class="rtitle">{esc(v['title'])}</span>
          <span class="rplay">{views(v['play'])} 播放</span>
        </a>"""

TIMELINE = [
    ("2023", "DC 联盟时代", "深渊之路与 X47 星城攻防，DC 联盟的兴衰被一集集记录下来。", "BV1is4y1K7ib", "THIS IS EVE ONLINE! X47 星城结构战"),
    ("2024", "帝国北伐", "EX6-AO、SNFV-I、U-QVWD……帝国舰队一路北上，战线不断拉长。", "BV1JSefe5ENm", "SNFV-I 会战：中国玩家舰队视角"),
    ("2025", "三千人会战", "BWF-ZZ 3500+ 人、PR-8CA 结构战、1DQ1 星城会战，欧服战争规模刷新纪录。", "BV15PdFYiE3i", "BWF-ZZ 3750 人大型会战"),
    ("2026", "WWW 世界大战", "4-HWWF 首都星城被破、49- 星城两千人对轰，2003~2026 全史梳理同期上线。", "BV1htofBtEBp", "4-HWWF 首都星城被打进结构增强"),
]

def timeline_item(year, title, text, bvid, label):
    return f"""      <li class="tl-item" data-reveal>
        <span class="tl-year">{year}</span>
        <div class="tl-body">
          <h3>{esc(title)}</h3>
          <p>{esc(text)}</p>
          <a class="tl-link" href="{href(bvid)}" target="_blank" rel="noopener">代表作 · {esc(label)} <span>↗</span></a>
        </div>
      </li>"""

STATS = [
    (P["archive_count"] or 0, "部投稿", ""),
    (P["fans"] or 0, "位关注者", ""),
    (P["likes"] or 0, "次点赞", ""),
    (P["level"] or 0, "B站等级", "Lv."),
]

def stat_item(n, label, prefix):
    return f"""          <div class="stat">
            <div class="snum" data-count="{n}" data-prefix="{prefix}">0</div>
            <div class="slabel">{label}</div>
          </div>"""

body = []
body.append(f"""  <section id="home" class="hero">
    <div class="hero-grid"></div>
    <div class="wrap hero-inner">
      <div class="hero-copy">
        <div class="badge" data-reveal><span class="pulse"></span> EVE ONLINE · OFFICIAL PARTNER</div>
        <h1 data-reveal>Cabbage<span class="accent">Timil</span></h1>
        <p class="hero-sub" data-reveal>在七千个星系之间，做一个诚实的记录者。</p>
        <p class="hero-desc" data-reveal>
          欧服华人视角的战地影像档案。从 4-HWWF 首都星城到 49- 星城攻防，
          把新伊甸正在发生的事，翻译成中文玩家听得懂的语言。
        </p>
        <div class="hero-actions" data-reveal>
          <a class="btn primary" href="https://space.bilibili.com/{P['mid']}" target="_blank" rel="noopener">前往 B 站主页 <span>→</span></a>
          <a class="btn ghost" href="https://www.youtube.com/@{esc(P['name'])}" target="_blank" rel="noopener">YouTube 频道</a>
        </div>
        <div class="stats" data-reveal>
{chr(10).join(stat_item(*s) for s in STATS)}
        </div>
      </div>
      <div class="hero-visual" data-reveal>
        <div class="stack">
          <div class="shot s1"><img src="{img(featured[2]['cover'])}" alt="" referrerpolicy="no-referrer" loading="lazy"></div>
          <div class="shot s2"><img src="{img(featured[1]['cover'])}" alt="" referrerpolicy="no-referrer" loading="lazy"></div>
          <div class="shot s3"><img src="{img(featured[0]['cover'])}" alt="" referrerpolicy="no-referrer" loading="lazy"></div>
        </div>
        <div class="stack-caption">NOW RECORDING · NEW EDEN</div>
      </div>
    </div>
    <div class="scroll-hint"><span></span>SCROLL</div>
  </section>

  <section id="about" class="section">
    <div class="wrap">
      <div class="sec-head" data-reveal>
        <span class="eyebrow">01 / 关于</span>
        <h2>把欧服战场，讲给中文玩家听</h2>
        <p>EVE Online 官方合作伙伴。长期跟拍欧服大型会战，做中文社区里少有人做的那件事：<br class="pc">在战报之外，留下画面、时间线和前因后果。</p>
      </div>
      <div class="pillars">
        <article class="pillar" data-reveal>
          <span class="pnum">01</span>
          <h3>战地实录</h3>
          <p>一线会战视角。诱导亮起、旗舰进场、星城进入结构增强的每一分钟，都尽可能完整地拍下来。</p>
        </article>
        <article class="pillar" data-reveal>
          <span class="pnum">02</span>
          <h3>局势快讯</h3>
          <p>WWW 开战以来的战线变化、帝国北伐与凛冬防御，用几分钟把一周的战况讲清楚。</p>
        </article>
        <article class="pillar" data-reveal>
          <span class="pnum">03</span>
          <h3>中文情报</h3>
          <p>把英文社区的战报、会议与舆论翻译成中文，让中国玩家和欧服战场保持零时差。</p>
        </article>
        <article class="pillar" data-reveal>
          <span class="pnum">04</span>
          <h3>历史与百科</h3>
          <p>从 2003 到 2026，EVE 二十余年的大事件、势力变迁与战争全图，做成能一口气看完的档案。</p>
        </article>
      </div>
      <blockquote class="quote" data-reveal>
        <p>“星海灿烂，伊甸之广，容得下每一个热爱游戏的玩家。”</p>
        <cite>—— 《星海灿烂，伊甸之广容得下每一个热爱游戏的玩家》</cite>
      </blockquote>
    </div>
  </section>

  <section id="works" class="section">
    <div class="wrap">
      <div class="sec-head" data-reveal>
        <span class="eyebrow">02 / 精选</span>
        <h2>值得先看的九部</h2>
        <p>按播放量挑选。想快速认识这个频道，从这三部开始：<br class="pc">《2003~2026 大事记》《4-HWWF 首都星城》与《星海灿烂》。</p>
      </div>
      <div class="vgrid">
{chr(10).join(vcard(v) for v in featured)}
      </div>

      <div class="recent" data-reveal>
        <div class="recent-head"><h3>最新更新</h3><a href="https://space.bilibili.com/{P['mid']}/video" target="_blank" rel="noopener">查看全部 {P['archive_count']} 部 →</a></div>
        <div class="rows">
{chr(10).join(recent_row(v) for v in recent)}
        </div>
      </div>
    </div>
  </section>

  <section id="series" class="section">
    <div class="wrap">
      <div class="sec-head" data-reveal>
        <span class="eyebrow">03 / 合集</span>
        <h2>按战役与主题归档</h2>
        <p>九个合集，从 68 部规模的联盟战史到两三部的小专题，方便按线索一次看完。</p>
      </div>
      <div class="cgrid">
{chr(10).join(ccard(c) for c in collections)}
        <a class="ccard cta" href="https://space.bilibili.com/{P['mid']}/lists" target="_blank" rel="noopener" data-reveal>
          <div class="cta-inner">
            <span class="cta-k">BILIBILI · COLLECTIONS</span>
            <h3>在 B 站查看全部合集</h3>
            <p>九个合集持续更新，新战役会第一时间归入对应主题。</p>
            <span class="cta-go">打开合集页 <span>→</span></span>
          </div>
        </a>
      </div>
    </div>
  </section>

  <section id="timeline" class="section">
    <div class="wrap">
      <div class="sec-head" data-reveal>
        <span class="eyebrow">04 / 时间线</span>
        <h2>镜头里的新伊甸</h2>
        <p>四年，四个阶段。频道几乎与欧服最近一轮大战争同步生长。</p>
      </div>
      <ol class="timeline">
{chr(10).join(timeline_item(*t) for t in TIMELINE)}
      </ol>
    </div>
  </section>

  <section id="contact" class="section">
    <div class="wrap">
      <div class="sec-head" data-reveal>
        <span class="eyebrow">05 / 关注与合作</span>
        <h2>一起看这场战争</h2>
        <p>视频首发 B 站，海外玩家可看 YouTube 备份。合作、投稿与战报线索，欢迎直接私信。</p>
      </div>
      <div class="contacts">
        <a class="contact" href="https://space.bilibili.com/{P['mid']}" target="_blank" rel="noopener" data-reveal>
          <span class="clabel">BILIBILI</span>
          <h3>CabbageTimil</h3>
          <p>主阵地 · {P['archive_count']} 部投稿 / {vnum(P['fans'])} 关注</p>
        </a>
        <a class="contact" href="https://www.youtube.com/@{esc(P['name'])}" target="_blank" rel="noopener" data-reveal>
          <span class="clabel">YOUTUBE</span>
          <h3>@CabbageTimil</h3>
          <p>仅供海外玩家观看视频，未专门运营</p>
        </a>
        <div class="contact" data-reveal>
          <span class="clabel">QQ 群</span>
          <h3 id="qq">1027324687</h3>
          <p>粉丝群 · 战报讨论与组队<button class="copy" data-copy="1027324687">复制</button></p>
        </div>
      </div>
      <p class="note" data-reveal>页面内容取自 B 站公开主页与投稿接口，数据更新于 {datetime.datetime.now().strftime('%Y.%m.%d')}。</p>
    </div>
  </section>""")

CSS = r"""
:root{
  --bg:#04060c; --bg2:#070b15; --panel:rgba(14,20,34,.72); --panel2:rgba(9,13,23,.86);
  --line:rgba(255,255,255,.09); --line2:rgba(255,255,255,.16);
  --text:#e9eef7; --muted:#8d9aae; --muted2:#65718a;
  --cyan:#4fd8ff; --cyan-dim:#1b7f9c; --amber:#ffb35c; --violet:#9d7bff;
  --r:18px; --wrap:1180px;
  --mono:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0; background:var(--bg); color:var(--text);
  font-family:"PingFang SC","HarmonyOS Sans SC","Noto Sans SC","Microsoft YaHei",system-ui,-apple-system,sans-serif;
  line-height:1.65; -webkit-font-smoothing:antialiased; overflow-x:hidden;
}
body::before{
  content:""; position:fixed; inset:0; z-index:-2; pointer-events:none;
  background:
    radial-gradient(900px 620px at 78% -8%, rgba(79,216,255,.16), transparent 62%),
    radial-gradient(760px 520px at 6% 8%, rgba(157,123,255,.13), transparent 60%),
    radial-gradient(1000px 700px at 50% 108%, rgba(255,179,92,.07), transparent 60%),
    linear-gradient(180deg,#04060c 0%,#060a12 42%,#04060c 100%);
}
#stars{position:fixed; inset:0; z-index:-1; pointer-events:none; opacity:.75}
img{display:block; max-width:100%}
a{color:inherit; text-decoration:none}
a:focus-visible,button:focus-visible{outline:2px solid var(--cyan); outline-offset:3px; border-radius:4px}
h1,h2,h3{line-height:1.15; letter-spacing:-.02em; margin:0}
.wrap{width:min(var(--wrap),92vw); margin-inline:auto}

/* nav */
.nav{
  position:fixed; top:0; left:0; right:0; z-index:60; height:66px; display:flex; align-items:center;
  backdrop-filter:blur(16px) saturate(140%); -webkit-backdrop-filter:blur(16px) saturate(140%);
  background:linear-gradient(180deg,rgba(4,6,12,.92),rgba(4,6,12,.55));
  border-bottom:1px solid rgba(255,255,255,.06); transition:background .3s;
}
.nav-in{width:min(var(--wrap),92vw); margin-inline:auto; display:flex; align-items:center; justify-content:space-between; gap:20px}
.brand{display:flex; align-items:center; gap:10px; font-weight:700; letter-spacing:.02em}
.brand .mark{width:34px; height:34px; flex:0 0 auto; border-radius:10px; object-fit:cover; background:#0c1524;
  box-shadow:0 0 0 1px rgba(255,255,255,.22), 0 0 0 4px rgba(79,216,255,.06), 0 0 18px rgba(79,216,255,.4);
  transition:box-shadow .25s, transform .25s}
.brand:hover .mark{box-shadow:0 0 0 1px rgba(79,216,255,.7), 0 0 0 4px rgba(79,216,255,.12), 0 0 26px rgba(79,216,255,.6); transform:translateY(-1px)}
.brand small{display:block; font:500 10px/1.2 var(--mono); letter-spacing:.18em; color:var(--muted2)}
.nav-links{display:flex; gap:26px; font-size:13.5px; color:var(--muted)}
.nav-links a{position:relative; padding:6px 0; transition:color .2s}
.nav-links a::after{content:"";position:absolute;left:0;right:100%;bottom:0;height:1px;background:var(--cyan);transition:right .25s}
.nav-links a:hover{color:var(--text)}
.nav-links a:hover::after{right:0}
.nav-cta{font-size:13px; padding:9px 16px; border:1px solid var(--line2); border-radius:999px; color:var(--text); transition:.2s}
.nav-cta:hover{border-color:var(--cyan); box-shadow:0 0 0 3px rgba(79,216,255,.12)}

/* hero */
.hero{position:relative; padding:150px 0 90px; min-height:min(100svh,860px); display:flex; flex-direction:column; justify-content:center; overflow:hidden}
.hero-grid{
  position:absolute; inset:0; pointer-events:none; opacity:.5;
  background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);
  background-size:72px 72px;
  mask-image:radial-gradient(ellipse 80% 65% at 50% 40%,#000 30%,transparent 78%);
  -webkit-mask-image:radial-gradient(ellipse 80% 65% at 50% 40%,#000 30%,transparent 78%);
}
.hero-inner{position:relative; display:grid; grid-template-columns:1.08fr .92fr; gap:48px; align-items:center}
.badge{
  display:inline-flex; align-items:center; gap:9px; font:600 11px/1 var(--mono); letter-spacing:.2em;
  color:#bff0ff; padding:9px 14px; border-radius:999px; border:1px solid rgba(79,216,255,.3);
  background:linear-gradient(90deg,rgba(79,216,255,.14),rgba(79,216,255,.03)); margin-bottom:26px;
}
.pulse{width:6px;height:6px;border-radius:50%;background:var(--cyan);box-shadow:0 0 0 0 rgba(79,216,255,.6);animation:pulse 2.4s infinite}
@keyframes pulse{70%{box-shadow:0 0 0 9px rgba(79,216,255,0)}100%{box-shadow:0 0 0 0 rgba(79,216,255,0)}}
.hero h1{font-size:clamp(44px,6.4vw,92px); font-weight:800; letter-spacing:-.045em}
.hero h1 .accent{background:linear-gradient(100deg,var(--cyan) 10%,#a8e9ff 45%,var(--violet) 95%);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero-sub{margin:18px 0 0; font-size:clamp(17px,1.6vw,21px); color:#cfe4f2; font-weight:500}
.hero-desc{margin:16px 0 0; max-width:36em; color:var(--muted); font-size:15px}
.hero-actions{display:flex; flex-wrap:wrap; gap:12px; margin:32px 0 0}
.btn{display:inline-flex; align-items:center; gap:10px; padding:13px 22px; border-radius:999px; font-size:14.5px; font-weight:600; transition:transform .2s, box-shadow .25s, background .25s, border-color .25s}
.btn.primary{background:linear-gradient(100deg,#5fe0ff,#8ad8ff 45%,#b7a4ff); color:#04101a; box-shadow:0 10px 34px -10px rgba(79,216,255,.65)}
.btn.primary:hover{transform:translateY(-2px); box-shadow:0 16px 40px -12px rgba(79,216,255,.85)}
.btn.primary span{transition:transform .2s}
.btn.primary:hover span{transform:translateX(3px)}
.btn.ghost{border:1px solid var(--line2); color:var(--text); background:rgba(255,255,255,.02)}
.btn.ghost:hover{border-color:rgba(255,255,255,.4); background:rgba(255,255,255,.06); transform:translateY(-2px)}
.stats{display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin-top:44px; padding-top:26px; border-top:1px solid var(--line)}
.stat .snum{font-family:var(--mono); font-size:clamp(20px,2.1vw,26px); font-weight:700; letter-spacing:-.02em; color:#eaf6ff}
.stat .slabel{font-size:11.5px; color:var(--muted2); letter-spacing:.05em; margin-top:2px}

.hero-visual{position:relative; display:flex; flex-direction:column; align-items:center; justify-content:center}
.hero-visual::before{content:""; position:absolute; width:82%; aspect-ratio:1; border-radius:50%; background:radial-gradient(circle,rgba(79,216,255,.20),rgba(157,123,255,.10) 45%,transparent 68%); filter:blur(28px); z-index:0}
.stack{position:relative; width:100%; max-width:452px; aspect-ratio:16/11; margin-inline:auto; z-index:1}
.shot{position:absolute; inset:0; border-radius:14px; overflow:hidden; border:1px solid rgba(255,255,255,.14); box-shadow:0 30px 70px -30px rgba(0,0,0,.9), 0 0 0 1px rgba(0,0,0,.4)}
.shot img{width:100%;height:100%;object-fit:cover}
.shot::after{content:"";position:absolute;inset:0;background:linear-gradient(200deg,rgba(79,216,255,.10),transparent 40%,rgba(4,6,12,.35))}
.s1{transform:translate(-11%,-9%) rotate(-8deg) scale(.8); opacity:.5; filter:saturate(.65)}
.s2{transform:translate(11%,-4%) rotate(6.5deg) scale(.86); opacity:.78}
.s3{transform:translate(0,6%) rotate(-1.5deg); z-index:3; animation:float 9s ease-in-out infinite}
@keyframes float{50%{transform:translate(0,3%) rotate(-1.5deg)}}
.stack-caption{position:relative; z-index:4; margin-top:34px; text-align:center; font:500 10px/1 var(--mono); letter-spacing:.28em; color:var(--muted2)}
.scroll-hint{position:absolute; left:50%; bottom:26px; transform:translateX(-50%); display:flex; align-items:center; gap:10px; font:500 9.5px/1 var(--mono); letter-spacing:.28em; color:var(--muted2)}
.scroll-hint span{width:1px;height:34px;background:linear-gradient(180deg,transparent,var(--cyan)); display:block; animation:drop 2.2s infinite}
@keyframes drop{0%{opacity:0;transform:scaleY(.2)}40%{opacity:1}100%{opacity:0;transform:scaleY(1)}}

/* sections */
.section{padding:clamp(70px,9vw,120px) 0; border-top:1px solid rgba(255,255,255,.055); position:relative}
section[id]{scroll-margin-top:84px}
.sec-head{max-width:760px; margin-bottom:clamp(34px,4.5vw,54px)}
.eyebrow{display:inline-block; font:600 11px/1 var(--mono); letter-spacing:.24em; color:var(--cyan); margin-bottom:16px}
.sec-head h2{font-size:clamp(26px,3.5vw,42px); font-weight:750; letter-spacing:-.03em}
.sec-head p{margin:16px 0 0; color:var(--muted); font-size:15px}
.pc{display:inline}

/* pillars */
.pillars{display:grid; grid-template-columns:repeat(4,1fr); gap:14px}
.pillar{position:relative; padding:26px 22px 24px; border:1px solid var(--line); border-radius:var(--r); background:linear-gradient(170deg,rgba(255,255,255,.045),rgba(255,255,255,.012)); overflow:hidden; transition:border-color .25s, transform .25s}
.pillar:hover{border-color:rgba(79,216,255,.4); transform:translateY(-4px)}
.pillar .pnum{font:600 10px/1 var(--mono); letter-spacing:.2em; color:var(--muted2)}
.pillar h3{font-size:17.5px; margin:14px 0 10px}
.pillar p{margin:0; font-size:13.6px; color:var(--muted); line-height:1.72}
.quote{margin:clamp(40px,5vw,64px) 0 0; padding:28px 32px; border-left:2px solid var(--cyan); background:linear-gradient(90deg,rgba(79,216,255,.09),transparent 72%); border-radius:0 12px 12px 0}
.quote p{margin:0; font-size:clamp(16px,1.9vw,21px); font-weight:600; letter-spacing:-.01em}
.quote cite{display:block; margin-top:10px; font-style:normal; font-size:12.5px; color:var(--muted2)}

/* video grid */
.vgrid{display:grid; grid-template-columns:repeat(3,1fr); gap:20px}
.vcard{display:flex; flex-direction:column; gap:12px; border-radius:14px; transition:transform .28s}
.vcard:hover{transform:translateY(-5px)}
.thumb{position:relative; aspect-ratio:16/9; border-radius:12px; overflow:hidden; border:1px solid var(--line); background:linear-gradient(140deg,#0d1626,#141d2f)}
.thumb img{width:100%;height:100%;object-fit:cover; transition:transform .55s cubic-bezier(.2,.7,.3,1), filter .3s; filter:saturate(1.02)}
.vcard:hover .thumb img{transform:scale(1.07); filter:saturate(1.15) brightness(1.05)}
.thumb-veil{position:absolute; inset:0; background:linear-gradient(180deg,transparent 45%,rgba(4,6,12,.72)); pointer-events:none}
.thumb::before{content:""; position:absolute; inset:0; box-shadow:inset 0 0 0 1px rgba(79,216,255,0); transition:box-shadow .3s; z-index:2; border-radius:12px}
.vcard:hover .thumb::before{box-shadow:inset 0 0 0 1px rgba(79,216,255,.55), 0 12px 40px -12px rgba(79,216,255,.4)}
.thumb.noimg{background:linear-gradient(140deg,#102033,#1a1530)}
.thumb.noimg img{display:none}
.chip{position:absolute; z-index:3; font:600 11px/1 var(--mono); padding:5px 8px; border-radius:6px; background:rgba(4,8,14,.78); color:#dbe9f5; backdrop-filter:blur(6px); border:1px solid rgba(255,255,255,.12)}
.chip.dur{right:9px; bottom:9px}
.chip.play{left:9px; bottom:9px; color:#bff0ff; border-color:rgba(79,216,255,.3); background:rgba(6,16,26,.82)}
.vbody h3{margin:0; font-size:14.6px; font-weight:600; line-height:1.5; letter-spacing:0;
  display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; min-height:3em}
.vcard:hover .vbody h3{color:#dff4ff}
.vmeta{display:flex; justify-content:space-between; gap:10px; margin-top:7px; font:500 11.5px/1 var(--mono); color:var(--muted2); letter-spacing:.02em}

/* recent */
.recent{margin-top:clamp(38px,5vw,58px); border:1px solid var(--line); border-radius:var(--r); background:var(--panel2); overflow:hidden}
.recent-head{display:flex; align-items:center; justify-content:space-between; padding:18px 22px; border-bottom:1px solid var(--line)}
.recent-head h3{margin:0; font-size:14px; letter-spacing:.02em}
.recent-head a{font:600 12px/1 var(--mono); color:var(--cyan); letter-spacing:.06em}
.recent-head a:hover{text-decoration:underline}
.row{display:grid; grid-template-columns:96px 1fr auto; gap:16px; align-items:center; padding:13px 22px; border-top:1px solid rgba(255,255,255,.05); transition:background .2s}
.row:first-child{border-top:0}
.row:hover{background:rgba(79,216,255,.05)}
.rdate{font:500 11.5px/1 var(--mono); color:var(--muted2)}
.rtitle{font-size:13.8px; color:#cdd9e6; overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
.rplay{font:500 11.5px/1 var(--mono); color:var(--muted2)}

/* collections */
.cgrid{display:grid; grid-template-columns:repeat(2,1fr); gap:14px}
.ccard{display:flex; gap:16px; padding:14px; border:1px solid var(--line); border-radius:14px; background:linear-gradient(150deg,rgba(255,255,255,.04),rgba(255,255,255,.01)); transition:border-color .25s, transform .25s, background .25s}
.ccard:hover{border-color:rgba(157,123,255,.45); transform:translateY(-3px); background:linear-gradient(150deg,rgba(157,123,255,.09),rgba(255,255,255,.01))}
.cthumb{flex:0 0 118px; aspect-ratio:4/3; border-radius:10px; overflow:hidden; border:1px solid rgba(255,255,255,.1); background:#0d1626}
.cthumb img{width:100%;height:100%;object-fit:cover; transition:transform .5s}
.ccard:hover .cthumb img{transform:scale(1.08)}
.cthumb.noimg{background:linear-gradient(140deg,#1a1530,#0d1626)}
.cthumb.noimg img{display:none}
.cinfo{min-width:0; padding:4px 2px 2px}
.ctop{display:flex; align-items:center; gap:10px; margin-bottom:8px}
.tag{font:600 9.5px/1 var(--mono); letter-spacing:.16em; color:#c9b8ff; border:1px solid rgba(157,123,255,.35); padding:4px 6px; border-radius:5px}
.ccount{font:500 11px/1 var(--mono); color:var(--muted2)}
.cinfo h3{margin:0 0 7px; font-size:15.5px; font-weight:650}
.cinfo p{margin:0; font-size:12.8px; color:var(--muted); line-height:1.6}
.ccard.cta{align-items:center; border-color:rgba(79,216,255,.28); background:linear-gradient(140deg,rgba(79,216,255,.10),rgba(157,123,255,.06) 60%,rgba(255,255,255,.01))}
.ccard.cta:hover{border-color:rgba(79,216,255,.6); transform:translateY(-3px)}
.cta-inner{padding:10px 4px}
.cta-k{font:600 9.5px/1 var(--mono); letter-spacing:.2em; color:#8fd8ee}
.ccard.cta h3{margin:10px 0 7px; font-size:17px}
.ccard.cta p{margin:0; font-size:12.8px; color:var(--muted)}
.cta-go{display:inline-flex; align-items:center; gap:8px; margin-top:14px; font:600 12.5px/1 var(--mono); color:#bff0ff}
.cta-go span{transition:transform .2s}
.ccard.cta:hover .cta-go span{transform:translateX(3px)}

/* timeline */
.timeline{list-style:none; margin:0; padding:0 0 0 8px; position:relative}
.timeline::before{content:""; position:absolute; left:8px; top:6px; bottom:6px; width:1px; background:linear-gradient(180deg,rgba(79,216,255,.5),rgba(157,123,255,.35),rgba(255,255,255,.05))}
.tl-item{position:relative; display:grid; grid-template-columns:96px 1fr; gap:28px; padding:0 0 34px 30px}
.tl-item::before{content:""; position:absolute; left:-3px; top:9px; width:9px; height:9px; border-radius:50%; background:var(--bg); border:1.5px solid var(--cyan); box-shadow:0 0 0 4px rgba(79,216,255,.1)}
.tl-year{font:700 15px/1.2 var(--mono); color:#bfefff; letter-spacing:.02em; padding-top:2px}
.tl-body h3{margin:0 0 6px; font-size:16.5px}
.tl-body p{margin:0; color:var(--muted); font-size:14px; max-width:60ch}
.tl-link{display:inline-flex; align-items:center; gap:6px; margin-top:11px; font:500 12.5px/1 var(--mono); color:#8fd8ee; border-bottom:1px dashed rgba(79,216,255,.35); padding-bottom:4px; transition:color .2s, border-color .2s}
.tl-link span{transition:transform .2s}
.tl-link:hover{color:#d7f6ff; border-color:rgba(79,216,255,.8)}
.tl-link:hover span{transform:translate(2px,-2px)}

/* contact */
.contacts{display:grid; grid-template-columns:repeat(3,1fr); gap:14px}
.contact{display:block; padding:26px 24px; border:1px solid var(--line); border-radius:var(--r); background:linear-gradient(160deg,rgba(255,255,255,.05),rgba(255,255,255,.012)); transition:border-color .25s, transform .25s}
a.contact:hover{border-color:rgba(79,216,255,.45); transform:translateY(-4px)}
.clabel{font:600 10px/1 var(--mono); letter-spacing:.22em; color:var(--muted2)}
.contact h3{margin:14px 0 8px; font-size:19px; font-weight:700; letter-spacing:-.01em}
.contact p{margin:0; font-size:13px; color:var(--muted); display:flex; align-items:center; gap:10px; flex-wrap:wrap}
.copy{font:600 10.5px/1 var(--mono); padding:5px 9px; border-radius:5px; border:1px solid var(--line2); background:rgba(255,255,255,.04); color:var(--muted); cursor:pointer; transition:.2s}
.copy:hover{color:var(--text); border-color:var(--cyan)}
.note{margin:34px 0 0; font:400 11.5px/1.6 var(--mono); color:var(--muted2); letter-spacing:.02em}
footer{border-top:1px solid rgba(255,255,255,.06); padding:30px 0 40px}
.foot{width:min(var(--wrap),92vw); margin-inline:auto; display:flex; justify-content:space-between; gap:16px; flex-wrap:wrap; font:400 11.5px/1.6 var(--mono); color:var(--muted2); letter-spacing:.04em}

/* reveal */
[data-reveal]{opacity:0; transform:translateY(16px); transition:opacity .7s cubic-bezier(.2,.7,.3,1), transform .7s cubic-bezier(.2,.7,.3,1)}
[data-reveal].in{opacity:1; transform:none}
.is-static [data-reveal]{opacity:1!important; transform:none!important}

/* responsive */
@media (max-width:1080px){
  .pillars{grid-template-columns:repeat(2,1fr)}
  .vgrid{grid-template-columns:repeat(2,1fr)}
  .contacts{grid-template-columns:1fr}
}
@media (max-width:940px){
  .hero-inner{grid-template-columns:1fr; gap:40px}
  .hero-visual{order:-1; min-height:0; max-width:520px; margin-inline:auto}
  .stack{aspect-ratio:16/11}
  .nav-links{display:none}
  .stats{grid-template-columns:repeat(2,1fr); row-gap:18px}
  .cgrid{grid-template-columns:1fr}
  .row{grid-template-columns:1fr auto; gap:8px 14px}
  .rdate{grid-column:1/-1}
  .pc{display:none}
}
@media (max-width:620px){
  .hero{padding-top:154px}
  .vgrid{grid-template-columns:1fr}
  .pillars{grid-template-columns:1fr}
  .quote{padding:22px 20px}
  .tl-item{grid-template-columns:1fr; gap:6px; padding-left:26px}
  .cthumb{flex-basis:92px}
}
@media (prefers-reduced-motion:reduce){
  *{animation:none!important; transition:none!important}
  html{scroll-behavior:auto}
  [data-reveal]{opacity:1; transform:none}
}
"""

JS = r"""
(function(){
  var rm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var STATIC = /[?&]static=1/.test(location.search);
  if (STATIC) document.documentElement.classList.add('is-static');

  /* starfield */
  var cv = document.getElementById('stars');
  if (cv && !rm) {
    var ctx = cv.getContext('2d'), stars = [], w = 0, h = 0, dpr = Math.min(window.devicePixelRatio || 1, 2);
    function resize(){
      w = cv.width = Math.floor(innerWidth * dpr);
      h = cv.height = Math.floor(innerHeight * dpr);
      cv.style.width = innerWidth + 'px'; cv.style.height = innerHeight + 'px';
      var n = Math.round((innerWidth * innerHeight) / 14000);
      stars = [];
      for (var i = 0; i < n; i++) stars.push({
        x: Math.random() * w, y: Math.random() * h,
        r: (Math.random() * 1.3 + .25) * dpr,
        a: Math.random() * .55 + .15,
        s: Math.random() * .00035 + .00008,
        p: Math.random() * Math.PI * 2,
        c: Math.random() > .93 ? '157,123,255' : (Math.random() > .86 ? '255,179,92' : '200,230,255')
      });
    }
    function draw(t){
      ctx.clearRect(0, 0, w, h);
      for (var i = 0; i < stars.length; i++) {
        var s = stars[i];
        var a = s.a * (.62 + .38 * Math.sin(t * s.s + s.p));
        ctx.beginPath();
        ctx.arc(s.x, s.y + Math.sin(t * s.s * 2 + s.p) * 4 * dpr, s.r, 0, 6.2832);
        ctx.fillStyle = 'rgba(' + s.c + ',' + a.toFixed(3) + ')';
        ctx.fill();
      }
      requestAnimationFrame(draw);
    }
    resize(); addEventListener('resize', resize); requestAnimationFrame(draw);
  }

  /* reveal */
  var items = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !rm && !STATIC) {
    var io = new IntersectionObserver(function(es){
      es.forEach(function(e){ if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: .08 });
    items.forEach(function(el, i){ el.style.transitionDelay = Math.min(i % 4 * 70, 210) + 'ms'; io.observe(el); });
  } else {
    items.forEach(function(el){ el.classList.add('in'); });
  }

  /* count up */
  var nums = document.querySelectorAll('[data-count]');
  function run(el){
    var target = +el.dataset.count, pre = el.dataset.prefix || '', t0 = null, dur = 1200;
    if (!target) { el.textContent = pre + '0'; return; }
    function step(ts){
      if (!t0) t0 = ts;
      var p = Math.min((ts - t0) / dur, 1), e = 1 - Math.pow(1 - p, 3);
      el.textContent = pre + Math.round(target * e).toLocaleString('en-US');
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  if ('IntersectionObserver' in window && !rm && !STATIC) {
    var io2 = new IntersectionObserver(function(es){
      es.forEach(function(e){ if (e.isIntersecting) { run(e.target); io2.unobserve(e.target); } });
    }, { threshold: .4 });
    nums.forEach(function(n){ io2.observe(n); });
  } else {
    nums.forEach(function(n){ n.textContent = (n.dataset.prefix || '') + (+n.dataset.count).toLocaleString('en-US'); });
  }

  /* nav shadow */
  var nav = document.querySelector('.nav');
  addEventListener('scroll', function(){
    if (window.scrollY > 24) nav.style.background = 'linear-gradient(180deg,rgba(4,6,12,.97),rgba(4,6,12,.8))';
    else nav.style.background = '';
  }, { passive: true });

  /* copy */
  document.querySelectorAll('.copy').forEach(function(b){
    b.addEventListener('click', function(){
      var txt = b.dataset.copy, old = b.textContent;
      var done = function(){ b.textContent = '已复制'; setTimeout(function(){ b.textContent = old; }, 1400); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(done, fallback);
      else fallback();
      function fallback(){
        var ta = document.createElement('textarea'); ta.value = txt; document.body.appendChild(ta);
        ta.select(); try { document.execCommand('copy'); done(); } catch(e) { b.textContent = txt; }
        document.body.removeChild(ta);
      }
    });
  });
})();
"""

NAV = f"""<header class="nav">
  <div class="nav-in">
    <a class="brand" href="#home">
      <img class="mark" src="{LOGO_URI}" alt="CabbageTimil 头像" width="34" height="34">
      <span>CabbageTimil<small>EVE ONLINE · EU PARTNER</small></span>
    </a>
    <nav class="nav-links">
      <a href="#about">关于</a>
      <a href="#works">精选</a>
      <a href="#series">合集</a>
      <a href="#timeline">时间线</a>
      <a href="#contact">关注</a>
    </nav>
    <a class="nav-cta" href="https://space.bilibili.com/{P['mid']}" target="_blank" rel="noopener">B 站主页 ↗</a>
  </div>
</header>"""

DOC = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CabbageTimil · EVE Online 欧服官方合作伙伴 | 新伊甸战地记录</title>
<meta name="description" content="CabbageTimil：EVE Online 官方合作伙伴，欧服华人视角的战地影像档案。{P['archive_count']} 部投稿，记录 WWW 世界大战、帝国北伐与 2003~2026 新伊甸全史。">
<meta name="theme-color" content="#04060c">
<meta property="og:type" content="profile">
<meta property="og:title" content="CabbageTimil · EVE Online 欧服合作伙伴">
<meta property="og:description" content="在七千个星系之间，做一个诚实的记录者。{P['archive_count']} 部投稿 / {vnum(P['fans'])} 位关注者。">
<meta property="og:image" content="{img(P['face'])}">
<link rel="icon" type="image/jpeg" href="{FAVICON_URI}">
<link rel="apple-touch-icon" href="{LOGO_URI}">
<link rel="preconnect" href="https://i0.hdslb.com" crossorigin>
<noscript><style>[data-reveal]{{opacity:1!important;transform:none!important}}</style></noscript>
<style>{CSS}</style>
</head>
<body>
<canvas id="stars" aria-hidden="true"></canvas>
{NAV}
<main>
{chr(10).join(body)}
</main>
<footer>
  <div class="foot">
    <span>© {datetime.datetime.now().year} CabbageTimil · New Eden Field Notes</span>
    <span>EVE Online is a trademark of CCP hf. 非官方粉丝页面。</span>
  </div>
</footer>
<script>{JS}</script>
</body>
</html>
"""

with open("CabbageTimil.html", "w", encoding="utf-8") as f:
    f.write(DOC)
print("wrote CabbageTimil.html", len(DOC), "bytes |", len(featured), "featured |", len(collections), "collections")
