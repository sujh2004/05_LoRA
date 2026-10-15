# Text-to-SQL：Qwen2.5-1.5B 在 Spider 上的全量微调与 LoRA 对比

在 Spider 开发集上，Qwen2.5-1.5B-Instruct 的执行准确率（Execution Accuracy）从零样本的 **31.5%** 提升到全量微调后的 **69.9%**。项目对比了全量微调和两种 LoRA 配置，并对失败样本做了分类分析。

## 主要结果

Spider 开发集（1034 条，跨数据库），执行准确率：

| 类型               | 样本数 | 基线（零样本） | LoRA（仅 attention） | LoRA（全部线性层） | 全量微调   |
| ------------------ | ------ | -------------- | -------------------- | ------------------ | ---------- |
| **总体**           | 1034   | 31.53%         | 57.06%               | 66.83%             | **69.92%** |
| simple             | 333    | 42.34%         | 69.07%               | 82.28%             | 82.88%     |
| join               | 408    | 27.21%         | 44.36%               | 50.49%             | 57.11%     |
| group_by           | 277    | 34.66%         | 56.32%               | 67.51%             | 68.95%     |
| order_by           | 237    | 27.85%         | 54.01%               | 63.29%             | 68.78%     |
| nested（子查询）   | 79     | 12.66%         | 37.97%               | 49.37%             | 48.10%     |
| set_op（集合操作） | 80     | 6.25%          | 42.50%               | 52.50%             | 51.25%     |

说明：类型之间会重叠（一条 SQL 可以同时含 join 和 group_by），样本数之和大于 1034；nested 不含集合操作。总体 95% 置信区间约 ±2.8 到 ±3.0 个百分点。

要点：

- 微调使总体执行准确率提升约 38 个百分点，远超统计噪声。提升最大的是子查询和集合操作，基线在这两类上几乎答不对。
- LoRA 的配置影响很大：把目标层从仅 attention 扩展到全部线性层，并把学习率从 1e-4 调到 2e-4，总体提升约 9.5 个百分点。
- LoRA（全部线性层）与全量微调相差 2.8 个百分点。在同一批题目上做配对检验，差异显著，但每组只训练了一次，该检验不包含训练随机性。
- 评测指标是自行实现的执行准确率，不是官方 test-suite 评测，**不能与 Spider 排行榜上的数字直接比较**。

## 任务与数据

- 任务：给定数据库结构和自然语言问题，生成 SQL。
- 数据：[Spider](https://huggingface.co/datasets/xlangai/spider)。训练集用 `train_spider.json`（7000 条），评测集用 `dev.json`（1034 条）。Spider 的训练库和开发库互不重叠，评测的是跨库泛化。训练时过滤了超过 1536 token 的样本，过滤后剩 7000 条。
- 基座模型：Qwen2.5-1.5B-Instruct。

## 方法

### Prompt 与训练目标

数据库结构取自 `tables.json` 的原始表名和列名，格式如下：

```
数据库结构:
singer(Singer_ID, Name, Country, Song_Name, Song_release_year, Age, Is_male)
concert(concert_ID, concert_Name, Theme, Stadium_ID, Year)
问题: How many singers do we have?
SQL: 
```

训练时问题部分的 label 设为 -100，只对 SQL 和结束符计算损失。训练和评测使用完全相同的 prompt 格式。prompt 中不含外键、列类型和样本值。

### 训练配置

|                        | 全量微调                    | LoRA（仅 attention）      | LoRA（全部线性层）       |
| ---------------------- | --------------------------- | ------------------------- | ------------------------ |
| 脚本                   | `main.py`                   | `train_lora.py`           | `train_lora_all.py`      |
| 训练的模块             | 全部参数                    | q/k/v/o                   | q/k/v/o/gate/up/down     |
| LoRA 参数              | –                           | r=16, α=32, dropout=0.05  | r=16, α=32, dropout=0.05 |
| 可训练参数占比         | 100%                        | 0.28%                  | 1.18%                 |
| 学习率                 | 1e-5                        | 1e-4                      | 2e-4                     |
| 等效 batch size        | 16（1×16）                  | 16（2×8）                 | 16（2×8）                |
| epoch                  | 3                           | 3                         | 3                        |
| 精度                   | fp32 权重 + bf16 混合精度   | bf16 权重 + bf16 混合精度 | 同左                     |
| 优化器                 | 8-bit AdamW（bitsandbytes） | AdamW                     | AdamW                    |
| gradient checkpointing | 开                          | 关                        | 关                       |

三组共同设置：最大序列长度 1536，学习率调度使用 Trainer 默认（线性衰减、无 warmup），每组只训练一次（单随机种子）。硬件：RTX 3090（24GB）。

## 评测方法

- **指标**：执行准确率。让模型生成 SQL，在对应的 sqlite 数据库上分别执行预测 SQL 和标准 SQL，比较结果。
- **结果比较**：标准 SQL 含 `ORDER BY` 时，行顺序必须一致；否则忽略行顺序，按行的多重集合比较。只要存在某种列的排列使结果一致就判对；多选或少选列仍判错。
- **生成**：贪心解码，最多生成 256 个 token，bf16 推理。输出会清洗：去掉 ````sql` 代码块和解释文字，只保留第一条语句。
- **安全**：数据库以只读方式打开，单条 SQL 执行超时 10 秒。

### 评测的局限

- 只比较在这一个数据库实例上的执行结果。两条语义不同的 SQL 可能碰巧结果相同（误判为对），而多选一列或列顺序不同会被判错（误判为错）。官方 test-suite 评测通过构造多个数据库来缓解这一问题，本项目没有使用。
- Spider 本身存在问句歧义和少量标注问题（见下文），这会压低所有系统的得分。
- 开发集同时用于选择 LoRA 配置和报告结果：第二组 LoRA 配置是看到第一组结果后调整的，因此对 LoRA（全部线性层）的结果存在轻微的乐观偏差。Spider 的测试集不公开，没有独立的测试集可用。

## 结果分析

### 1. 微调改变了什么

|                      | 失败总数 | 执行报错 | 其中语法错误 | 其中表/列名不存在 | 结果错误（能执行但结果不对） |
| -------------------- | -------- | -------- | ------------ | ----------------- | ---------------------------- |
| 基线                 | 708      | 405      | 71           | 316               | 303                          |
| LoRA（仅 attention） | 444      | 216      | 1            | 208               | 228                          |
| LoRA（全部线性层）   | 343      | 156      | 1            | 152               | 187                          |
| 全量微调             | 311      | 156      | 4            | 140               | 155                          |

- 基线有 71 条语法错误，微调后降到个位数，说明基线的失败里有一部分是输出格式问题，微调的一部分收益来自"学会了输出格式"。
- 微调后表/列名不存在仍是最大的单项失败来源：全量微调的 311 条失败中占 140 条（45%）。

### 2. 名称类错误（全量微调，140 条）

用 `analyze_name_errors.py` 把全量微调的 140 条"表/列名不存在"按成因归类（用 `tables.json` 核对模型写出的名字）：

| 成因                                                         | 列名 | 表名 | 合计 | 占比  |
| ------------------------------------------------------------ | ---- | ---- | ---- | ----- |
| 名字在库里存在，但不在 SQL 用到的那张表里（跨表串列）        | 84   | –    | 84   | 60.0% |
| 无法匹配到库里任何名字（编造、缩写或同义改写、把取值当列名） | 29   | 10   | 39   | 27.9% |
| 命名写法不一致（大小写、下划线）                             | 13   | 0    | 13   | 9.3%  |
| 表名写得不完整或近似                                         | –    | 2    | 2    | 1.4%  |
| 把列当成了表                                                 | –    | 2    | 2    | 1.4%  |

- **跨表串列是最大的来源**：84 条里 car_1 占 34 条，其次是 world_1（10）和 dog_kennels（9）。这类错误出在多表 JOIN 加别名之后，例如 `T2.Song_Name` 的 T2 实际是 `singer_in_concert`，而该列属于 `singer`。
- **命名写法不一致全部集中在 pets_1**：真实列名是 `PetType`，模型写成 `pet_type`（13 条）。该库的 `Pets` 表里 `PetType` 和 `pet_age` 两种风格混用。
- **"无法匹配"类**包含缩写和同义改写（如 `HP` 对 `Horsepower`，`tournament_name` 对 `tourney_name`）、把取值当成列名（如 `UnitedAirlines`），以及凭空编造的表（如 concert_singer 里歌曲信息其实是 `singer` 表的列，模型却写出了不存在的 `song` 表）。这类的细分是我对例子的归纳，没有逐条人工核对。
- 这些分类由脚本按名字匹配自动完成，"跨表串列"没有进一步区分是别名绑定错误还是漏写了 JOIN。

### 失败集中在少数数据库

全量微调的 311 条失败里，world_1（69/120）和 car_1（53/92）这两个库共贡献了 122 条，占失败总数的 39.2%，而它们只占全部题目的 20.5%。失败最多的 5 个库（world_1、car_1、dog_kennels、student_transcripts_tracking、wta_1）贡献了 66.6% 的失败，题目占比为 42.0%。world_1 和 car_1 的准确率都在 42.5% 左右。总体准确率主要被少数几个难库拉低，同一个库里相似的问题多，一个系统性错误会被重复计数。

### 3.错误类型举例

| 类别                        | 说明                                                         |
| --------------------------- | ------------------------------------------------------------ |
| A. 问句歧义或合理的替代写法 | 例如"for every concert"既可按 id 也可按 name 分组            |
| B. 标准答案本身有问题       | 例如问题只问 first name，标准 SQL 却返回了 fname 和 age      |
| C. schema linking 错误      | 表/列选错、命名错误、凭空编造                                |
| D. 取值和字面量错误         | 例如大小写、编造的编码值                                     |
| E. 结构或语义错误           | 例如漏掉 DISTINCT、用 EXCEPT 代替 NOT IN 导致语义不同、join 键选错 |

读样本时发现的具体例子：

- **问句歧义**：问 "What is the maximum capacity and the average of all stadiums?"，标准答案取的是表里名为 `Average` 的列，而 `avg(capacity)` 也是合理的读法。
- **字面量大小写**：模型写 `pettype = "Cat"`，库里的值是 `'cat'`。SQLite 的 `=` 区分大小写，所以匹配不到任何行。同一个错误在多个问题里重复出现，说明模型不知道库里的真实取值。
- **漏掉 DISTINCT**：同时养猫和狗的学生会在结果里出现两次。
- **用 EXCEPT 代替 NOT IN**：`EXCEPT` 按值去重，会把共享同一个值的行一起去掉，语义和按 id 过滤的 `NOT IN` 不同。

### 4. LoRA 与全量微调的对比

- 配置影响大：仅 attention 的 LoRA 低于全量微调 12.3 个百分点；扩展到全部线性层并提高学习率后，差距缩小到 2.8 个百分点。
- 在 simple、nested、set_op 三类上，LoRA（全部线性层）与全量微调的差距在 1.3 个百分点以内；差距主要集中在 join（差 6.1）和 order_by（差 5.5）。
- 配对比较：624 条两者都对，只有全量微调答对 99 条，只有 LoRA（全部线性层）答对 67 条，两者都错 244 条。配对检验 z=(99−70)/√166≈2.48， p≈0.013：在这批题目上，全量微调略好于 LoRA（全部线性层）。该检验只反映评测集的抽样噪声，不包含训练随机性；每组只训练了一次，所以这个差距在重复训练下是否稳定，本项目没有验证。
- 以上均为单次训练的结果，且两处改动同时发生，不能把提升归因于某一个因素。

## 局限与后续方向

以下方向**尚未验证**，仅作为后续工作：

- 在 prompt 中加入外键、列类型和每列的样本值，缓解 join 键错误和字面量错误。
- 执行反馈重试：遇到 `no such column` 时，把报错信息和 schema 再交给模型重新生成一次。
- 对未知标识符做名称吸附（忽略大小写和下划线，匹配到真实的表/列名）。这属于系统流水线的后处理，与模型本身的提升应分开报告。
- 使用官方 test-suite 评测，并用多个随机种子重复实验。

## 复现

```bash
# 1. 准备数据和模型
#    Spider 官方包解压到 data/spider/（含 tables.json、train_spider.json、dev.json、database/）
#    Qwen2.5-1.5B-Instruct 下载到 model/
#    脚本里的模型路径（BASE_MODEL / model_name）需要按你的环境修改

# 2. 基线评测
python eval_spider_ex.py --spider_dir ./data/spider --out results/baseline_results.jsonl

# 3. 全量微调 + 评测
python main.py
python eval_spider_ex.py --spider_dir ./data/spider --model ./results_full/final --out results/full_results.jsonl

# 4. LoRA（仅 attention）+ 评测
python train_lora.py
python eval_spider_ex.py --spider_dir ./data/spider --adapter ./results_lora/final --out results/lora_results.jsonl

# 5. LoRA（全部线性层）+ 评测
python train_lora_all.py
python eval_spider_ex.py --spider_dir ./data/spider --adapter ./results_lora_all/final --out results/lora_all_results.jsonl

# 6. 对比与错误分析
python analyze_results.py results/baseline_results.jsonl results/full_results.jsonl results/lora_all_results.jsonl results/lora_results.jsonl
python analyze_name_errors.py results/full_results.jsonl --spider_dir ./data/spider
```

## 仓库结构

```
.
├── main.py                  # 全量微调
├── train_lora.py            # LoRA（仅 attention）
├── train_lora_all.py        # LoRA（全部线性层），与上一个文件只有目标层、学习率、输出目录不同
├── eval_spider_ex.py        # 执行准确率评测
├── analyze_results.py       # 结果对比与错误分析
├── analyze_name_errors.py   # 名称类错误细分
└── results/                 # 各组的逐条评测结果（jsonl）
```

数据集、基座模型权重和训练产生的 checkpoint 不放进仓库。

## 引用

- Yu et al., *Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task*, EMNLP 2018.
- Qwen Team, *Qwen2.5 Technical Report*, 2024.