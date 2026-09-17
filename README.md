# 每日 arXiv 论文带读

这个公开仓库保存每日 arXiv 学习包和 HTML 幻灯片，通过 GitHub Pages 发布静态网站。

站点入口：<https://pomeloneo.github.io/ar_xiv_slider/>。

仓库保持公开，以使用 GitHub Free 的 Pages 静态托管；学习材料和站点均可公开访问。
每篇学习包按日期存放在 `YYYY-MM-DD/`，由首页论文清单链接进入。

## 发布一天的学习包

每日学习材料先生成到本地目录，再运行：

```bash
python3 scripts/publish-day.py \
  --source /data00/home/limantang.neo/learning/arxiv-daily/YYYY-MM-DD \
  --date YYYY-MM-DD \
  --title "Paper title" \
  --arxiv-id "0000.00000v1" \
  --direction AI \
  --summary "一句话学习价值" \
  --slides slides.html
```

发布器会：

1. 将当天学习包中允许公开的 HTML、笔记、代码、图像等文件复制到 `site/YYYY-MM-DD/`，跳过隐藏文件、配置、日志及私有记录。
2. 生成当天入口页。
3. 幂等更新 `site/papers.json`；同日重跑先验证并暂存新材料，再替换当天内容，旧内容保留在仓库根目录的 `.publish-backup-*` 中。
4. 输出 HTML 幻灯片的 Pages 路径；实际发布仍取决于下方部署步骤。

发布器只接受包内规范相对路径的 HTML 课件，入口 `index.html` 为保留文件名。
具体文件扩展名白名单见 `scripts/publish-day.py` 的 `PUBLIC_EXTENSIONS`；JSON/JSONL 不会自动公开，依赖这些文件的 demo 应先改为内嵌公开数据，或审查后调整白名单。

检查变更无误后提交并推送：

```bash
git add site
git commit -m "Publish arXiv learning package for YYYY-MM-DD"
git push origin main
```

Pages 已启用，推送到 `main` 且包含站点文件变更时，会触发 GitHub Actions 将 `site/` 部署到 GitHub Pages。
必须检查部署成功及线上页面可访问，再发送课件链接。
