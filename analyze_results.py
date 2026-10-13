"""
Spider 评测结果对比与错误分析

用法：
  python analyze_results.py baseline_results.jsonl full_results.jsonl lora_results.jsonl

约定：第 1 个文件是基线；第 2 个文件是你的主模型，它的错误样本会导出到 error_examples.md，
方便你逐条阅读。所有文件必须来自同一份 dev.json（脚本会检查）。
"""
import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

TYPES = ["simple", "join", "group_by", "order_by", "nested", "set_op"]


def load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8")]


def features(sql):
    """和 eval_spider_ex.py 的 sql_features 的区别：这里的 nested 不含集合操作。
    集合操作（INTERSECT/UNION/EXCEPT）天然有两个 SELECT，eval 脚本会把它们也算进 nested，造成两类重叠。"""
    s, f = sql.lower(), []
    has_set = any(k in s for k in (" intersect ", " union ", " except "))
    if " join " in s:
        f.append("join")
    if "group by" in s:
        f.append("group_by")
    if "order by" in s:
        f.append("order_by")
    if s.count("select") > 1 and not has_set:
        f.append("nested")
    if has_set:
        f.append("set_op")
    return f or ["simple"]


def error_category(r):
    """把每条失败样本归到一个类别里。"""
    if r["correct"]:
        return "correct"
    reason = r["reason"].lower()
    if reason.startswith("gold_error"):
        return "标准SQL执行失败（评测环境问题）"
    if reason.startswith("pred_error"):
        for key, name in [("no such column", "列名不存在"), ("no such table", "表名不存在"),
                          ("ambiguous", "列名有歧义"), ("syntax error", "语法错误"),
                          ("incomplete input", "SQL 不完整"), ("interrupted", "执行超时")]:
            if key in reason:
                return f"执行报错/{name}"
        return "执行报错/其他"
    # 能执行但结果不对：看预测 SQL 是否缺少标准 SQL 里有的结构
    g, p = set(features(r["gold"])), set(features(r["pred"]))
    missing = [t for t in TYPES[1:] if t in g and t not in p]
    return "结果错误/缺少结构: " + ",".join(missing) if missing else "结果错误/结构齐全，列或条件不对"


def acc(rows):
    return sum(r["correct"] for r in rows) / len(rows) if rows else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--examples", type=int, default=8, help="主模型每类错误导出多少条样本")
    args = ap.parse_args()

    names = [Path(f).stem.replace("_results", "") for f in args.files]
    results = [load(f) for f in args.files]
    n = len(results[0])
    for rs in results:
        assert len(rs) == n and all(a["gold"] == b["gold"] for a, b in zip(rs, results[0])), \
            "结果文件对不上：它们必须来自同一份 dev.json，并且样本数相同"

    # ---- 1. 分类型准确率表（可直接贴进 README）----
    idx_by_type = defaultdict(list)
    for i, r in enumerate(results[0]):
        for t in features(r["gold"]):
            idx_by_type[t].append(i)
    print("## 分类型执行准确率（类型会重叠，样本数之和大于总数）\n")
    print("| 类型 | 样本数 | " + " | ".join(names) + " |")
    print("|---|---|" + "---|" * len(names))
    print(f"| overall | {n} | " + " | ".join(f"{acc(rs):.2%}" for rs in results) + " |")
    for t in TYPES:
        ids = idx_by_type[t]
        print(f"| {t} | {len(ids)} | " + " | ".join(f"{acc([rs[i] for i in ids]):.2%}" for rs in results) + " |")
    for nm, rs in zip(names, results):
        p = acc(rs)
        print(f"\n{nm}: 总体 {p:.2%}，95% 置信区间约 ±{1.96 * math.sqrt(p * (1 - p) / n):.2%}"
              "（差异小于这个量级的对比不要过度解读）", end="")
    print("\n")

    # ---- 2. 失败原因分布 ----
    for nm, rs in zip(names, results):
        cats = Counter(error_category(r) for r in rs)
        print(f"## {nm}：失败原因分布（共 {n - cats['correct']} 条失败）")
        for c, k in cats.most_common():
            if c != "correct":
                print(f"  {k:4d}  ({k / n:.1%})  {c}")
        print()

    # ---- 3. 相对基线：修好了多少，又弄坏了多少 ----
    for nm, rs in list(zip(names, results))[1:]:
        fixed = sum((not a["correct"]) and b["correct"] for a, b in zip(results[0], rs))
        broken = sum(a["correct"] and (not b["correct"]) for a, b in zip(results[0], rs))
        print(f"## {nm} 相对 {names[0]}：修好 {fixed} 条，退化 {broken} 条（净增 {fixed - broken}）")
    if len(results) >= 3:
        a, b = results[1], results[2]
        both = sum(x["correct"] and y["correct"] for x, y in zip(a, b))
        only_a = sum(x["correct"] and not y["correct"] for x, y in zip(a, b))
        only_b = sum(y["correct"] and not x["correct"] for x, y in zip(a, b))
        print(f"\n## {names[1]} 对比 {names[2]}：都对 {both}，只有 {names[1]} 对 {only_a}，"
              f"只有 {names[2]} 对 {only_b}，都错 {n - both - only_a - only_b}")

    # ---- 4. 导出主模型的错误样本 ----
    if len(results) >= 2:
        by_cat = defaultdict(list)
        for r in results[1]:
            c = error_category(r)
            if c != "correct":
                by_cat[c].append(r)
        with open("error_examples.md", "w", encoding="utf-8") as f:
            f.write(f"# {names[1]} 的错误样本（每类最多 {args.examples} 条）\n\n")
            for c, rows in sorted(by_cat.items(), key=lambda x: -len(x[1])):
                f.write(f"## {c}（共 {len(rows)} 条）\n\n")
                for r in rows[:args.examples]:
                    f.write(f"- 问题: {r['question']}\n  - db: {r['db_id']}\n  - 标准: `{r['gold']}`\n"
                            f"  - 预测: `{r['pred']}`\n  - 原因: {r['reason']}\n\n")
        print(f"\n错误样本已导出到 error_examples.md（{names[1]}）")


if __name__ == "__main__":
    main()
