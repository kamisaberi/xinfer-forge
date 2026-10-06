# Training Execution Speeds: Edge CPU vs. Enterprise GPU

`xinfer-forge` is engineered to adapt models within constrained execution budgets. This benchmark evaluates the wall-clock execution time and energy required to train a standard **5,000-flow batch across 5 epochs**.

---

## 1. Execution Speed Comparison

```text
 5,000 SAMPLES / 5 EPOCHS WALL-CLOCK EXECUTION TIME (Lower is Better):

 4-Core Intel Core Ultra (CPU Mode) : ════════════════════════════════ 18.2s
 8-Core Rockchip RK3588 (CPU Mode)  : ══════════════════════════════════════════ 24.8s
 16-Core Intel Xeon 8480+ (AVX-512) : ══════════ 6.4s
 NVIDIA Jetson AGX Orin (GPU Mode)  : ══════ 4.1s
 NVIDIA RTX A4000 (16GB VRAM)       : ═══ 2.1s
 NVIDIA L4 Tensor Core GPU (24GB)   : ══ 1.8s
```

### Detailed Benchmark Results Table

| Target Hardware Platform | Compute Mode | Batch Size | Total Training Time (5 Epochs) | Throughput (Samples/Sec) | Energy Consumed (Joules) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Rockchip RK3588** | 8-Core ARM64 CPU | 64 | $24.8\,\text{seconds}$ | $1{,}008\text{ flows/s}$ | $185.2\,\text{J}$ |
| **Intel Core Ultra 7 165H**| 4 P-Cores (AVX2) | 64 | $18.2\,\text{seconds}$ | $1{,}373\text{ flows/s}$ | $218.4\,\text{J}$ |
| **Intel Xeon Platinum 8480+**| 16 Cores (AVX-512)| 128 | **$6.4\,\text{seconds}$** | $3{,}906\text{ flows/s}$ | $672.0\,\text{J}$ |
| **NVIDIA Jetson AGX Orin**| Ampere GPU (CUDA) | 128 | **$4.1\,\text{seconds}$** | $6{,}097\text{ flows/s}$ | **$98.4\,\text{J}$** |
| **NVIDIA RTX A4000** | 6,144 CUDA Cores | 128 | **$2.1\,\text{seconds}$** | $11{,}904\text{ flows/s}$ | $147.0\,\text{J}$ |
| **NVIDIA L4 Enterprise** | Ada Lovelace GPU | 256 | **$1.8\,\text{seconds}$** | **$13{,}888\text{ flows/s}$**| **$112.5\,\text{J}$** |

---

## 2. Key Takeaways

1. **Edge CPU Feasibility:** Even on fanless edge hardware lacking a discrete GPU (e.g., Intel Core Ultra or Rockchip), adaptation completes in **under 25 seconds**, easily fitting within an hourly adaptation cycle.
2. **Negligible Thermal Impact:** Consuming under $220\,\text{Joules}$ per adaptation cycle ensures edge appliances do not trigger thermal throttling.

