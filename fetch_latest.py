# -*- coding: utf-8 -*-
"""Refresh latest.js with the channel's newest uploads.

Bilibili refuses to serve the space video-list API to browsers (412 / -799 on the
JSONP path), so the static page cannot pull the list itself. Instead this script
fetches it server-side and writes a tiny JS file the page loads on every refresh:

    window.__LATEST__ = {"updated": 1762..., "videos": [{bvid,title,pub,view,reply}, ...]}

Run it before deploying, from cron/Task Scheduler, or in a loop:

    python fetch_latest.py            # once
    python fetch_latest.py --loop 600 # every 10 minutes

If Bilibili is rate limiting us, the existing file is left untouched.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

MID = "279635057"
OUT = "latest.js"
COUNT = 5
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")
SPI = "https://api.bilibili.com/x/frontend/finger/spi"
LIST = ("https://api.bilibili.com/x/space/arc/search"
        "?mid={mid}&ps={count}&pn=1&order=pubdate")
VIEW = "https://api.bilibili.com/x/web-interface/view?bvid="
SEASON = ("https://api.bilibili.com/x/polymer/web-space/seasons_archives_list"
          "?mid={mid}&season_id={sid}&page_num=1&page_size={count}&sort_reverse=true")


def get_json(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def buvid_cookie():
    try:
        data = get_json(SPI, {"User-Agent": UA, "Referer": "https://www.bilibili.com/"})["data"]
        return f"buvid3={data['b_3']}; buvid4={data['b_4']}"
    except Exception:
        return ""


def fetch_uploads(count=COUNT):
    cookie = buvid_cookie()
    headers = {
        "User-Agent": UA,
        "Referer": f"https://space.bilibili.com/{MID}/video",
    }
    if cookie:
        headers["Cookie"] = cookie
    url = LIST.format(mid=MID, count=count)
    for attempt in range(1, 5):
        try:
            payload = get_json(url, headers)
        except urllib.error.HTTPError as exc:
            print(f"  http {exc.code} (attempt {attempt})")
            time.sleep(15 * attempt)
            continue
        code = payload.get("code")
        if code == 0:
            return payload["data"]["list"]["vlist"]
        print(f"  api {code} {payload.get('message')} (attempt {attempt})")
        if code not in (-799, -412, -352):
            return None
        time.sleep(20 * attempt)
    return None


def fetch_from_seasons(count=COUNT):
    """Fallback discovery: aggregate every 合集 the creator maintained.

    The space video-list API is rate limited / WAF'd most of the time, but the
    season endpoint keeps answering, and new uploads usually land in a 合集.
    """
    try:
        data = json.load(open("bili_data.json", encoding="utf-8"))
    except Exception:
        return []
    found = []
    headers = {"User-Agent": UA, "Referer": f"https://space.bilibili.com/{MID}"}
    for coll in data.get("collections", []):
        url = SEASON.format(mid=MID, sid=coll["id"], count=10)
        try:
            payload = get_json(url, headers)
        except Exception:
            continue
        if payload.get("code") != 0:
            continue
        for a in payload.get("data", {}).get("archives") or []:
            found.append({
                "bvid": a["bvid"],
                "title": a["title"],
                "pub": a.get("pubdate") or 0,
                "view": 0,
                "reply": 0,
            })
        time.sleep(0.3)
    found.sort(key=lambda v: -v["pub"])
    out, seen = [], set()
    for v in found:
        if v["bvid"] in seen:
            continue
        seen.add(v["bvid"])
        out.append(v)
        if len(out) >= count:
            break
    return out


def attachment(v):
    """Best-effort view/reply counts; the page can still refresh these itself."""
    try:
        stat = get_json(VIEW + v["bvid"], {"User-Agent": UA,
                                           "Referer": "https://www.bilibili.com/"})["data"]["stat"]
        return stat.get("view", 0), stat.get("reply", 0)
    except Exception:
        return 0, 0


def fallback():
    """Seed from bili_data.json so the file always exists and the page keeps working."""
    try:
        data = json.load(open("bili_data.json", encoding="utf-8"))
        latest = sorted(data["latest"], key=lambda v: -(v.get("pub") or 0))[:COUNT]
        return [{
            "bvid": v["bvid"], "title": v["title"], "pub": v.get("pub") or 0,
            "view": v.get("play") or 0, "reply": 0,
        } for v in latest]
    except Exception:
        return []


def write(videos):
    payload = {"updated": int(time.time()), "videos": videos}
    body = "window.__LATEST__ = " + json.dumps(payload, ensure_ascii=False) + ";\n"
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(body)
    print(f"wrote {OUT}: {len(videos)} videos")


def existing_newest():
    """Newest pub in the current latest.js, so we never downgrade it."""
    try:
        with open(OUT, encoding="utf-8") as fh:
            body = fh.read()
        start = body.index("{")
        payload = json.loads(body[start:body.rindex("}") + 1])
        return max([(v.get("pub") or 0) for v in payload.get("videos", [])] or [0])
    except Exception:
        return 0


def enrich(videos):
    for v in videos:
        view, reply = attachment(v)
        if view:
            v["view"] = view
        if reply:
            v["reply"] = reply
        time.sleep(0.35)
    return videos


def run_once():
    print("fetching newest uploads …")
    vlist = fetch_uploads()
    if vlist:
        videos = []
        for v in vlist[:COUNT]:
            view, reply = attachment(v)
            videos.append({
                "bvid": v["bvid"],
                "title": v["title"],
                "pub": v.get("created") or v.get("pubdate") or 0,
                "view": view or v.get("play") or 0,
                "reply": reply,
            })
            time.sleep(0.4)
        write(videos)
        return True

    print("space list unavailable; aggregating 合集 instead")
    videos = fetch_from_seasons()
    if videos:
        newest = max(v["pub"] for v in videos)
        if newest >= existing_newest():
            write(enrich(videos))
            return True
        print("  season data is not newer than the current latest.js")

    print("keeping the previous latest.js")
    if not os.path.exists(OUT):
        write(fallback())
    return False


def main():
    if "--loop" in sys.argv:
        try:
            every = int(sys.argv[sys.argv.index("--loop") + 1])
        except (IndexError, ValueError):
            every = 600
        while True:
            run_once()
            print(f"sleeping {every}s …")
            time.sleep(every)
    else:
        sys.exit(0 if run_once() else 1)


if __name__ == "__main__":
    main()
