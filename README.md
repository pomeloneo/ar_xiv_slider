# 每日 arXiv 论文带读

这个公开仓库保存每日 arXiv 学习包和 HTML 幻灯片，通过 GitHub Pages 发布静态网站。

站点入口：<https://pomeloneo.github.io/ar_xiv_slider/>。

仓库保持公开，以使用 GitHub Free 的 Pages 静态托管；学习材料和站点均可公开访问。
每篇学习包按日期存放在 `YYYY-MM-DD/`，由首页论文清单链接进入。

## 读者从哪里开始

打开当天的「本篇总览」，选择「图解全文」或「详细讲解」。
图解全文（Slider）是可翻页的完整讲解，详细讲解（阅读笔记）是同一篇论文的文章版，任选一种即可，不必重复读两遍。
学习包指这两种阅读形式，加上可选的算例、练习答案与图源码，不是第三篇必读材料。
每篇一次提供完整主线，不拆成几天，不以回答练习作为解锁条件。

首页和阅读页可手动切换「已读／未读」，首页可按阅读状态和标签组合筛选。
状态按去掉版本号的 arXiv ID 存在当前浏览器的 localStorage 中；刷新与同浏览器多标签页之间会保留、同步，换浏览器或清除站点数据不会保留。
打开文章不会自动标记已读，已读也不等于已经掌握。
存储不可用时页面会提示，并允许在当前页面暂存标记。

作者与每日任务需遵循 [内容与阅读体验规范](docs/AUTHORING.md)。

## 共享 Mermaid 图表

笔记和课件使用本地共享的 Mermaid 渲染脚本，无需运行时访问外部 CDN。
图表可以缩放，保留可编辑源码，加载失败时仍可阅读图注和正文。
页面接入格式见 [内容与阅读体验规范](docs/AUTHORING.md)。

修改渲染逻辑或依赖时，在仓库根目录运行：

```bash
npm ci
npm run build:mermaid
```

生成的 `site/assets/mermaid/` 和第三方许可证一同提交，各篇共享一次下载；不要手动编辑生成的脚本。
依赖版本由 `package.json` 和生成的 `package-lock.json` 固定。
需要在本地学习包中通过相同相对路径打开图表时，可额外提供明确的镜像目录：

```bash
npm run build:mermaid -- /path/to/arxiv-daily/assets/mermaid
```

构建语法目标为 Chrome 100 / Safari 15.4；实际渲染须在目标浏览器检查，语法目标不等于已在所有浏览器实测。

## 发布一天的学习包

每日学习材料先生成到本地目录，再运行：

```bash
python3 scripts/publish-day.py \
  --source /path/to/arxiv-daily/YYYY-MM-DD \
  --date YYYY-MM-DD \
  --title "Paper title" \
  --title-zh "论文中文标题" \
  --arxiv-id "0000.00000v1" \
  --direction AI \
  --tag "主题标签" \
  --tag "方法标签" \
  --summary "一句话学习价值" \
  --slides slides.html
```

发布器会：

1. 将当天学习包中允许公开的 HTML、笔记、代码、图像等文件复制到 `site/YYYY-MM-DD/`，跳过隐藏文件、配置、日志及私有记录。
2. 生成当天入口页，并在首页以中文译名为主标题、英文原题为辅助信息。
3. 幂等更新 `site/papers.json` 和支持标签筛选的静态首页；方向会自动成为第一个标签，`--tag` 可重复传入。
4. 输出 HTML 幻灯片的 Pages 路径；实际发布仍取决于下方部署步骤。

发布器只接受包内规范相对路径的 HTML 课件，入口 `index.html` 为保留文件名。
具体文件扩展名白名单见 `scripts/publish-day.py` 的 `PUBLIC_EXTENSIONS`；JSON/JSONL 不会自动公开，依赖这些文件的 demo 应先改为内嵌公开数据，或审查后调整白名单。
同日发布第二篇时必须传入唯一的 `--publication-key`，例如 `YYYY-MM-DD-0000.00000`；不传时默认为日期，同日重跑会原位更新，旧内容保留在仓库根目录的 `.publish-backup-*` 中。

检查变更无误后提交并推送：

```bash
git add site
git commit -m "Publish arXiv learning package for YYYY-MM-DD"
git push origin main
```

Pages 已启用，推送到 `main` 且包含站点文件变更时，会触发 GitHub Actions 将 `site/` 部署到 GitHub Pages。
必须检查部署成功及线上页面可访问，再发送课件链接。

## 批量学习包

`scripts/render-learning-package.py` 将逐篇审读后的 `content.json` 生成文章、完整课件和独立答案。
每篇内容同时保留 `demo.py`、真实运行输出和 Mermaid 源码；原始论文与检索日志留在本地，不随站点自动发布。
`scripts/prepare-batch.py` 核对预期篇数、去重、重跑每个 demo 并核对输出，再生成单篇入口与清单。
`scripts/finalize-batch.py` 在部署后逐文件比较线上与本地内容哈希，记录交付状态，并可通过已授权的 bot 发送本批目录。
收件人须通过命令参数传入，不保存在公开源码中。

基础检查使用 `python3 -m unittest discover -s tests -v`。
浏览器检查使用 `node scripts/verify-browser.mjs`；需要已有 Playwright 和 Chromium，可通过 `ARXIV_PLAYWRIGHT` 与 `ARXIV_CHROMIUM` 指定路径。
检查覆盖阅读状态持久化、跨标签页同步、标签组合筛选、存储失败降级、无 JavaScript 阅读、新课件翻页和 Mermaid 渲染。
