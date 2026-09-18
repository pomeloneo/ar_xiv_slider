groups = {
    "先进": {"corr": 0.48, "path": [0.0, -1.0, -0.3, 0.4, 0.1, 0.0], "share_h1": 7.64},
    "高收入新兴": {"corr": 0.35, "path": [0.2, -1.2, 0.5, 1.0, 0.4, -0.1], "share_h1": 1.99},
    "中等收入新兴": {"corr": 0.18, "path": [-0.1, -0.8, 0.3, 0.7, 0.1, -0.2], "share_h1": 0.77},
    "低收入新兴": {"corr": 0.02, "path": [0.1, 0.1, 0.0, -0.4, -0.6, -0.7], "share_h1": 0.02},
}
for name, item in groups.items():
    first_negative = next((i for i, value in enumerate(item["path"]) if value < 0), None)
    rebuild = any(value > 0 for value in item["path"][first_negative + 1:]) if first_negative is not None else False
    print(f"{name}：产出相关={item['corr']:.2f}，首次去库=h{first_negative}，后续补库={rebuild}，h1份额={item['share_h1']:.2f}%")
assert next(i for i, x in enumerate(groups["低收入新兴"]["path"]) if x < 0) == 3
print("边界：响应值是为展示路径而缩放的示意数；相关系数与方差份额来自论文概括，未重估原始面板。")
