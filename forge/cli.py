#!/usr/bin/env python3
import argparse
from forge.main import run_adaptation_cycle

def main():
    parser = argparse.ArgumentParser(description="xInfer Forge CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Execute an adaptation and fine-tuning cycle")
    run_parser.add_argument("--config", default="configs/forge_config.yaml", help="Path to configuration YAML")

    args = parser.parse_args()

    if args.command == "run":
        run_adaptation_cycle(args.config)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()