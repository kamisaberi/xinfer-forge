import unittest
import os
from forge.models.autoencoder import NetworkAnomalyAutoencoder
from forge.exporter.onnx_exporter import ONNXExporter
from forge.exporter.graph_optimizer import ONNXGraphOptimizer

class TestONNXExportPipeline(unittest.TestCase):
    def test_export_and_optimize(self):
        config = {
            "training": {"input_dim": 32},
            "appliance": {"models_dir": "/tmp/test_models"},
            "export": {"onnx_output_name": "unit_test_model.onnx", "opset_version": 17}
        }
        model = NetworkAnomalyAutoencoder(input_dim=32)
        exporter = ONNXExporter(config)
        output_path = exporter.export(model)

        self.assertTrue(os.path.exists(output_path))
        
        optimizer = ONNXGraphOptimizer(output_path)
        self.assertTrue(optimizer.optimize_and_verify())

        # Cleanup
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == '__main__':
    unittest.main()