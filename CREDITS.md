# Credits and provenance

ForgeMatch（铸忆） is AutoTrust-AI's name for this integration, schedule tuning, systems optimization, and experiment record. It builds directly on the following public work.

| Contribution | Author / project | Reference |
|---|---|---|
| NanoGPT speedrun benchmark and evolving trainer | Keller Jordan and the modded-nanogpt community | [modded-nanogpt](https://github.com/KellerJordan/modded-nanogpt) |
| ANVIL2 training system, kernels, sparse tables, and optimizer work | Deven Pietrzak | [PR #360](https://github.com/KellerJordan/modded-nanogpt/pull/360), source `c924f68e4d72e80307fc27a7bb3a55cfb6ad43c7` |
| Exact-match training-data retrieval and learned retrieval features | hermabr | [PR #367](https://github.com/KellerJordan/modded-nanogpt/pull/367), archived PR head `3e92b0e28293dcb184197da1a0ce1f543e84f76c` |
| Original NanoGPT / llm.c lineage | Andrej Karpathy and contributors | [nanoGPT](https://github.com/karpathy/nanoGPT), [llm.c](https://github.com/karpathy/llm.c) |

The Exact-match published 47.2056-second report identifies training source commit `65fb235a2e755b23ccd8edb26581511f57c88721`; its statistics and record are also present in the archived PR head above. A PR-head identifier and a record's embedded source identifier should not be conflated.

Additional foundations include PyTorch, Triton, FlashAttention, the `kernels` ecosystem, Rust/PyO3, Hugging Face, FineWeb, and the many prior speedrun contributors. The inherited [model README](model/README.md) preserves the upstream contributor history, but its historical run instructions do not describe the ForgeMatch reproduction recipe.

Our integration adapts retrieval to the ANVIL loader, optimizer, and graph buffers; tunes the shorter training schedule; applies CPU affinity, deferred CUDA waiting, coordinated index release, and pageable raw-shard allocation; and records complete fixed-seed evidence. These changes do not transfer authorship of upstream methods or imply upstream endorsement.

The archived experiment source is commit `d7b6a09512010189292974b3a9b9f19c111d9b38`, with parent `7f6f968dea96b9c5219affc4b6c0a678cf1d57c0`. The packaged 33 source files are byte-identical to that snapshot and pinned in [provenance/source-files.json](provenance/source-files.json). This packaging repository has its own Git history.

The original MIT license is retained in [LICENSE](LICENSE) and [model/LICENSE](model/LICENSE). Dataset and external dependency licenses remain those of their respective projects. No training dataset, credentials, or pretrained external knowledge is supplied by the documentation package.
