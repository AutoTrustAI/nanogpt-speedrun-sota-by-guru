# ForgeMatch · 铸忆

**ANVIL2 训练系统与 exact-match 记忆检索融合：8×H100 上，五个 seed 平均 24.8998 秒。**

[English](README.md) · [复现指南](docs/REPRODUCE.md) · [策略说明](docs/STRATEGY.md) · [证据说明](docs/EVIDENCE.md) · [规则与边界](docs/COMPLIANCE.md)

**ForgeMatch** 是 AutoTrust-AI 对这套融合与优化策略的命名：**Forge** 呼应 ANVIL 的锻造意象，**Match** 指向训练前缀的精确匹配；中文名 **铸忆**，意为“把记忆铸入模型”。底层训练算法和检索方法来自公开贡献，详见[致谢](CREDITS.md)。

## 已核验成绩

652 步、固定五个 seed，完整验证集 **10,485,760 tokens**，全词表概率计算。五次完整运行的最终 loss 均低于 **3.28**。

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

## 核心策略

在 ANVIL2 底座中加入 exact-match 检索特征，并缩短、重新安排训练日程。随后优化 CPU 绑核、预取批次的 CUDA 等待时机、各 rank 的索引释放协调，以及原始 shard 的 CPU 内存分配。实际 H2D 传输继续使用 pinned 小批次缓冲；查询先于当前 step 数据入库，完整验证与计时边界保持不变。详见[策略说明](docs/STRATEGY.md)。

参考环境为 **8×H100 80GB HBM3、双路 Xeon Platinum 8481C、约 1.8 TiB 主机内存**。完整检索使用 **103 个训练 shard**，另需一个验证 shard。CPU 绑核针对该机器拓扑，迁移到其他机器前应按[复现指南](docs/REPRODUCE.md)核查。

[`model/`](model/) 保存 33 份逐字节一致的归档源码；[`provenance/source-files.json`](provenance/source-files.json) 记录其 SHA256。`model/README.md` 是继承的历史文档，运行本策略请以本仓库的[复现指南](docs/REPRODUCE.md)为准。

感谢 [Keller Jordan 及 modded-nanogpt 贡献者](https://github.com/KellerJordan/modded-nanogpt)、[Deven Pietrzak 的 ANVIL2](https://github.com/KellerJordan/modded-nanogpt/pull/360) 和 [hermabr 的 exact-match](https://github.com/KellerJordan/modded-nanogpt/pull/367)。详见[致谢](CREDITS.md)与[许可证](LICENSE)。
