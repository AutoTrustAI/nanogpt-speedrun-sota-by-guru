# ForgeMatch · 铸忆

**ScienceGuru + Guru Turbo 1.2 · 8×H100 上，五个 seed 平均 24.8998 秒。**

[English](README.md) · [复现指南](docs/REPRODUCE.md) · [策略说明](docs/STRATEGY.md) · [证据说明](docs/EVIDENCE.md) · [实验室 baseline](docs/BASELINES.md) · [基准规则](docs/COMPLIANCE.md)

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
- 运行顺序固定为 **43→42→44→45→46**，统计包含全部五次运行。
- 本次五 seed 达到目标：平均 ≤25 秒、极差 ≤5 秒、每次 loss≤3.28。

成绩采用最终 validation 行的 `train_time`，计入训练、训练内容的读取、建库、查询与必要收尾。编译、预热和最终模型验证在该计时区间之外，详见[计时说明](docs/COMPLIANCE.md#timing-boundary)。

完整结果见[机器可读记录](results/cohorts.json)及[证据说明](docs/EVIDENCE.md)。

## 与官方已认可的 SOTA 比较

截至 **2026-09-23**，[官方 Track 1 纪录榜](https://github.com/KellerJordan/modded-nanogpt#world-record-history)的最新成绩为 **@jvarho 的 Canonical Token Masking**，耗时 **1.126 分钟（约 67.56 秒）**，对应的 [PR #350](https://github.com/KellerJordan/modded-nanogpt/pull/350) 已合并。

| 策略 | 训练耗时 | 硬件 | 目标 loss |
|---|---:|---|---:|
| **官方 SOTA — Canonical Token Masking** | **约 67.56 秒** | 8×H100 | ≤3.28 |
| **ForgeMatch — ScienceGuru + Guru Turbo 1.2** | **24.8998 秒** | 8×H100 | ≤3.28 |

相较官方 SOTA 公布的耗时，ForgeMatch **耗时降低约 63.14%，加速约 2.713 倍，节省约 42.66 秒**。参考秒数由榜单中已四舍五入的分钟数换算，ForgeMatch 采用五个 seed 的实测均值。

## 与公开方案比较

| 策略 | 公开平均耗时 | 平均 loss | 次数 | ForgeMatch 耗时降幅 |
|---|---:|---:|---:|---:|
| [ANVIL2](https://github.com/KellerJordan/modded-nanogpt/pull/360) | 39.914 秒 | 3.277311 | 18 | **37.62% / 1.603× 加速** |
| [Exact-match](https://github.com/hermabr/modded-nanogpt-public/blob/3e92b0e28293dcb184197da1a0ce1f543e84f76c/records/track_1_short/2026-09-16_ExactMatch/this_pr/statistics.md) | 47.2056 秒 | 3.26556 | 5 | **47.25% / 1.896× 加速** |
| **ForgeMatch，652 步** | **24.8998 秒** | **3.27498** | **5** | — |

以上采用 **loss≤3.28 门槛**，对比各来源在各自机器上报告的平均耗时，样本数与实际 loss 列于表中。两种原策略的同机 seed-42 复现结果与来源详见[策略比较](docs/STRATEGY.md#comparisons)。

## 知名机构及研究团队的公开 baseline

核查日期：**2026-09-23**。以下采用 **8×H100、FineWeb loss≤3.28** 的训练计时任务。标有“约”的秒数由榜单中已四舍五入的分钟数换算。

| 机构关联 | 策略 | 公开耗时 |
|---|---|---:|
| Google + Google DeepMind、威斯康星大学麦迪逊分校、UC San Diego | [PACEvolve](https://arxiv.org/pdf/2601.10657v3) | **140.2 秒** |
| Georgia Tech + Microsoft | [NorMuon](https://github.com/KellerJordan/modded-nanogpt/pull/144) | **约 140.70 秒** |
| Stanford 关联的 Enigma 项目 | [梯度 all-reduce 优化](https://github.com/KellerJordan/modded-nanogpt#world-record-history) | **约 179.40 秒** |
| Recursive | [ReLU² kernel 优化](https://github.com/KellerJordan/modded-nanogpt/pull/322) | **约 75.36 秒** |
| Hyperstition，原 Social Physics Lab | [ANVIL2](https://github.com/KellerJordan/modded-nanogpt/pull/360) | **39.914 秒** |

机构关联、日期、原始来源及 OpenAI/Anthropic 模型的优化器赛道结果详见 [baseline 文档](docs/BASELINES.md)。

## 重要程度与考察内容

**它在小型语言模型训练效率、GPU 系统优化和自动化研究评估中具有较高参考价值。** 任务开放、质量目标固定，改动可追溯到源码和日志，适合反复验证优化思路。Google/DeepMind 的 PACEvolve、METR 和 Prime Intellect 都将它用于研究评估。Muon 系列展示了部分优化思想向更大模型迁移的价值。[相关研究](docs/BASELINES.md#benchmark-significance-and-scope)

| 考察维度 | 具体内容 |
|---|---|
| 收敛效率 | 优化器、学习率、初始化、训练日程，能否用更少更新达到指定 loss |
| 模型与目标设计 | 注意力、残差、embedding、辅助预测目标等设计 |
| GPU 与分布式效率 | BF16/FP8、Triton/CUDA kernel、算子融合、通信与计算重叠 |
| 数据与主机协作 | 数据加载、CPU 绑核、预取、内存分配、H2D 传输与 GPU 等待 |
| 实验与复现质量 | 多次运行、统计显著性、同机对照、计时边界、源码与日志可核查 |

主赛道以达到指定质量的训练时间计分；优化器赛道以固定模型、数据和 batch size 下的训练步数计分。

## 核心策略

模型从训练前缀中检索候选后续 token，将匹配长度与候选 embedding 转化为可学习特征，在网络输入、中间层和输出处使用。652 步训练日程配合 FP8 计算和稀疏参数更新，在目标 loss 下缩短训练时间。CPU 绑核、延后至实际使用时的 CUDA 等待、各 rank 协调释放索引，以及普通 CPU 内存中的原始 shard，进一步减少主机与 GPU 的协作开销。实际 H2D 传输使用 pinned 小批次缓冲；查询先于当前 step 数据入库，完整验证与计时边界保持不变。详见[策略说明](docs/STRATEGY.md)。

参考环境为 **8×H100 80GB HBM3、双路 Xeon Platinum 8481C、约 1.8 TiB 主机内存**。完整检索使用 **103 个训练 shard**，另需一个验证 shard。CPU 绑核针对该机器拓扑，迁移到其他机器前应按[复现指南](docs/REPRODUCE.md)核查。

[`model/`](model/) 保存 33 份逐字节一致的归档源码；[`provenance/source-files.json`](provenance/source-files.json) 记录其 SHA256。`model/README.md` 是继承的历史文档，运行本策略请以本仓库的[复现指南](docs/REPRODUCE.md)为准。

[来源署名与致谢](CREDITS.md) · [MIT 许可证](LICENSE)
