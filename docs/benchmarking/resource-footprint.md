# Resource Footprint: Memory, Disk & Retention Auditing

`xinfer-forge` operates within constrained edge footprints, enforcing strict garbage collection, memory pooling, and automated checkpoint pruning.

---

## 1. RAM Footprint Breakdown During Training

Memory usage was profiled during maximum GPU and CPU execution passes over a 10,000-sample dataset:

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ Total Process Resident Set Size (RSS): 1,480 MB             │
 ├─────────────────────────────────────────────────────────────┤
 │ • PyTorch Execution Runtime & C++ Kernels     : 650 MB      │
 │ • Model Weights & Optimizer State (AdamW)     : ~14 MB      │
 │ • Gradient Graphs & Activation Buffers (B=64) : 42 MB       │
 │ • In-Memory Dataset Tensors (10k x 32 Float32): ~1.3 MB     │
 │ • Python Virtual Environment Base Overhead    : 180 MB      │
 │ • CUDA Driver Context & Memory Pool Buffer    : 592 MB      │
 └─────────────────────────────────────────────────────────────┘
```

* **Zero Memory Creep:** After each adaptation cycle, `forge-cli` invokes `torch.cuda.empty_cache()` and explicit Python garbage collection (`gc.collect()`), returning RSS to baseline idle ($< 220\text{ MB}$).

---

## 2. Checkpoint Retention Policy (`checkpoint_dir`)

To prevent storage exhaustion on local NVMe or eMMC flash storage:
* **Active Verified Baseline:** Stored as `network_threat_v1.onnx` ($7.4\text{ KB}$).
* **Candidate Checkpoint:** Stored as `candidate_weights.pt` ($18.2\text{ KB}$).
* **Pruning Invariant:** Only the **latest verified checkpoint** and the **active production model** are retained on disk. Intermediate epoch checkpoints are discarded automatically upon training completion.

