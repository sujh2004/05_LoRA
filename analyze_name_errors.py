"""
名称类错误细分：把 "no such column / no such table" 按成因归类

用法：
  python analyze_name_errors.py full_results.jsonl --spider_dir ./data/spider

对每条这类失败，用 tables.json 里的真实 schema 核对模型写出的名字，判断它属于：
  - 列名在库里存在，但不在 SQL 用到的那张表里（跨表串列）
  - 命名写法不一致（大小写、下划线），例如 pet_type 对 PetType
  - 表名写得不完整，例如 cars 对 cars_data
  - 把列当成了表
  - 凭空编造的名字
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def load_schemas(tables_json):
    out = {}
    for t in json.load(open(tables_json, encoding="utf-8")):
        tables = t["table_names_original"]
        cols = defaultdict(list)
        for tid, name in t["column_names_original"]:
            if tid >= 0:
                cols[tables[tid]].append(name)
        out[t["db_id"]] = {"tables": tables, "columns": cols}
    return out


def classify(kind, name, schema):
    tables = schema["tables"]
    all_cols = [c for cs in schema["columns"].values() for c in cs]
    n = norm(name)
    if kind == "column":
        if name.lower() in {c.lower() for c in all_cols}:
            return "列名在库里存在，但不在 SQL 用到的那张表里（跨表串列）"
        if any(norm(c) == n for c in all_cols):
            return "命名写法不一致（大小写/下划线），如 pet_type 对 PetType"
        return "凭空编造的列名"
    if name.lower() in {c.lower() for c in all_cols}:
        return "把列当成了表"
    if any(norm(t) == n for t in tables):
        return "命名写法不一致（大小写/下划线）"
    if len(n) >= 3 and any(len(norm(t)) >= 3 and (n in norm(t) or norm(t) in n) for t in tables):
        return "表名写得不完整或近似，如 cars 对 cars_data"
    return "凭空编造的表名"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("result_file")
    ap.add_argument("--spider_dir", required=True)
    ap.add_argument("--show", type=int, default=3, help="每类显示几条例子")
    args = ap.parse_args()

    schemas = load_schemas(Path(args.spider_dir) / "tables.json")
    rows = [json.loads(l) for l in open(args.result_file, encoding="utf-8")]
    groups = defaultdict(list)
    for r in rows:
        m = re.search(r"no such (column|table): (.+)", r["reason"])
        if not m or r["correct"]:
            continue
        kind, name = m.group(1), m.group(2).strip().strip('"`\'[]')
        name = name.split(".")[-1]  # 去掉别名前缀，如 T2.Song_Name -> Song_Name
        groups[(kind, classify(kind, name, schemas[r["db_id"]]))].append((r, name))

    total = sum(len(v) for v in groups.values())
    print(f"共 {total} 条名称类失败（占全部 {len(rows)} 条里的 {total / len(rows):.1%}）\n")
    for kind, title in (("column", "列名不存在"), ("table", "表名不存在")):
        sub = {k: v for k, v in groups.items() if k[0] == kind}
        n_sub = sum(len(v) for v in sub.values())
        print(f"## {title}（{n_sub} 条）")
        for (_, cat), items in sorted(sub.items(), key=lambda x: -len(x[1])):
            dbs = Counter(r["db_id"] for r, _ in items).most_common(3)
            print(f"  {len(items):4d}  ({len(items) / n_sub:.0%})  {cat}    主要集中在: "
                  + ", ".join(f"{d}×{k}" for d, k in dbs))
            for r, name in items[:args.show]:
                print(f"        [{r['db_id']}] 模型写了 `{name}` | 问题: {r['question'][:70]}")
        print()
    print("提示：同一个数据库里相似的问题很多，一个系统性错误（如 pet_type）会被重复计数，"
          "上面最后一栏能帮你看出是不是少数几个库贡献了大部分错误。")


if __name__ == "__main__":
    main()
