"""
Spider 执行准确率（Execution Accuracy, EX）评测脚本

思路：让模型生成 SQL -> 在真实 sqlite 数据库上执行预测 SQL 和标准 SQL -> 比较两者的执行结果。

用法示例：
  # 1) 基座模型零样本基线
  python eval_spider_ex.py --spider_dir ./data/spider
  # 2) LoRA 微调后（adapter 目录是 Trainer 保存的 checkpoint）
  python eval_spider_ex.py --spider_dir ./data/spider --adapter ./results/checkpoint-xxx
  # 3) 全量微调后（--model 指向保存的模型目录，分词器仍从原模型名加载）
  python eval_spider_ex.py --spider_dir ./data/spider --model ./results_full/final
  # 先用 --limit 20 小样本试跑，确认流程没问题
"""
import argparse
import json
import re
import sqlite3
import time
from collections import Counter, defaultdict
from pathlib import Path

BASE_MODEL = "/root/text2sql/model/Qwen2.5-1.5B-Instruct"


# ---------- 1. Prompt：必须和训练时的格式完全一致 ----------
def load_schemas(tables_json):
    return {t["db_id"]: t for t in json.load(open(tables_json, encoding="utf-8"))}


def get_schema(tables, db_id):
    t, cols = tables[db_id], {}
    for tid, name in t["column_names_original"]:
        if tid >= 0:
            cols.setdefault(t["table_names_original"][tid], []).append(name)
    return "\n".join(f"{tb}({', '.join(cs)})" for tb, cs in cols.items())


def build_prompt(schema, question):
    return f"数据库结构:\n{schema}\n问题: {question}\nSQL: "


# ---------- 2. 清洗模型输出 ----------
def clean_sql(text):
    """基座模型零样本时常带 ```sql 代码块或解释文字，只保留第一条 SQL。"""
    m = re.search(r"```(?:sql)?\s*(.*?)```", text, re.S | re.I)
    if m:
        text = m.group(1)
    text = re.split(r"\n\s*\n", text.strip())[0]  # 遇到空行就截断
    text = text.split(";")[0]                      # 只取第一条语句
    return " ".join(text.split())


# ---------- 3. 执行并比较 ----------
def run_sql(db_path, sql, timeout=10):
    conn = sqlite3.connect(str(db_path))
    conn.text_factory = lambda b: b.decode(errors="ignore")  # Spider 有非 UTF-8 的数据
    conn.execute("PRAGMA query_only = ON")                  # 只读，防止预测 SQL 改库
    start = time.time()
    # 每执行 10 万条虚拟机指令检查一次，超时就中断（防止死循环/笛卡尔积卡住）
    conn.set_progress_handler(lambda: 1 if time.time() - start > timeout else 0, 100000)
    try:
        return True, conn.execute(sql).fetchall()
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def is_correct(pred_sql, gold_sql, db_path):
    ok_g, gold = run_sql(db_path, gold_sql)
    if not ok_g:
        return False, f"gold_error: {gold}"
    ok_p, pred = run_sql(db_path, pred_sql)
    if not ok_p:
        return False, f"pred_error: {pred}"
    if "order by" in gold_sql.lower():      # 标准 SQL 有排序，行顺序必须一致
        same = pred == gold
    else:                                   # 否则忽略行顺序，只比较行的多重集合
        same = Counter(pred) == Counter(gold)
    return same, "ok" if same else "wrong_result"


def sql_features(sql):
    """给标准 SQL 打标签，用于按类型统计准确率（错误分析用）。"""
    s, f = sql.lower(), []
    if " join " in s:
        f.append("join")
    if "group by" in s:
        f.append("group_by")
    if "order by" in s:
        f.append("order_by")
    if s.count("select") > 1:
        f.append("nested")
    if any(k in s for k in (" intersect ", " union ", " except ")):
        f.append("set_op")
    return f or ["simple"]


# ---------- 4. 批量生成 ----------
def generate(model_name, tok_name, adapter, prompts, batch_size=16, max_new_tokens=256):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(tok_name)
    tok.padding_side = "left"          # 批量生成必须左填充，否则生成位置会错
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.bfloat16).to("cuda")
    if adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter)
    model.eval()

    outs = []
    for i in range(0, len(prompts), batch_size):
        enc = tok(prompts[i:i + batch_size], return_tensors="pt", padding=True).to("cuda")
        with torch.no_grad():
            gen = model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False,
                                 pad_token_id=tok.pad_token_id)
        outs += tok.batch_decode(gen[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
        print(f"generated {min(i + batch_size, len(prompts))}/{len(prompts)}", flush=True)
    return outs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spider_dir", required=True, help="官方 Spider 包目录，含 tables.json、dev.json 和 database/")
    ap.add_argument("--model", default=BASE_MODEL)
    ap.add_argument("--tokenizer", default=BASE_MODEL, help="分词器始终从基座模型目录加载")
    ap.add_argument("--adapter", default=None, help="LoRA 适配器目录（可选）")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", default="eval_results.jsonl")
    args = ap.parse_args()

    spider = Path(args.spider_dir)
    # 直接读官方 dev.json（1034 条），不依赖 Hugging Face 网络
    dev = json.load(open(spider / "dev.json", encoding="utf-8"))
    ds = [{"db_id": e["db_id"], "question": e["question"], "query": e["query"]} for e in dev]
    if args.limit:
        ds = ds[:args.limit]

    tables = load_schemas(spider / "tables.json")
    prompts = [build_prompt(get_schema(tables, ex["db_id"]), ex["question"]) for ex in ds]
    raw = generate(args.model, args.tokenizer, args.adapter, prompts)

    by_feature = defaultdict(lambda: [0, 0])  # 特征 -> [答对数, 总数]
    n_correct = 0
    with open(args.out, "w", encoding="utf-8") as f:
        for ex, r in zip(ds, raw):
            pred = clean_sql(r)
            db = spider / "database" / ex["db_id"] / f"{ex['db_id']}.sqlite"
            ok, reason = is_correct(pred, ex["query"], db)
            n_correct += ok
            for k in sql_features(ex["query"]):
                by_feature[k][0] += ok
                by_feature[k][1] += 1
            f.write(json.dumps({"db_id": ex["db_id"], "question": ex["question"], "gold": ex["query"],
                                "pred": pred, "raw": r, "correct": ok, "reason": reason},
                               ensure_ascii=False) + "\n")

    print(f"\nExecution Accuracy: {n_correct}/{len(ds)} = {n_correct / len(ds):.4f}")
    for k, (c, t) in sorted(by_feature.items()):
        print(f"  {k:10s} {c}/{t} = {c / t:.4f}")
    print(f"逐条结果已写入 {args.out}（可用于错误分析）")


if __name__ == "__main__":
    main()
