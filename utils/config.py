"""
FortiPrompt Configuration Utilities
Handles loading and saving of configuration and results
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List


def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Load configuration from JSON file
    
    Args:
        config_path: Path to the configuration JSON file
        
    Returns:
        Dictionary containing configuration data
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_results(output_dir: Path, results: List, metrics: Dict, report: str) -> None:
    """
    Save test results, metrics, and report to files
    
    Args:
        output_dir: Directory to save results in
        results: List of attack results
        metrics: Dictionary of calculated metrics
        report: Generated report string
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save results as JSON
    results_path = output_dir / 'results.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        # Convert results to serializable format
        serializable_results = []
        for result in results:
            if hasattr(result, '__dict__'):
                serializable_results.append(result.__dict__)
            elif hasattr(result, '_asdict'):
                serializable_results.append(result._asdict())
            else:
                serializable_results.append(result)
        json.dump(serializable_results, f, indent=2, default=str)
    
    # Save metrics as JSON
    metrics_path = output_dir / 'metrics.json'
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, default=str)
    
    # Save report as text
    report_path = output_dir / 'report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)