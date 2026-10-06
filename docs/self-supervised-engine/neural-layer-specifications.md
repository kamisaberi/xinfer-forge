# Neural Layer Specifications: Projections & Activations

To ensure deterministic compilation to ONNX Opset 17 and hardware acceleration across edge NPUs (Intel OpenVINO, Rockchip RKNN, HailoRT), `xinfer-forge` utilizes standard mathematical operations without custom unquantizable layers.

---

## 1. Layer Architecture Specifications

| Layer Index | Operation | Input Shape | Output Shape | Parameters | Activation / Normalization |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Encoder 1** | `nn.Linear` | `[B, 32]` | `[B, 16]` | $32 \times 16 + 16 = 528$ | `LayerNorm(16)` + `LeakyReLU(0.1)` |
| **Encoder 2** | `nn.Linear` | `[B, 16]` | `[B, 8]` | $16 \times 8 + 8 = 136$ | `LayerNorm(8)` (Latent Bottleneck) |
| **Decoder 1** | `nn.Linear` | `[B, 8]` | `[B, 16]` | $8 \times 16 + 16 = 144$ | `LayerNorm(16)` + `LeakyReLU(0.1)` |
| **Decoder 2** | `nn.Linear` | `[B, 16]` | `[B, 32]` | $16 \times 32 + 32 = 544$ | Linear Identity (Output Reconstruction) |

$$\text{Total Trainable Weights} = 528 + 136 + 144 + 544 + \text{Norm Params} = 1{,}632 \text{ Parameters}$$

---

## 2. Activation Function Selection: LeakyReLU ($0.1$)

$$\text{LeakyReLU}(x) = \begin{cases} x, & \text{if } x \ge 0 \\ 0.1 \cdot x, & \text{if } x < 0 \end{cases}$$

Standard `ReLU` causes "dying neuron" syndrome during continual retraining on sparse tabular network data. `LeakyReLU(0.1)` maintains continuous gradient flow through negative activation values while mapping cleanly to edge integer quantization (INT8) primitives.

