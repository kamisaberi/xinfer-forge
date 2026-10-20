#!/usr/bin/env python3
import argparse
from forge.main import run_adaptation_cycle
from forge.quantization.ptq_engine import PtqQuantizationEngine


def main():
    parser = argparse.ArgumentParser(description="xInfer Forge CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Execute an adaptation and fine-tuning cycle")
    run_parser.add_argument("--config", default="configs/forge_config.yaml", help="Path to configuration YAML")

    # Command: quantize
    quant_parser = subparsers.add_parser("quantize", help="Execute Post-Training Quantization (PTQ) to INT8 ONNX")
    quant_parser.add_argument("--model", required=True, help="Path to input FP32 ONNX model")
    quant_parser.add_argument("--output", default="models/model_int8.onnx", help="Path to output INT8 ONNX model")
    quant_parser.add_argument("--config", default="configs/quantization_profile.yaml", help="Path to quantization profile YAML")
    quant_parser.add_argument("--dim", type=int, default=32, help="Feature dimension count D")
    quant_parser.add_argument("--min-recall", type=float, default=None, help="Custom Golden Gate minimum recall threshold (e.g. 0.999)")

    args = parser.parse_args()

    if args.command == "run":
        run_adaptation_cycle(args.config)
    elif args.command == "quantize":
        engine = PtqQuantizationEngine(config_path=args.config)
        success, msg = engine.quantize_model(args.model, args.output, input_dim=args.dim, custom_min_recall=args.min_recall)
        if success:
            print(f"[+] Quantization successful: {msg}")
        else:
            print(f"[-] Quantization failed: {msg}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()