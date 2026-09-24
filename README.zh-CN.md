**AUTOTRUST AI  ·  SCIENCEGURU  ·  研究**

# New Record：ScienceGuru 将 NanoGPT Speedrun 缩短至 24.9 秒，速度为 Recursive 六月纪录（75.4 秒）的 3 倍

运行 Guru Turbo 1.2 的 AutoTrust 科研平台，在八张 H100 上用 24.90 秒将 GPT-2 Small 训练至 3.28 的验证损失目标：训练速度达到当前官方纪录的 2.71×。

2026 年 9 月 25 日  ·  ScienceGuru  ·  Guru Turbo 1.2  ·  NanoGPT Speedrun

今天，我们发布 ScienceGuru 在 NanoGPT Speedrun 上的成绩。这个开放基准关注的是：将一个 GPT-2 规模的模型训练至固定质量门槛，最快需要多久。运行 Guru Turbo 1.2 的 ScienceGuru，在八张 H100 GPU 上以平均 24.90 秒的用时，将模型训练至平均验证损失 3.2750；实验使用五个预注册随机种子，并保留每一次运行的结果。

这一速度是当前官方纪录 Canonical Token Masking（#91，约 67.56 秒）的 2.71×，也是我们核查过的最快开放投稿 ANVIL2（39.91 秒）的 1.60×。代码、日志、源码哈希和验证脚本已在 [github.com/AutoTrustAI/nanogpt-speedrun-sota-by-guru](https://github.com/AutoTrustAI/nanogpt-speedrun-sota-by-guru) 公开。

![ScienceGuru 的 NanoGPT Speedrun 成绩](assets/blog-nanogpt-scorecard.png)

*8×H100 上五个随机种子的平均值。该成绩为自行报告，目前尚未成为排行榜接受的纪录。*

## 为什么选择 NanoGPT Speedrun

Speedrun 固定了数据、硬件和目标，即在一个 8×H100 节点上达到不高于 3.28 的 FineWeb 验证损失，并且只衡量训练时间。任何提升都必须经得起一个已被社区优化两年多的代码库的检验：通过对优化器、架构、数值精度、内核、通信和数据加载的改进，91 项官方纪录已将训练时间从 45 分钟缩短到约 67.6 秒。

因此，它是对自动化科研的一项严格检验。今年 6 月，[Recursive 报告了](https://www.recursive.com/articles/first-steps-toward-automated-ai-research)其自动化科研系统取得的 77.5 秒方案，其更快的 ReLU² 内核成为官方纪录 #87。

![NanoGPT Speedrun 的官方纪录、开放投稿与 ScienceGuru 成绩](assets/blog-nanogpt-history.png)

*自 2025 年 10 月以来的官方 Track 1 纪录、两项开放投稿和 ScienceGuru 的五种子平均值，采用对数刻度。官方时间由排行榜中经过舍入的分钟数换算而来。*

## ScienceGuru 改了什么

这个结果并非来自单一技巧。ScienceGuru 从最前沿出发，以两个最快的公开投稿为起点，它们仍处于开放的拉取请求状态。ScienceGuru 将两者融合，借助融合后的模型将训练计划几乎缩短一半，然后重新调整那些决定八张 GPU 是否会闲置等待的主机端系统。Speedrun 的规则明确鼓励基于开放的拉取请求继续开发，仓库中也对两位作者作了致谢。

### 1. 融合两项开放投稿

Deven Pietrzak 的 [ANVIL2](https://github.com/KellerJordan/modded-nanogpt/pull/360) 是一个快速训练系统：它采用采样 softmax 训练、拥有 84.6 百万行的哈希 n-gram 嵌入表、ANVIL 优化器、全栈 FP8、混合宽度注意力，以及通过 CUDA 图捕获的训练步骤。Herman Brunborg 的 [Exact-match](https://github.com/KellerJordan/modded-nanogpt/pull/367) 则增加了另一种记忆：在 CPU 上为训练数据建立索引，找出当前上下文在此前数据中的最长匹配，并将匹配片段后续的 token 作为可学习向量，添加到网络的输入、中间和输出位置。

两者无法直接组合。ANVIL2 的 CUDA 图会重放固定的内存地址，而 Exact-match 则在 CPU 线程上产生依赖数据的匹配结果。ScienceGuru 将检索结果设为固定形状，即每个位置一个匹配长度和四个候选 token，再将其接入 ANVIL2 捕获的图中，并使用合成的“有匹配”和“无匹配”输入对图进行预热，让两条路径都在计时开始前完成捕获。它还将检索参数注册到 ANVIL2 的优化器中，把中间注入点移到 ANVIL2 跳过的层之前，并让检索遵循真实的文档边界——这些边界在 ANVIL2 为注意力计算拆分序列之前取得。

**技术细节**

#### 捕获的训练步骤中的检索

Exact-match 的三个注入点在 ANVIL2 前向传播中的位置（摘自 `model/train_gpt.py`）：

```python
x = self.embed(input_seq)
x = x + self.ret_site_scale_in.type_as(x) * ret_r            # input
...
# ANVIL skips layer 7; inject before that branch and its cache[7] write.
if i == 7:
    x = x + self.ret_site_scale_mid.type_as(x) * ret_r[None]  # middle
...
x = x + self.ret_site_scale_out.type_as(x) * ret_r[None]      # output
x = norm(x)
```

不计时的预热交替使用合成的“有匹配”和“无匹配”输入，让 CUDA 图捕获两条路径；模型和优化器状态在计时开始前恢复：

```python
# Alternate absent/present synthetic matches; all learned state is restored below.
_warm_ret = (torch.full_like(inputs, 8 if step % 2 else 0, dtype=torch.int64),
             (inputs.long()[:, None].expand(-1, 4).contiguous() if step % 2 else
              torch.full((inputs.numel(), 4), -1, dtype=torch.int64, device=device)))
_CG.fwd(step, inputs, targets, cum_seqlens, _bg_fwd, _warm_ret)
```

### 2. 将训练计划几乎缩短一半

检索从第一步起就提供下一个 token 的证据，因此融合后的模型能够更早达到目标。ScienceGuru 将 ANVIL2 的完整训练计划从 1,194 步按比例缩减至 656 步，再缩减至 652 步，同时保持各阶段结构不变。最终计划使用 180.9 百万个 token 训练网络。与 Exact-match 一样，检索索引本身由全部 103 个 FineWeb 训练分片构建，且构建过程计入计时区间。

### 3. 持续为 GPU 提供数据

检索在 CPU 上运行，因此最后的提升来自系统层面的工作：

- **NUMA 感知的进程放置。** 每张 GPU 的进程都运行在其所属 CPU 插槽的 13 个物理核心上，并在 PyTorch 启动工作线程池之前完成设置。
- **延后 CUDA 等待。** 预取批次携带其就绪事件，训练步骤只在首次使用时等待该事件。
- **有界异步复制。** 更大的锁页缓冲区和对在途复制数量的限制，让检索结果能够持续传输到 GPU，而不会阻塞加载器。
- **协调索引释放。** 在任何 rank 释放自身索引之前，所有 rank 都先确认自己的查询已完成。
- **可分页的原始分片。** 大型 CPU 分片不再整体锁页；只对向 GPU 提供数据的逐批次缓冲区锁页。

在同一台机器上测量，这些步骤将五种子平均用时从 25.28 秒降至 25.01 秒，而 652 步训练计划进一步将其降至 24.90 秒。

**技术细节**

#### 延后 CUDA 等待

预取线程在一个批次的复制操作发出后记录一个事件。训练循环只在该批次首次被 GPU 使用时等待该事件，而不是让更早的工作等待未来的批次（`model/retrieval.py`）：

```python
def wait_for_batch(batch):
    """Transfer a prefetched batch's CUDA ownership at its first real consumer."""
    ready = batch[8]
    if ready is not None:
        consumer_stream = torch.cuda.current_stream(batch[0].device)
        consumer_stream.wait_event(ready)
        for tensor in (*batch[:4], *batch[7]):
            tensor.record_stream(consumer_stream)
```

![ScienceGuru 在同一台机器上的实验进展](assets/blog-nanogpt-research-loop.png)

*同一台机器上的测量结果。原始 ANVIL2 和 Exact-match 数值来自随机种子 42 的单次运行；ScienceGuru 各行是五种子平均值。*

## 我们如何验证

速度成绩很容易出错，因此这份发布包从设计上就便于核查：

- **预注册随机种子。** 在首次运行之前就固定了随机种子 42 至 46，并报告每一次运行。五次运行的损失均不高于 3.28（平均 3.27498，最差 3.2777）。针对 3.28 的单侧 t 检验得到 p ≈ 0.0019（t = 6.06，自由度为四），满足 Speedrun 的 p < 0.01 规则。另一个 656 步实验组平均用时 25.01 秒（p ≈ 0.001）。
- **沿用上游计时边界。** 与所有纪录一样，编译、预热和最终验证的前向传播不计入时间。检索索引构建、每一次检索查询、跨 rank 合并、线程汇合和最终同步均计入时间。
- **因果检索。** 每个训练步骤先查询，再插入自身的 token。验证索引仅包含训练分片，验证目标从不插入其中。
- **数据保持不变。** 官方 token 文件经过哈希核验，并通过一项包含 173 个案例的对比测试检查修改后的加载器。
- **固定源码。** 33 个源文件与实验提交 `d7b6a095` 逐字节一致。运行 `python3 scripts/verify_results.py`，即可在 CPU 上重新核查每个哈希、每次运行和每项统计量。

## 范围与注意事项

- 这是自行报告的成绩，并非排行榜接受的纪录。它基于两个开放的拉取请求，而维护者尚未审查这两个请求。

- 检索索引覆盖完整训练集，而网络使用 180.9 百万个 token 进行训练。维护者尚未对这种检索方式作出裁定；Exact-match 的拉取请求目前还没有收到审查。

- 与 ANVIL2 和 Exact-match 的对比使用的是它们在其他机器上公布的平均值；我们在同一台机器上的复现是单次运行。最终实验组的随机种子在开发期间也曾使用。

- CPU 放置方案针对我们的主机进行了调优：两颗 Xeon Platinum 8481C CPU，以及约 1.8 TiB 内存。

## 下一步

这是 ScienceGuru 本月在开放科研基准上发布的第三项成果。在 Autoresearch@Home 这一五分钟 NanoChat 基准上，Recursive 于 6 月报告的 10 个种子的平均成绩为 0.9109 比特/字节，而搭载 Guru Turbo 1.0 的 ScienceGuru 达到了 [0.889522](https://github.com/AutoTrustAI/autoresearch-sota-strategy)，截至 9 月 1 日位列官方排行榜 #1。在 MedARC 的 NanoPath v2 上，维护者独立重新训练了 ScienceGuru 的方案后，该方案以 0.6597 的成绩成为[经过验证的可训练方案第一名](https://github.com/AutoTrustAI/nanopath-sota-strategy)。

每一次这样的运行都会留下经过验证的科研轨迹，而 AutoTrust 会使用这些轨迹训练未来的 Guru 模型。完成这项工作的系统，也在产生将帮助它持续改进的数据。

### SCIENCEGURU

将取得这一成果的系统用于你自己的研究。在 [ScienceGuru.ai](https://scienceguru.ai) 下载 ScienceGuru。

[下载 ScienceGuru →](https://scienceguru.ai)

代码、日志和验证：[github.com/AutoTrustAI/nanogpt-speedrun-sota-by-guru](https://github.com/AutoTrustAI/nanogpt-speedrun-sota-by-guru)

社区纪录：[github.com/KellerJordan/modded-nanogpt](https://github.com/KellerJordan/modded-nanogpt#world-record-history)（Track 1）。官方时间由排行榜中经过舍入的分钟数换算而来。
