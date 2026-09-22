"""Optional rank-local CPU placement; called before importing torch or worker pools."""
import os


def configure_rank_affinity():
    mode = os.environ.get("HYBRID_CPU_AFFINITY", "none")
    if mode == "none":
        return
    if mode not in ("physical", "smt"):
        raise ValueError("HYBRID_CPU_AFFINITY must be none, physical or smt")
    rank = int(os.environ["LOCAL_RANK"])
    if int(os.environ["LOCAL_WORLD_SIZE"]) != 8 or not 0 <= rank < 8:
        raise RuntimeError("This measured CPU topology uses eight local ranks")
    cpus = set(range(rank * 13, (rank + 1) * 13))
    if mode == "smt":
        cpus.update(cpu + 104 for cpu in list(cpus))
    allowed = os.sched_getaffinity(0)
    if not cpus <= allowed:
        raise RuntimeError(f"Requested CPU set is outside current affinity: {cpus - allowed}")
    # The host was measured as two52-core sockets, GPUs0–3/node0 and4–7/node1.
    expected_node = rank // 4
    for cpu in cpus:
        if not os.path.exists(f"/sys/devices/system/node/node{expected_node}/cpu{cpu}"):
            raise RuntimeError("CPU topology differs from declared rank-local mapping")
    os.sched_setaffinity(0, cpus)
    if os.sched_getaffinity(0) != cpus:
        raise RuntimeError("Failed to apply the complete CPU mask")
    print(f"[cpu-affinity] local_rank={rank} mode={mode} cpus={sorted(cpus)} node={expected_node}", flush=True)
