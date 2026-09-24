# ScienceGuru：NanoGPT 训练仅需 24.8998 秒，较官方 SOTA 加速约 2.71 倍

**AutoTrust 的 ScienceGuru 科研平台使用 Guru Turbo 1.2 模型，将 8×H100 上的 NanoGPT Speedrun 训练时间压至 25 秒以内。** 五个 seed 的平均用时为 **24.8998 秒**，每次验证 loss 均 ≤3.28。在相同质量门槛下，相较官方 SOTA 的约 67.56 秒，**耗时降低约 63.14%，节省约 42.66 秒**。[成绩与对比来源](docs/BASELINES.md)。

| 平均训练时间 | 相较官方 SOTA 加速 | 训练耗时降低 | 达到 loss ≤3.28 的 seed |
|---:|---:|---:|---:|
| **24.8998 秒** | **≈2.71×** | **≈63.14%** | **5 / 5** |

自 2024 年以来，这项基准已累积 **91 条官方历史纪录，另有两次重计时**。每一次新进展，都需要继续优化经过社区多年打磨的训练系统；下图将我们的成绩放在这一持续演进的历史中。

![NanoGPT Speedrun 成绩历史：91 条官方纪录与两项公开成绩，最后展示 AutoTrust 的 ScienceGuru 使用 Guru Turbo 1.2 取得的 24.8998 秒成绩。](assets/speedrun-history.svg)

[图表数据与来源](docs/SPEEDRUN_CHART.md) · [完整历史 PNG](assets/speedrun-history.png) · [近一年放大版](assets/speedrun-history-recent.png)

[English](README.md) · [复现指南](docs/REPRODUCE.md) · [策略说明](docs/STRATEGY.md) · [证据说明](docs/EVIDENCE.md) · [研究 baseline](docs/BASELINES.md) · [领先团队背景](docs/TEAMS.md) · [基准规则](docs/COMPLIANCE.md)

## AutoTrust、ScienceGuru 与 Guru Turbo 1.2

[**AutoTrust**](https://autotrust.ai/) 面向科学研究开发 AI；**ScienceGuru** 是其科研平台，将文献阅读、推理和写作整合到一个工作空间。本项目使用 **Guru Turbo 1.2 模型**开展研究，并公开 NanoGPT 训练策略、实验成绩与复现证据。

| 名称 | 在本项目中的角色 |
|---|---|
| **AutoTrust** | 项目背后的团队与品牌。 |
| **ScienceGuru** | AutoTrust 的科研平台，也是本仓库成绩使用的名称。 |
| **Guru Turbo 1.2** | 本研究项目使用的模型。 |

平台介绍来自 [AutoTrust 官网](https://autotrust.ai/)，模型版本与三者关系由项目负责人确认，记录于[项目署名](provenance/project-attribution.json)。基准测试实际训练的是 [`model/`](model/) 中归档的小型语言模型。

ScienceGuru 的训练方案结合训练语料的因果前缀检索、稀疏 n-gram embedding、FP8 计算和紧凑训练日程，并通过 CPU 绑核、异步预取与协调内存管理减少 GPU 等待和时间波动。

## 已核验成绩

由 **AutoTrust · ScienceGuru · Guru Turbo 1.2** 跑出的 652 步方案，采用固定五个 seed，完整验证集 **10,485,760 tokens**，全词表概率计算。五次完整运行的最终 loss 均低于 **3.28**。

![ScienceGuru 五个 seed 的验证结果：训练用时为 24.868 至 24.939 秒，平均 24.8998 秒，五次验证 loss 均低于 3.28。](assets/seed-validation.svg)

[下载验证图 PNG](assets/seed-validation.png) · [图表来源与生成方式](docs/SPEEDRUN_CHART.md)

<details>
<summary>公开验证数据：逐 seed 成绩与统计</summary>

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

</details>

成绩采用最终 validation 行的 `train_time`，计入训练、训练内容的读取、建库、查询与必要收尾。编译、预热和最终模型验证在该计时区间之外，详见[计时说明](docs/COMPLIANCE.md#timing-boundary)。

完整结果见[机器可读记录](results/cohorts.json)及[证据说明](docs/EVIDENCE.md)。

## 性能对比

核查日期：**2026-09-24 UTC**。以下比较 **8×H100、FineWeb loss≤3.28** 的训练耗时；标有 **≈** 的耗时由榜单中四舍五入的分钟数换算。加速比为各方案耗时除以 ScienceGuru 的五个 seed 平均耗时。

![NanoGPT 训练耗时对比：ScienceGuru 24.8998 秒、ANVIL2 39.914 秒、Exact-match 47.2056 秒、官方 SOTA 约 67.56 秒、Recursive 约 75.36 秒、PACEvolve 140.2 秒、NorMuon 约 140.70 秒、Enigma 约 179.40 秒。](assets/benchmark-comparison.svg)

[下载对比图 PNG](assets/benchmark-comparison.png) · [对比数据与来源](docs/BASELINES.md)

| 策略 | 团队与机构 | 训练耗时 | ScienceGuru 加速比 |
|---|---|---:|---:|
| **[ScienceGuru，652 步](results/cohorts.json)** | **AutoTrust · Guru Turbo 1.2** | **24.8998 秒** | — |
| [ANVIL2](https://github.com/KellerJordan/modded-nanogpt/pull/360) | Hyperstition，原 Social Physics Lab | **39.914 秒** | **1.603×** |
| [Exact-match](https://github.com/hermabr/modded-nanogpt-public/blob/3e92b0e28293dcb184197da1a0ce1f543e84f76c/records/track_1_short/2026-09-16_ExactMatch/this_pr/statistics.md) | Herman Brunborg / Stanford 博士生 | **47.2056 秒** | **1.896×** |
| **[官方 SOTA · Canonical Token Masking](https://github.com/KellerJordan/modded-nanogpt/pull/350)** | Jan Varho / Fluentia | **≈67.56 秒** | **≈2.713×** |
| [ReLU² kernel 优化](https://github.com/KellerJordan/modded-nanogpt/pull/322) | Recursive | **≈75.36 秒** | **≈3.027×** |
| [PACEvolve](https://arxiv.org/pdf/2601.10657v3) | Google + Google DeepMind、威斯康星大学麦迪逊分校、UC San Diego | **140.2 秒** | **5.631×** |
| [NorMuon](https://github.com/KellerJordan/modded-nanogpt/pull/144) | Georgia Tech + Microsoft | **≈140.70 秒** | **≈5.651×** |
| [梯度 all-reduce 优化](https://github.com/KellerJordan/modded-nanogpt#world-record-history) | Stanford 关联的 Enigma 项目 | **≈179.40 秒** | **≈7.205×** |

相较官方 SOTA，ScienceGuru **耗时降低约 63.14%，加速约 2.713 倍，节省约 42.66 秒**。该纪录在[官方 Track 1 榜单](https://github.com/KellerJordan/modded-nanogpt#world-record-history)中的成绩为 1.126 分钟，对应 [PR #350](https://github.com/KellerJordan/modded-nanogpt/pull/350)。

ANVIL2 为 18 次运行的均值，平均 loss 3.277311；Exact-match 为 5 次运行的均值，平均 loss 3.26556。同机 seed-42 复现详见[策略比较](docs/STRATEGY.md#comparisons)；机构关联、实验配置及 OpenAI/Anthropic 模型的优化器赛道结果详见 [baseline 文档](docs/BASELINES.md)。

## 领先贡献者的背景

| 贡献者 | 公开背景 | 本次对比中的成绩 |
|---|---|---|
| **Jan Varho · Canonical Token Masking** | [个人网站](https://jan.varho.org/)介绍其为 Fluentia 软件开发者。 | **≈67.56 秒** |
| **Hyperstition · Deven Pietrzak** | [ANVIL2 项目说明](https://github.com/KellerJordan/modded-nanogpt/pull/360)自述其背景为“MIT Math”；Hyperstition 前身为 Social Physics Lab。 | **39.914 秒** |
| **Herman Brunborg · Exact-match** | [GitHub 主页](https://github.com/hermabr)介绍其为 Stanford 博士生。 | **47.2056 秒** |
| **Recursive · Cong Lu** | [个人网站](https://www.conglu.co.uk/)介绍其为 Recursive 创始团队成员，曾任 Google DeepMind 研究科学家。 | **≈75.36 秒** |

各团队的技术方法、原始来源与比较范围见[领先团队背景](docs/TEAMS.md)；本实现继承的代码与方法见[来源署名与致谢](CREDITS.md)。

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
