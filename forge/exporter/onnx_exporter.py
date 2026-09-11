import os
import torch

class ONNXExporter:
    def __init__(self, config):
        self.config = config
        self.models_dir = config["appliance"]["models_dir"]
        self.output_filename = config["export"]["onnx_output_name"]
        os.makedirs(self.models_dir, exist_ok=True)

    def export(self, model):
        model.eval()
        input_dim = self.config["training"]["input_dim"]
        dummy_input = torch.randn(1, input_dim, dtype=torch.float32)

        output_path = os.path.join(self.models_dir, self.output_filename)
        print(f"[Exporter] Compiling adapted PyTorch model to ONNX: {output_path} ...")

        torch.onnx.export(
            model,
            dummy_input,
            output_path,
            export_params=True,
            opset_version=self.config["export"].get("opset_version", 17),
            do_constant_folding=True,
            input_names=['input'],
            output_names=['scores'],
            dynamic_axes={'input': {0: 'batch_size'}, 'scores': {0: 'batch_size'}}
        )

        file_size = os.path.getsize(output_path)
        print(f"[Exporter] Export complete. Binary size: {file_size} bytes.")
        return output_path