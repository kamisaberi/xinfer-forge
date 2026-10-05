1. Install dependencies:

    ```
    cd /home/kami/blackbox-sentinel/xinfer-forge   # Or your project directory
    pip install -r requirements.txt```

2. Execute the adaptation pipeline:
    ```
    ./deploy/run_adaptation.sh
    ```

### Output:
```
==========================================================
  xInfer Forge: Continuous Adaptation & SSL Engine        
==========================================================
[Collector] Collected 1000 ambient flow records.
[Trainer] Starting Self-Supervised Masked Autoencoding on 1000 local samples...
[Trainer] Epoch [1/10] - Reconstruction Loss: 0.045120
[Trainer] Epoch [5/10] - Reconstruction Loss: 0.008412
[Trainer] Epoch [10/10] - Reconstruction Loss: 0.001840
[Trainer] Local self-supervised adaptation completed successfully.
[Safety Gate] Evaluating adapted model against non-negotiable Golden Attacks...
  PASS: ATTACK_PORTSCAN_SYN - Threat Score: 0.941 >= 0.80
  PASS: ATTACK_MODBUS_UNAUTHORIZED_WRITE - Threat Score: 0.962 >= 0.85
[Safety Gate] VALIDATION PASSED. Detection rate: 100.0%. Safe to deploy.
[Exporter] Compiling adapted PyTorch model to ONNX: models/network_threat_v2.onnx ...
[Exporter] Export complete. Binary size: 8420 bytes.
[Dispatcher] Triggering zero-downtime hot-reload at http://localhost:8443/api/v1/control/reload-model ...
[Dispatcher] Sentinel successfully hot-reloaded model: models/network_threat_v2.onnx!
==========================================================
  Adaptation Cycle Complete: Model Deployed with Zero Lag 
==========================================================
```


