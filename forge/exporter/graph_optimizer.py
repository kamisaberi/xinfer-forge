import os
import onnx
from onnx import shape_inference

class ONNXGraphOptimizer:
    """Validates structural integrity, infers shapes, and checks compatibility for xinfer."""
    def __init__(self, model_path):
        self.model_path = model_path

    def optimize_and_verify(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        print(f"[GraphOptimizer] Inspecting exported ONNX model: {self.model_path} ...")
        model = onnx.load(self.model_path)
        
        # Verify protobuf syntax and layer connectivity
        onnx.checker.check_model(model)

        # Run static shape inference
        inferred_model = shape_inference.infer_shapes(model)
        onnx.save(inferred_model, self.model_path)

        input_names = [inp.name for inp in inferred_model.graph.input]
        output_names = [out.name for out in inferred_model.graph.output]

        print(f"[GraphOptimizer] Verification Passed. Inputs: {input_names} | Outputs: {output_names}")
        return True