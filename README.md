# 每日 arXiv 论文带读

这个仓库通过 GitHub Pages 发布每日 arXiv 学习包和 HTML 幻灯片。

线上站点：<https://pomeloneo.github.io/ar_xiv_slider/>

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

1. 将当天学习包复制到 `site/YYYY-MM-DD/`。
2. 生成当天入口页。
3. 幂等更新 `site/papers.json`；同日重跑会替换当天内容。
4. 输出 HTML 幻灯片的 Pages 路径。

检查变更无误后提交并推送：

```bash
git add site
git commit -m "Publish arXiv learning package for YYYY-MM-DD"
git push origin main
```

推送到 `main` 后，GitHub Actions 会将 `site/` 部署到 GitHub Pages。
