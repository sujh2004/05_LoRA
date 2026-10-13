import json
import torch
from datasets import Dataset, DatasetDict
from transformers import AutoTokenizer,AutoModelForCausalLM,Trainer,TrainingArguments
from transformers import DataCollatorForSeq2Seq
from peft import LoraConfig,TaskType,get_peft_model
def load_spider(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    data = [
        {
            "db_id": item["db_id"],
            "question": item["question"],
            "query": item["query"]
        }
        for item in data
    ]

    return Dataset.from_list(data)

dataset = DatasetDict({
    "train": load_spider("data/spider/train_spider.json"),
    "validation": load_spider("data/spider/dev.json")
})

lora_config = LoraConfig(
    task_type = TaskType.CAUSAL_LM,
    inference_mode = False,
    r = 16,
    lora_alpha=32,
    lora_dropout= 0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
)
model_name = "/root/text2sql/model/Qwen2.5-1.5B-Instruct"
output_dir = "./results_lora"
tokenizer = AutoTokenizer.from_pretrained(
    model_name,
    local_files_only=True
)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    dtype=torch.bfloat16,
    local_files_only=True
)
model.config.use_cache = False
model = get_peft_model(model,lora_config)
model.enable_input_require_grads()
model.print_trainable_parameters()

data_collator = DataCollatorForSeq2Seq(
    tokenizer = tokenizer,
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

tables = {t["db_id"] : t for t in json.load(open("data/spider/tables.json"))}

def get_schema(db_id):
    t, cols = tables[db_id],{}
    for tid , name in t["column_names_original"]:
        if tid >= 0:
            cols.setdefault(t["table_names_original"][tid],[]).append(name)
    return "\n".join(f"{tb}({', '.join(cs)})" for tb, cs in cols.items())


def tokenizer_function(example):
    prompt = f"数据库结构:\n{get_schema(example['db_id'])}\n问题: {example['question']}\nSQL: "
    p_ids = tokenizer(prompt)["input_ids"]
    a_ids = tokenizer(example["query"]+ tokenizer.eos_token)["input_ids"] 
    return {"input_ids":p_ids+a_ids,
            "attention_mask" : [1] * (len(p_ids)+len(a_ids)),
            "labels": [-100] * len(p_ids)+a_ids}


tokenized_dataset = dataset.map(tokenizer_function,remove_columns=dataset["train"].column_names)

lens = [len(x) for x in tokenized_dataset["train"]["input_ids"]]
print("最长样本 token 数:", max(lens), "| 最长的5个:", sorted(lens)[-5:])
MAX_LEN = 1536
tokenized_dataset["train"] = tokenized_dataset["train"].filter(lambda e: len(e["input_ids"]) <= MAX_LEN)

training_args = TrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size = 2,
    gradient_accumulation_steps=8,
    num_train_epochs = 3,
    learning_rate = 1e-4,
    bf16=True,
    gradient_checkpointing=False,
    optim="adamw_torch",        # 8bit 优化器，需要 pip install bitsandbytes
    logging_steps=20,
    save_strategy="epoch",
    save_total_limit=2,                  # 只保留最近 2 个 checkpoint，避免写满数据盘
)

trainer = Trainer(
    model = model,
    args = training_args,
    data_collator = data_collator,
    train_dataset = tokenized_dataset["train"]
)

trainer.train()

# 保存最终模型和分词器，评测时 --model 指向这个目录
trainer.save_model(f"{output_dir}/final")
tokenizer.save_pretrained(f"{output_dir}/final")