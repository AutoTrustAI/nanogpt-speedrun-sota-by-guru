# ForgeMatch · 铸忆

**ScienceGuru + Guru Turbo 1.2 · 8×H100 上，五个 seed 平均 24.8998 秒。**

[English](README.md) · [复现指南](docs/REPRODUCE.md) · [策略说明](docs/STRATEGY.md) · [证据说明](docs/EVIDENCE.md) · [实验室 baseline](docs/BASELINES.md) · [规则与边界](docs/COMPLIANCE.md)

**ForgeMatch** 是面向 NanoGPT Speedrun 的快速语言模型训练方案。它利用训练语料的因果前缀检索、稀疏 n-gram embedding、FP8 计算和紧凑训练日程提高训练效率，并通过 CPU 绑核、异步预取与协调内存管理减少 GPU 等待和时间波动。

## 已核验成绩

由 **ScienceGuru + Guru Turbo 1.2** 跑出的 652 步方案，采用固定五个 seed，完整验证集 **10,485,760 tokens**，全词表概率计算。五次完整运行的最终 loss 均低于 **3.28**。

| Seed | 最终训练计时（秒） | 验证 loss |
|---:|---:|---:|
| 42 | 24.908 | 3.2733 |
| 43 | 24.898 | 3.2777 |
| 44 | 24.868 | 3.2752 |
| 45 | 24.939 | 3.2732 |
| 46 | 24.886 | 3.2755 |
| **平均** | **24.8998** | **3.27498** |

- 时间极差 **0.071 秒**，样本标准差 **0.026499 秒**。
- 最差 loss **3.2777**；相对 3.28 门槛的单侧 t 检验 **p≈0.001868**，自由度 4。
- 运行顺序固定为 **43→42→44→45→46**；没有剔除慢样本、替换 seed，或混入旧版本成绩。
- 本次五 seed 达到本地目标：平均 ≤25 秒、极差 ≤5 秒、每次 loss≤3.28。

成绩采用最终 validation 行的 `train_time`，**不是进程启动到退出的墙钟时间**。编译、预热和最终模型验证不计时；训练内容的读取、建库、查询与必要收尾仍在计时内。空内存分配、prefault、线程准备及验证文件 header 读取发生在计时前，详见[计时边界](docs/COMPLIANCE.md#timing-boundary)。

这是证据已核验的本地实验结果，**尚非官方认可的世界纪录**。开发期间反复使用了固定 seed；上述 p 值不能消除自适应调参带来的统计局限。完整结果见[机器可读记录](results/cohorts.json)及[证据说明](docs/EVIDENCE.md)。

## 与公开方案比较

| 策略 | 公开平均耗时 | 平均 loss | 次数 | ForgeMatch 耗时降幅 |
|---|---:|---:|---:|---:|
| [ANVIL2](https://github.com/KellerJordan/modded-nanogpt/pull/360) | 39.914 秒 | 3.277311 | 18 | **37.62% / 1.603× 加速** |
| [Exact-match](https://github.com/hermabr/modded-nanogpt-public/blob/3e92b0e28293dcb184197da1a0ce1f543e84f76c/records/track_1_short/2026-09-16_ExactMatch/this_pr/statistics.md) | 47.2056 秒 | 3.26556 | 5 | **47.25% / 1.896× 加速** |
| **ForgeMatch，652 步** | **24.8998 秒** | **3.27498** | **5** | — |

以上对齐的是 **loss≤3.28 门槛**，实际 loss、机器和样本数不同，不能解释为同 loss 或同机受控对照的提升。Exact-match 的质量余量更大；ANVIL2 作者披露其 18 次统计中有一次原始日志遗失。我们此前也完成了两种原策略的同机单 seed 复现，详见[比较口径](docs/STRATEGY.md#comparisons)。

## 知名机构及研究团队的公开 baseline

核查日期：**2026-09-23**。以下均涉及 **8×H100、FineWeb loss≤3.28** 的训练计时任务；包含历史纪录和论文实验，不代表这些机构当前的最优能力。标有“约”的秒数由官方榜单的分钟数换算。

| 机构关联 | 策略 | 公开耗时 | 成绩性质 |
|---|---|---:|---|
| Google + Google DeepMind、威斯康星大学麦迪逊分校、UC San Diego | [PACEvolve](https://arxiv.org/pdf/2601.10657v3) | **140.2 秒** | 论文实验：旧 v40 基线 142.8→140.2 秒；未找到正式上榜证据 |
| Georgia Tech + Microsoft | [NorMuon](https://github.com/KellerJordan/modded-nanogpt/pull/144) | **约 140.70 秒** | 已接受的历史纪录 #41，2.345 分钟 |
| Stanford 关联的 Enigma 项目 | [梯度 all-reduce 优化](https://github.com/KellerJordan/modded-nanogpt#world-record-history) | **约 179.40 秒** | 已接受的历史纪录 #22，2.990 分钟 |
| Recursive | [ReLU² kernel 优化](https://github.com/KellerJordan/modded-nanogpt/pull/322) | **约 75.36 秒** | 已接受的历史纪录 #87，1.256 分钟；原提交仅部分改动被采纳 |
| Hyperstition，原 Social Physics Lab | [ANVIL2](https://github.com/KellerJordan/modded-nanogpt/pull/360) | **39.914 秒** | 18 次公开均值；PR 尚未合并 |

机构归属证据、日期与原始来源详见 [baseline 文档](docs/BASELINES.md)。ANVIL2 作者的 MIT 教育背景不能将该成绩变成“MIT 实验室纪录”；Stanford 学生个人提交也不能直接归给 Stanford 实验室。

## 重要程度与考察内容

**它在小型语言模型训练效率、GPU 系统优化和自动化研究评估中具有较高参考价值。** 任务开放、质量目标固定，改动可追溯到源码和日志，适合反复验证优化思路。Google/DeepMind 的 PACEvolve、METR 和 Prime Intellect 都将它用于研究评估。Muon 系列展示了部分优化思想向更大模型迁移的价值，但每项 speedrun 技巧仍需分别验证可扩展性。[相关研究与边界](docs/BASELINES.md#benchmark-significance-and-scope)

| 考察维度 | 具体内容 |
|---|---|
| 收敛效率 | 优化器、学习率、初始化、训练日程，能否用更少更新达到指定 loss |
| 模型与目标设计 | 注意力、残差、embedding、辅助预测目标等设计 |
| GPU 与分布式效率 | BF16/FP8、Triton/CUDA kernel、算子融合、通信与计算重叠 |
| 数据与主机协作 | 数据加载、CPU 绑核、预取、内存分配、H2D 传输与 GPU 等待 |
| 实验与复现质量 | 多次运行、统计显著性、同机对照、计时边界、源码与日志可核查 |

主赛道看达到指定质量的训练时间；优化器赛道主要看固定模型下的训练步数，二者不能直接换算。我们的 **652 步 / 24.8998 秒** 不能直接与 Prime Intellect 表中的 **2726 步或 3042 步** 比较。

该成绩的解释范围是这项训练任务。它不直接衡量聊天、推理、代码生成、推理服务延迟或大模型训练的整体成本，也不能据此认定某个研究系统全面胜过 Google、Microsoft 等机构。我们的方案继承了更多后续社区优化，且仍待官方复核。

## 核心策略

模型从训练前缀中检索候选后续 token，将匹配长度与候选 embedding 转化为可学习特征，在网络输入、中间层和输出处使用。652 步训练日程配合 FP8 计算和稀疏参数更新，在目标 loss 下缩短训练时间。CPU 绑核、延后至实际使用时的 CUDA 等待、各 rank 协调释放索引，以及普通 CPU 内存中的原始 shard，进一步减少主机与 GPU 的协作开销。实际 H2D 传输使用 pinned 小批次缓冲；查询先于当前 step 数据入库，完整验证与计时边界保持不变。详见[策略说明](docs/STRATEGY.md)。

参考环境为 **8×H100 80GB HBM3、双路 Xeon Platinum 8481C、约 1.8 TiB 主机内存**。完整检索使用 **103 个训练 shard**，另需一个验证 shard。CPU 绑核针对该机器拓扑，迁移到其他机器前应按[复现指南](docs/REPRODUCE.md)核查。

[`model/`](model/) 保存 33 份逐字节一致的归档源码；[`provenance/source-files.json`](provenance/source-files.json) 记录其 SHA256。`model/README.md` 是继承的历史文档，运行本策略请以本仓库的[复现指南](docs/REPRODUCE.md)为准。

[来源署名与致谢](CREDITS.md) · [MIT 许可证](LICENSE)
