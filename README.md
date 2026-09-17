# 每日 arXiv 论文带读

这个私有仓库保存每日 arXiv 学习包和 HTML 幻灯片，并已配置 GitHub Pages 发布工作流。

预定站点地址：<https://pomeloneo.github.io/ar_xiv_slider/>（尚未上线）。

2026-09-17 实测：仓库已设为 private，但创建 Pages 时 GitHub 返回 HTTP 422：`Your current plan does not support GitHub Pages for this repository.`。
免费私有仓库与私有仓库 Pages 是不同的功能，后者在个人账户下需要 GitHub Pro；参见 [GitHub Pages 官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)。
保留仓库私有设置，等待解决 Pages 套餐限制或选定其他托管方式后再进行线上交付。
仓库私有不代表 Pages 网站私有，发布的学习材料默认仍可公开访问。

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

Pages 启用后，推送到 `main` 会触发 GitHub Actions 将 `site/` 部署到 GitHub Pages。
必须检查部署成功及线上页面可访问，再发送课件链接。
