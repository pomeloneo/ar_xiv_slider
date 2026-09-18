import re

cases = {
    "证书案例": [
        "网站 503 无法访问",
        "DNS 正常 TLS 握手 证书链 错误",
        "更新 中间证书 重启 网关 恢复",
    ],
    "磁盘案例": [
        "网站 503 无法访问",
        "日志 写入失败 磁盘 已满",
        "清理 磁盘 扩容 恢复",
    ],
    "数据库案例": [
        "接口 超时",
        "数据库 连接池 耗尽",
        "调低 超时 修复 连接泄漏",
    ],
}
query = "DNS 正常 TLS 握手 证书链 错误"

def words(text):
    return set(re.findall(r"[\w\u4e00-\u9fff]+", text.lower()))

def score(left, right):
    return len(words(left) & words(right))

whole = sorted(
    ((score(query, " ".join(entries)), name) for name, entries in cases.items()),
    reverse=True,
)
entries = sorted(
    ((score(query, entry), name, index, entry)
     for name, timeline in cases.items()
     for index, entry in enumerate(timeline)),
    reverse=True,
)
best = entries[0]
print("整案重叠排名：" + " > ".join(f"{name}({value})" for value, name in whole))
print(f"入口命中：{best[1]} 第{best[2] + 1}阶段，得分 {best[0]}：{best[3]}")
print("锚定后续：" + " → ".join(cases[best[1]][best[2]:]))
assert best[1] == "证书案例" and best[2] == 1
print("边界：这是精确词集合教学检索；同义词、抽取错误、权限和真实解决效果均未验证。")
