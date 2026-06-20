#!/usr/bin/env python3
"""
Odoo Debug MAS - Multi-Agent Debugging Framework for Odoo Modules
=================================================================
Entry point for running debugging and evaluation.

Usage:
  python main.py debug --traceback-file path/to/traceback.txt
  python main.py debug --traceback "ImportError: ..."
  python main.py evaluate --mode both
  python main.py evaluate --mode mas
  python main.py evaluate --mode single
"""

import argparse
import sys
import time
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph.mas_graph import build_mas_graph
from graph.single_agent_graph import build_single_agent_graph
from evaluation.evaluator import run_evaluation


def cmd_debug(args):
    """Run debugging on a single traceback."""
    if args.traceback_file:
        with open(args.traceback_file, "r", encoding="utf-8") as f:
            traceback_text = f.read().strip()
    elif args.traceback:
        traceback_text = args.traceback
    else:
        print("Error: provide --traceback or --traceback-file")
        sys.exit(1)

    mode = args.agent or "mas"
    print(f"\n{'='*60}")
    print(f"Odoo Debug MAS - {mode.upper()} mode")
    print(f"{'='*60}\n")

    if mode == "mas":
        graph = build_mas_graph()
    else:
        graph = build_single_agent_graph()

    initial_state = {
        "traceback": traceback_text,
        "start_time": time.time(),
        "end_time": 0.0,
        "retry_count": 0,
    }

    print(f"Input traceback:\n{traceback_text[:200]}...\n")
    print("Running agents...\n")

    result = graph.invoke(initial_state)

    resolution_time = result.get("end_time", 0) - result.get("start_time", 0)

    print(f"{'='*60}")
    print("RESULT")
    print(f"{'='*60}")
    print(f"Error Type:       {result.get('error_type', 'N/A')}")
    print(f"File:             {result.get('file_path', 'N/A')}")
    print(f"Root Cause:       {result.get('root_cause', 'N/A')}")
    print(f"Doc Verification: {result.get('doc_verification', 'N/A')}")
    print(f"Resolution Time:  {resolution_time:.2f}s")
    print(f"\nRecommendation:\n{result.get('recommendation', 'N/A')}")


def cmd_evaluate(args):
    """Run evaluation on dataset."""
    run_evaluation(mode=args.mode)


def main():
    parser = argparse.ArgumentParser(description="Odoo Debug MAS Framework")
    subparsers = parser.add_subparsers(dest="command")

    # debug subcommand
    debug_parser = subparsers.add_parser("debug", help="Debug a single traceback")
    debug_parser.add_argument("--traceback", type=str, help="Traceback text")
    debug_parser.add_argument("--traceback-file", type=str, help="Path to file containing traceback")
    debug_parser.add_argument("--agent", choices=["mas", "single"], default="mas", help="Agent mode")
    debug_parser.set_defaults(func=cmd_debug)

    # evaluate subcommand
    eval_parser = subparsers.add_parser("evaluate", help="Run evaluation on dataset")
    eval_parser.add_argument("--mode", choices=["mas", "single", "both"], default="both", help="Evaluation mode")
    eval_parser.set_defaults(func=cmd_evaluate)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
