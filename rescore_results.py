"""
用"忽略列顺序"的口径，重新给已有的评测结果打分（不需要 GPU，不需要重新生成 SQL）

背景：eval_spider_ex.py 比较执行结果时要求列的顺序一致。但问题里先说 "opening year and staff number"，
预测先写 open_year 再写 num_of_staff，而标准答案写的是反过来的顺序，这种预测会被判错，
但返回的数据其实完全相同。官方 test-suite 评测会考虑列的排列，本脚本参考这个思路：
只要存在某种列的排列，使预测结果与标准结果的行（或带顺序的行）完全一致，就判对。

用法（需要 Spider 的 database/ 文件夹，所以在服务器上跑）：
  python rescore_results.py results/baseline_results.jsonl results/full_results.jsonl \
      results/lora_all_results.jsonl results/lora_results.jsonl --spider_dir ./data/spider

输出：
  - 每个文件旁边生成 xxx_lenient_results.jsonl，格式与原文件相同（correct 已按宽松口径更新），
    可以直接喂给 analyze_results.py 做分类型对比、失败分析和配对检验
  - 屏幕上打印严格口径与宽松口径的对比
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from eval_spider_ex import run_sql, sql_features

MAX_TRIES = 5000  # 列的排列组合上限，防止列很多时爆炸


def rows_equal_ignoring_col_order(pred, gold, order_matters):
    if len(pred) != len(gold):
        return False
    if not gold:
        return True
    n = len(gold[0])
    if len(pred[0]) != n:
        return False
    # 预测的第 i 列只可能对应"取值多重集合相同"的标准列，先剪枝
    pcols = [Counter(r[i] for r in pred) for i in range(n)]
    gcols = [Counter(r[j] for r in gold) for j in range(n)]
    cands = [[j for j in range(n) if gcols[j] == pcols[i]] for i in range(n)]
    if any(not c for c in cands):
        return False

    tries = 0

    def search(i, used, mapping):
        nonlocal tries
        if tries >= MAX_TRIES:
            return False
        if i == n:
            tries += 1
            inv = [0] * n
            for p, j in enumerate(mapping):
                inv[j] = p
            reordered = [tuple(row[inv[j]] for j in range(n)) for row in pred]
            return reordered == gold if order_matters else Counter(reordered) == Counter(gold)
        for j in cands[i]:
            if j not in used and search(i + 1, used | {j}, mapping + [j]):
                return True
        return False

    return search(0, frozenset(), [])


def is_correct_lenient(pred_sql, gold_sql, db_path):
    ok_g, gold = run_sql(db_path, gold_sql)
    if not ok_g:
        return False
    ok_p, pred = run_sql(db_path, pred_sql)
    if not ok_p:
        return False
    return rows_equal_ignoring_col_order(pred, gold, "order by" in gold_sql.lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--spider_dir", required=True)
    ap.add_argument("--show", type=int, default=3, help="每个文件打印几条被改判为正确的例子")
    args = ap.parse_args()
    spider = Path(args.spider_dir)

    summary = []
    for f in args.files:
        rows = [json.loads(l) for l in open(f, encoding="utf-8")]
        flipped = []
        for r in rows:
            r["correct_strict"] = r["correct"]
            if not r["correct"] and r["reason"] == "wrong_result":  # 只有"能执行但结果不对"的才可能被改判
                db = spider / "database" / r["db_id"] / f"{r['db_id']}.sqlite"
                if is_correct_lenient(r["pred"], r["gold"], db):
                    r["correct"], r["reason"] = True, "ok_lenient"
                    flipped.append(r)
        out = Path(f).with_name(Path(f).stem.replace("_results", "") + "_lenient_results.jsonl")
        with open(out, "w", encoding="utf-8") as fo:
            for r in rows:
                fo.write(json.dumps(r, ensure_ascii=False) + "\n")

        n = len(rows)
        strict = sum(r["correct_strict"] for r in rows)
        lenient = sum(r["correct"] for r in rows)
        assert all(r["correct"] for r in rows if r["correct_strict"]), "宽松口径不应把原本判对的改成错"
        summary.append((Path(f).stem, n, strict, lenient))
        print(f"\n## {Path(f).name}：严格 {strict}/{n} = {strict / n:.2%}  ->  宽松 {lenient}/{n} = {lenient / n:.2%}"
              f"（改判为正确 {len(flipped)} 条）  已写入 {out.name}")
        for r in flipped[:args.show]:
            print(f"   例: {r['question'][:70]}\n       标准: {r['gold'][:110]}\n       预测: {r['pred'][:110]}")

    print("\n## 汇总")
    print("| 文件 | 严格 | 宽松 | 差值（个百分点） |\n|---|---|---|---|")
    for name, n, s, l in summary:
        print(f"| {name} | {s / n:.2%} | {l / n:.2%} | {(l - s) / n * 100:+.1f} |")
    print("\n下一步：python analyze_results.py <各文件对应的 *_lenient_results.jsonl>，"
          "用宽松口径重做分类型对比和配对检验。")


if __name__ == "__main__":
    main()
