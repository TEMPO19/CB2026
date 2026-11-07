# 长白山摄影作品集

个人旅游摄影作品集网站。雪山夜景主题，极简风格，冷色系，中文黑体大标题 + 英文非衬线点缀排版。

封面标注抵达日期：2026 年 10 月 25 日（年 / 月 / 日三段式，以细线连接）。

纯静态站点，**无构建步骤**，可直接部署到 GitHub Pages。

---

## 单文件版本（离线可用）

`dist/changbai-single.html` —— 一个 HTML 文件，CSS / JS / 字体 / 全部 76 张图片都内联在里面，**双击即可离线打开**，不依赖任何外部资源。

重新构建：

```bash
python scripts/build_single_file.py
```

体积约 **21.8MB**（限制 25MB 内）。构建时做了四件事：

- 图片转 base64 内联，每张生成两级 webp（缩略 800px/q70 · 灯箱 1600px/q76）
- 字体只保留实际用到的 3 个字重（Inter 200/300/400）与 latin 子集，省 520KB
- 图片数据块放在文件末尾，浏览器先渲染页面骨架再解析图片
- 删除 `data-full` 死属性（JS 从未读取）

---

## 一分钟部署到 GitHub Pages

### 方式 A：GitHub Actions（推荐，已配好工作流）

仓库已内置 `.github/workflows/deploy.yml`，推送到 `main` 分支即自动发布。

```bash
# 1. 在 GitHub 新建仓库（名字自定，建议 Public）
# 2. 关联本地目录
cd 项目目录
git init
git add .
git commit -m "init: 长白山摄影作品集"
git branch -M main
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git push -u origin main

# 3. 打开仓库 Settings → Pages → Source 选 "GitHub Actions"
```

推送后 1–2 分钟，站点会在 `https://<你的用户名>.github.io/<仓库名>/` 上线。

### 方式 B：分支发布（不用 Actions）

Settings → Pages → Source 选 `main` 分支、根目录 `/ (root)`，保存即可。

> 仓库里的 `.nojekyll` 空文件会让 GitHub 跳过 Jekyll 处理，原样发布静态文件，避免它改动路径。

### 方式 C：拖拽上传（完全不想用命令行）

在 GitHub 仓库页面 → `Add file` → `Upload files`，把**部署清单**里的文件按原目录结构拖进去，Commit 即可。然后 Settings → Pages → Source 选 `main` / root。

---

## 部署清单

**必须上传**（网站运行所需，约 31MB）：

```
index.html
404.html
.nojekyll
css/style.css
js/main.js
assets/data.js
assets/favicon.png
assets/ink.png
assets/fonts/        (10 个 woff2，664KB)
assets/img/           (76 张 jpg + 76 张 webp，约 30MB)
```

**不需要上传**（已在 `.gitignore` 中排除）：

- `shots/` — 调试截图（73MB）
- `.backup/` — 原始素材备份（5.8MB）
- `scripts/` — 素材处理脚本（仅本地开发用，不影响站点运行）

---

## 自定义域名

在仓库根目录新建 `CNAME` 文件，内容写你的域名（不要写 `https://`）：

```
your-domain.com
```

提交后 GitHub Pages 会自动申请证书。CNAME 用**相对路径**的页面也能正常工作。

---

## 目录结构

```
index.html              # 页面结构（封面 / 目录 / 项目区 / 关于 / 灯箱）
404.html                # 404 页（GitHub Pages 自动挂载）
.nojekyll               # 跳过 Jekyll 处理
dist/
└── changbai-single.html # 单文件版（离线可用，CSS/JS/字体/图片全内联）
.github/workflows/
│   └── deploy.yml        # 自动部署工作流
css/
└── style.css             # 视觉系统与响应式布局
js/
└── main.js               # 项目渲染、滚动动画、灯箱、导航交互
assets/
├── data.js               # 图片清单（自动生成，勿手改）
├── manifest.json         # 图片元数据（自动生成）
├── fonts/                # 自托管 Inter 字体（5 字重 × latin/latin-ext）
├── favicon.png
├── ink.png               # 封面手写墨迹层（RGBA 透明）
└── img/                  # 76 张作品图（jpg 灯箱大图 + webp 网格缩略）
scripts/                  # 本地素材工具（不入库）
├── build_assets.py       # 下载 + 冷色调调色
├── import_*.py           # 导入本地实拍照片
├── compress_for_deploy.py    # 部署瘦身压缩
├── build_single_file.py  # 构建单文件 HTML
├── shoot.js              # 多端截图
└── verify.js             # 交互与响应式自检
```

---

## 五个项目

| 编号 | 项目 | 英文 | 张数 | 说明 |
|---|---|---|---|---|
| 01 | 天池 | Tianchi · Heaven Lake | 26 | 长白山北坡火山口湖，雪线、湖光与人像（风景与人像交错编排） |
| 02 | 恩都里 | Enduli · Manchu Heritage | 15 | 池北区满族文化主题商旅社区，剪纸、幡影与演艺空间 |
| 03 | 秋沙鸭公园 | Qiushaya Park · River Bend | 10 | 沿二道白河的国家一级保护动物栖息地，夜色、栈道与倒影 |
| 04 | 美人松 | Meirensong · Korean Pine | 15 | 长白松（长白山特有珍稀树种），红褐树干与金黄树冠 |
| 05 | 秋沙鸭河儿边 | Qiushaya Riverside | 10 | 二道白河河畔，落照、枯枝与夜色水面 |

---

## 设计规范

**配色**（冷色系）
- 背景：`#05080C` → `#0D141C` 深墨蓝
- 正文：`#E6EEF5`，次级 `#9FB3C4`，弱化 `#5E7488`
- 冰蓝点缀：`#BFD7E8` / `#7FA9C7` / `#3E6C8E`

**字体**
- 中文标题：黑体系（PingFang SC / SimHei / 微软雅黑），字重 700，字间距 `.06em`
- 英文点缀：Inter（自托管），字重 200–300，字间距 `.34em–.42em`，全大写

**动效**
- 封面入场：分阶延迟上浮（1.1s，`cubic-bezier(.22,1,.36,1)`）
- 封面视差：滚动位移 + 透明度衰减（`requestAnimationFrame` 节流）
- 网格进场：`IntersectionObserver` 触发，按序错峰 0.07s
- 图片悬停：缓慢放大 1.09× + 遮罩渐显 + 跟随放大镜
- 灯箱：缩放淡入 0.62s，切换交叉淡出
- 全站尊重 `prefers-reduced-motion`

---

## 交互

- 点击任意缩略图 → 灯箱放大；支持 `←` `→` 翻页、`Esc` 关闭、滚轮翻页、移动端左右滑动
- 灯箱底部缩略图条可直接跳转，顶部显示 `当前/总数`
- 顶部导航随滚动高亮当前项目，移动端切换为抽屉菜单
- 顶部细进度条反映滚动进度

---

## 响应式

| 断点 | 布局 |
|---|---|
| > 1100px | 3 列网格，宽幅跨 2 列，高幅跨 2 行 |
| ≤ 1100px | 2 列网格 |
| ≤ 860px | 单列，顶部导航折叠为抽屉 |
| ≤ 560px | 单列紧凑网格，图注常驻显示 |

已在 1440×900 / 820×1180 / 390×844 三档验证：无横向溢出、无控制台报错。

---

## 替换为自己的作品

1. 把照片放入 `assets/img/`，命名为 `{项目}-{序号}.jpg`（如 `tianchi-01.jpg`）
2. 跑对应的导入脚本更新清单：

```bash
python scripts/import_tianchi_mixed.py   # 天池（风景+人像打散）
python scripts/import_enduli.py          # 恩都里
python scripts/import_qiushaya.py        # 秋沙鸭公园
python scripts/import_meirensong.py      # 美人松
python scripts/import_hebian.py          # 秋沙鸭河儿边
```

3. `assets/data.js` 与 `assets/manifest.json` 会自动重新生成
4. 部署瘦身压缩（可选，图片超 1800px 的会压到 1700px / q82）：

```bash
python scripts/compress_for_deploy.py
```

---

## 本地预览

```bash
python -m http.server 8899
# 打开 http://127.0.0.1:8899/
```

部署前建议跑一遍交互自检：

```bash
node scripts/verify.js
```

---

## 其他托管平台

同一份文件可直接部署到 Netlify / Vercel / Cloudflare Pages，无需任何构建命令，构建目录填仓库根目录即可。

---

## 图片来源

作品照片为作者本人实拍（长白山天池、恩都里、秋沙鸭公园、美人松、二道白河畔）。
