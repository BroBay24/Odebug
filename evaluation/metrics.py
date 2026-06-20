from __future__ import annotations
import os
import json
import csv


def calculate_accuracy(results: list[dict]) -> float:
    """Calculate solution accuracy: proportion of cases correctly solved."""
    if not results:
        return 0.0
    correct = sum(1 for r in results if r.get("is_correct", False))
    return (correct / len(results)) * 100.0


def calculate_resolution_time(results: list[dict]) -> float:
    """Calculate average resolution time in seconds."""
    if not results:
        return 0.0
    times = [r.get("resolution_time", 0) for r in results if r.get("resolution_time")]
    return sum(times) / len(times) if times else 0.0


def calculate_relevance(results: list[dict]) -> float:
    """Calculate average relevance score (Likert 1-5)."""
    if not results:
        return 0.0
    scores = [r.get("relevance_score", 0) for r in results if r.get("relevance_score")]
    return sum(scores) / len(scores) if scores else 0.0


def save_results(results: list[dict], output_path: str):
    """Save evaluation results to JSON and CSV."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    csv_path = output_path.replace(".json", ".csv")
    if results:
        keys = results[0].keys()
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
