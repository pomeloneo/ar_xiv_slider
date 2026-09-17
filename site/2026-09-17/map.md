# 从历史成绩到谨慎决策

_本篇完整方法关系图 · arXiv:2608.23416v2_

---

五个步骤组成同一篇论文的完整研究主线，不是分成五天的课程。[^1]
[详细讲解中的关系图](notes.html#overview)已支持直接渲染与缩放；这里保留可编辑文本。

```mermaid
flowchart TD
    accTitle: 从历史成绩到谨慎决策
    accDescr: 研究问题经过五个必要检查，最后连接作者的实验结果和方法边界。
    question["历史成绩好，未来就可靠吗？"] --> scope["第一步：规定看什么、相信什么"]
    scope --> capacity["第二步：别让规则比证据更复杂"]
    capacity --> evaluation["第三步：让坏日子变多，再检查"]
    evaluation --> search["第四步：把试错次数算进去"]
    search --> sizing["第五步：按不确定程度限制投入"]
    sizing --> evidence["核查：作者证明和实验支持什么"]
    evidence --> limits["边界：不等于保证盈利或覆盖新情况"]
```

这是教学整理图，不是论文原图。
修改时请同步独立的 [Mermaid 源码](map.mmd) 和笔记中的图。

[^1]: Jiayu Li. (2026). The Axiomatic Trader, v2. 五阶段及其适用条件见 https://arxiv.org/html/2608.23416v2#S10 ，证据与局限见附录 B 和第 13 节。
