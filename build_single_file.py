#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
构建单文件 HTML —— 把 CSS / JS / 字体 / 图片全部内联进一个 .html

策略
----
- 图片：每个作品生成两级 webp（缩略 900px / 灯箱 1700px），base64 内联。
        单文件里图片只有一份数据，不再保留 jpg + webp 双份。
- 字体：只保留 latin 子集（页面无 latin-ext 区间字符），去掉 5 个 latin-ext 文件。
- CSS  ：内联进 <style>，url() 全部转 base64 data URI。
- JS   ：内联进 <script>，图片路径改为从 window.__IMGDATA__ 取。
- 产物：dist/changbai-single.html，双击即可离线打开。
"""
import base64
import io
import json
import os
import re
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "dist")
OUT_FILE = os.path.join(OUT_DIR, "changbai-single.html")

# 图片尺寸：缩略图（网格 / 目录 / 灯箱条）与大图（灯箱主体）
# 参数经逐张画质对比确定：1600/q76 与原 jpg 肉眼几乎无差异
THUMB_MAX, THUMB_Q = 800, 70
FULL_MAX, FULL_Q = 1600, 76

# 字体：页面实际只用到 Inter 的 200 / 300 / 400 三个字重
FONT_WEIGHTS = (200, 300, 400)


def b64(path, mime):
    with open(path, "rb") as f:
        return "data:%s;base64,%s" % (mime, base64.b64encode(f.read()).decode("ascii"))


def encode_webp(src, maxside, quality):
    """读取原图，按需缩放，输出 webp 字节"""
    im = Image.open(src)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    if max(im.size) > maxside:
        im = im.copy()
        im.thumbnail((maxside, maxside), Image.LANCZOS)
    else:
        im = im.copy()
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=quality, method=6)
    return buf.getvalue()


def build_image_map():
    """生成 {file: {thumb: dataURI, full: dataURI}} 及尺寸信息"""
    img_dir = os.path.join(ROOT, "assets", "img")
    files = sorted(f for f in os.listdir(img_dir) if f.lower().endswith(".jpg"))
    out = {}
    total = 0
    for i, fn in enumerate(files):
        key = os.path.splitext(fn)[0]
        src = os.path.join(img_dir, fn)
        tb = encode_webp(src, THUMB_MAX, THUMB_Q)
        fl = encode_webp(src, FULL_MAX, FULL_Q)
        total += len(tb) + len(fl)
        out[key] = {
            "thumb": "data:image/webp;base64," + base64.b64encode(tb).decode("ascii"),
            "full": "data:image/webp;base64," + base64.b64encode(fl).decode("ascii"),
        }
        if (i + 1) % 10 == 0:
            print("  图片 %d/%d" % (i + 1, len(files)))
    print("  原始图片字节: %.1f MB" % (total / 1024 / 1024))
    return out


def build_fonts_css():
    """生成内联字体 CSS：只保留 latin 子集 + 实际用到的字重"""
    fdir = os.path.join(ROOT, "assets", "fonts")
    css = []
    for weight in FONT_WEIGHTS:
        p = os.path.join(fdir, "inter-%d-latin.woff2" % weight)
        if not os.path.exists(p):
            continue
        css.append(
            "@font-face{font-family:'Inter';font-style:normal;font-weight:%d;font-display:swap;"
            "src:url(%s) format('woff2');"
            "unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,"
            "U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD;}"
            % (weight, b64(p, "font/woff2"))
        )
    return "\n".join(css)


def inline_css(css_text, imgs, hero_key):
    """把 CSS 里的 url() 替换为 data URI"""
    # 字体：原 path ../assets/fonts/xxx.woff2
    def font_repl(m):
        p = os.path.join(ROOT, "assets", "fonts", m.group(1))
        if os.path.exists(p):
            return "url(%s)" % b64(p, "font/woff2")
        return m.group(0)

    css_text = re.sub(r"url\(\.\./assets/fonts/([^)]+)\)", font_repl, css_text)
    # 英雄背景图
    css_text = re.sub(
        r"url\(\.\./assets/img/([\w-]+)\.jpg\)",
        lambda m: "url(%s)" % imgs[m.group(1)]["full"],
        css_text,
    )
    return css_text


def patch_js(js_text, imgs):
    """把 JS 里的图片路径改为查表"""
    # 缩略图引用
    js_text = js_text.replace(
        "src=\"assets/img/' + it.file + '.webp\"",
        "src=\"' + IMG(it.file, 'thumb') + '\"",
    )
    js_text = js_text.replace(
        "src=\"assets/img/' + thumb + '.webp\"",
        "src=\"' + IMG(thumb, 'thumb') + '\"",
    )
    # data-full 是死代码，直接去掉（灯箱走 LB.img.src）
    js_text = re.sub(r"\s*html \+= '\s+data-full=\"assets/img/' \+ it\.file \+ '\.jpg\" ';", "", js_text)
    # 灯箱主体
    js_text = js_text.replace(
        "LB.img.src = 'assets/img/' + f.item.file + '.jpg';",
        "LB.img.src = IMG(f.item.file, 'full');",
    )
    # 封面背景预载
    js_text = js_text.replace(
        "bgImg.src = 'assets/img/tianchi-16.jpg';",
        "bgImg.src = IMG('tianchi-16', 'full');",
    )
    # 注入 IMG 辅助函数
    helper = """
  /* ---------- 单文件模式：图片从内联数据表取 ---------- */
  function IMG(key, kind) {
    var m = window.__IMGDATA__;
    if (!m || !m[key]) return '';
    return m[key][kind === 'full' ? 'full' : 'thumb'];
  }
"""
    anchor = "  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };"
    if anchor in js_text:
        js_text = js_text.replace(anchor, anchor + "\n" + helper)
    else:
        raise SystemExit("找不到 JS 注入锚点")
    return js_text


def build():
    print("1/6 编码图片 ...")
    imgs = build_image_map()

    print("2/6 读取样式 ...")
    with open(os.path.join(ROOT, "css", "style.css"), encoding="utf-8") as f:
        css = f.read()
    css = inline_css(css, imgs, "tianchi-16")

    print("3/6 合并脚本 ...")
    with open(os.path.join(ROOT, "js", "main.js"), encoding="utf-8") as f:
        js = f.read()
    js = patch_js(js, imgs)
    with open(os.path.join(ROOT, "assets", "data.js"), encoding="utf-8") as f:
        data_js = f.read()

    print("4/6 组装 HTML ...")
    with open(os.path.join(ROOT, "index.html"), encoding="utf-8") as f:
        html = f.read()

    fonts_css = build_fonts_css()

    # CSS 链接 -> 内联
    html = html.replace('<link rel="stylesheet" href="css/style.css">',
                        "<style>\n%s\n%s\n</style>" % (fonts_css, css))

    # 墨迹 PNG -> data URI
    ink = os.path.join(ROOT, "assets", "ink.png")
    if os.path.exists(ink):
        html = html.replace('<img src="assets/ink.png" alt="">',
                            '<img src="%s" alt="">' % b64(ink, "image/png"))

    # favicon -> data URI
    fav = os.path.join(ROOT, "assets", "favicon.png")
    if os.path.exists(fav):
        html = html.replace('href="assets/favicon.png"', 'href="%s"' % b64(fav, "image/png"))

    # og:image 在单文件里无法用相对路径指向本地文件，也没法用 data URI
    # （多数社交平台不认 data URI），这里移除该行避免误导
    html = re.sub(r'<meta property="og:image"[^>]*>\n?', "", html)

    # 图片数据表放在 body 末尾 —— 浏览器解析完头部即可渲染页面骨架，
    # 十几 MB 的 base64 数据块在后面解析，首屏观感更好。
    imgdata = "<script>window.__IMGDATA__=" + json.dumps(imgs, ensure_ascii=False) + ";</script>"

    # 脚本链接 -> 内联（main.js 依赖 __IMGDATA__，但只在 DOMContentLoaded 后才用）
    html = html.replace('<script src="assets/data.js"></script>', "<script>\n%s</script>" % data_js)
    html = html.replace('<script src="js/main.js"></script>',
                        "<script>\n%s</script>\n%s" % (js, imgdata))

    print("5/6 写出文件 ...")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    size = os.path.getsize(OUT_FILE)
    print("6/6 完成")
    print("  ->", OUT_FILE)
    print("  体积: %.1f MB" % (size / 1024 / 1024))
    return OUT_FILE


if __name__ == "__main__":
    build()
