#!/usr/bin/env python3
import argparse
from forge.main import run_adaptation_cycle
from forge.quantization.ptq_engine import PtqQuantizationEngine
from forge.adaptation.finetune_engine import FinetuneEngine


def main():
    parser = argparse.ArgumentParser(description="xInfer Forge CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Command 1: run (Full background adaptation cycle)
    run_parser = subparsers.add_parser("run", help="Execute an adaptation and fine-tuning cycle")
    run_parser.add_argument("--config", default="configs/forge_config.yaml", help="Path to configuration YAML")

    # Command 2: quantize (INT8 PTQ Quantization)
    quant_parser = subparsers.add_parser("quantize", help="Execute Post-Training Quantization (PTQ) to INT8 ONNX")
    quant_parser.add_argument("--model", required=True, help="Path to input FP32 ONNX model")
    quant_parser.add_argument("--output", default="models/model_int8.onnx", help="Path to output INT8 ONNX model")
    quant_parser.add_argument("--config", default="configs/quantization_profile.yaml", help="Path to quantization profile YAML")
    quant_parser.add_argument("--dim", type=int, default=32, help="Feature dimension count D")
    quant_parser.add_argument("--min-recall", type=float, default=None, help="Custom Golden Gate minimum recall threshold (e.g. 0.990)")

    # Command 3: finetune (Incremental Continual Learning on New Field Telemetry)
    ft_parser = subparsers.add_parser("finetune", help="Fine-tune a pre-trained model on newly captured SLAB telemetry")
    ft_parser.add_argument("--base-model", required=True, help="Path to base pre-trained ONNX/PyTorch model")
    ft_parser.add_argument("--dataset", required=True, help="Path to newly captured .slab telemetry dataset")
    ft_parser.add_argument("--output", default="models/model_finetuned.onnx", help="Path to output adapted ONNX model")
    ft_parser.add_argument("--epochs", type=int, default=5, help="Number of fine-tuning epochs (default: 5)")
    ft_parser.add_argument("--lr", type=float, default=0.0001, help="Fine-tuning learning rate (default: 0.0001)")
    ft_parser.add_argument("--auto-quantize", action="store_true", default=True, help="Automatically quantize adapted model to INT8")
    ft_parser.add_argument("--min-recall", type=float, default=0.990, help="Custom Golden Gate minimum recall threshold (default: 0.990)")
    ft_parser.add_argument("--config", default="configs/finetune_profile.yaml", help="Path to finetune configuration YAML")

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
    elif args.command == "finetune":
        engine = FinetuneEngine(config_path=args.config)
        success, msg = engine.finetune_model(
            base_model_path=args.base_model,
            dataset_slab_path=args.dataset,
            output_model_path=args.output,
            epochs=args.epochs,
            lr=args.lr,
            auto_quantize=args.auto_quantize,
            min_recall=args.min_recall
        )
        if success:
            print(f"[+] Fine-tuning successful: {msg}")
        else:
            print(f"[-] Fine-tuning failed: {msg}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()