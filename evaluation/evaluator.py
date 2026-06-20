from __future__ import annotations
import time
import os
import json
from config import Config
from graph.mas_graph import build_mas_graph
from graph.single_agent_graph import build_single_agent_graph
from evaluation.metrics import calculate_accuracy, calculate_resolution_time, calculate_relevance, save_results


def load_dataset(dataset_path: str) -> list[dict]:
    """Load test cases from dataset directory.
    Expected format: JSON file with list of {traceback, ground_truth, error_category}."""
    cases = []
    if os.path.isdir(dataset_path):
        for fname in sorted(os.listdir(dataset_path)):
            if fname.endswith(".json"):
                with open(os.path.join(dataset_path, fname), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        cases.extend(data)
                    elif isinstance(data, dict):
                        if "test_cases" in data:
                            cases.extend(data["test_cases"])
                        else:
                            cases.append(data)
    elif os.path.isfile(dataset_path) and dataset_path.endswith(".json"):
        with open(dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                cases = data
            elif isinstance(data, dict) and "test_cases" in data:
                cases = data["test_cases"]
    return cases


def run_single_case(graph, traceback: str) -> dict:
    """Run a single test case through the given graph."""
    initial_state = {
        "traceback": traceback,
        "start_time": time.time(),
        "end_time": 0.0,
        "retry_count": 0,
    }
    result = graph.invoke(initial_state)
    resolution_time = result.get("end_time", 0) - result.get("start_time", 0)
    return {
        "error_type": result.get("error_type", ""),
        "file_path": result.get("file_path", ""),
        "root_cause": result.get("root_cause", ""),
        "recommendation": result.get("recommendation", ""),
        "resolution_time": round(resolution_time, 2),
    }


def run_evaluation(mode: str = "both") -> dict:
    """Run evaluation comparing MAS vs single-agent.
    mode: 'mas', 'single', or 'both'."""
    dataset_path = Config.DATASET_PATH
    results_path = Config.RESULTS_PATH
    os.makedirs(results_path, exist_ok=True)

    cases = load_dataset(dataset_path)
    if not cases:
        print(f"[WARNING] No test cases found in {dataset_path}")
        print("Place JSON files with test cases in the dataset/ directory.")
        print("Format: [{\"traceback\": \"...\", \"ground_truth\": \"...\", \"error_category\": \"...\"}]")
        return {}

    mas_results = []
    single_results = []

    if mode in ("mas", "both"):
        print(f"\n{'='*60}")
        print("Running Multi-Agent System evaluation...")
        print(f"{'='*60}")
        mas_graph = build_mas_graph()
        for i, case in enumerate(cases, 1):
            print(f"  Case {i}/{len(cases)}: {case.get('error_category', 'unknown')}...")
            result = run_single_case(mas_graph, case["traceback"])
            result["ground_truth"] = case.get("ground_truth", "")
            result["error_category"] = case.get("error_category", "")
            result["case_id"] = i
            mas_results.append(result)
        save_results(mas_results, os.path.join(results_path, "mas_results.json"))

    if mode in ("single", "both"):
        print(f"\n{'='*60}")
        print("Running Single-Agent evaluation...")
        print(f"{'='*60}")
        single_graph = build_single_agent_graph()
        for i, case in enumerate(cases, 1):
            print(f"  Case {i}/{len(cases)}: {case.get('error_category', 'unknown')}...")
            result = run_single_case(single_graph, case["traceback"])
            result["ground_truth"] = case.get("ground_truth", "")
            result["error_category"] = case.get("error_category", "")
            result["case_id"] = i
            single_results.append(result)
        save_results(single_results, os.path.join(results_path, "single_results.json"))

    summary = {}
    if mas_results:
        summary["mas"] = {
            "accuracy": calculate_accuracy(mas_results),
            "avg_resolution_time": calculate_resolution_time(mas_results),
            "avg_relevance": calculate_relevance(mas_results),
            "total_cases": len(mas_results),
        }
    if single_results:
        summary["single_agent"] = {
            "accuracy": calculate_accuracy(single_results),
            "avg_resolution_time": calculate_resolution_time(single_results),
            "avg_relevance": calculate_relevance(single_results),
            "total_cases": len(single_results),
        }

    summary_path = os.path.join(results_path, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print("EVALUATION SUMMARY")
    print(f"{'='*60}")
    for mode_name, metrics in summary.items():
        print(f"\n  {mode_name.upper()}:")
        print(f"    Accuracy:         {metrics['accuracy']:.1f}%")
        print(f"    Avg Resolution:   {metrics['avg_resolution_time']:.2f}s")
        print(f"    Avg Relevance:    {metrics['avg_relevance']:.2f}/5")
        print(f"    Total Cases:      {metrics['total_cases']}")

    print(f"\nResults saved to: {results_path}")
    return summary
