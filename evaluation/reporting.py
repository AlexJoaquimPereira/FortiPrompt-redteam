"""
FortiPrompt Reporting & Visualization
"""

import json
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, List

from .metrics import SecurityMetrics, MetricsCalculator


class ReportGenerator:
    """Generate security assessment reports"""

    def __init__(self):
        self.calculator = MetricsCalculator()

    def generate_report(self, metrics: SecurityMetrics, test_name: str) -> str:
        return f"""
{'='*80}
FORTIPROMPT SECURITY ASSESSMENT REPORT
{'='*80}

Test Name: {test_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Overall Security Score: {metrics.security_score:.1f}/100
Attack Success Rate: {metrics.attack_success_rate:.1%}
Successful Attacks: {metrics.successful_attacks}/{metrics.total_attacks}

Information Leakage Incidents: {metrics.total_leakage_incidents}
Policy Violations: {metrics.policy_violations}
Behavioral Deviation: {metrics.avg_behavioral_deviation:.2f}

Indirect Injection Success: {metrics.indirect_injection_success_rate:.1%}
Document Poisoning Effectiveness: {metrics.document_poisoning_effectiveness:.2f}
{'='*80}
"""

    def export_json(self, metrics: SecurityMetrics, path: str):
        with open(path, "w") as f:
            json.dump(metrics.to_dict(), f, indent=2)

    def visualize(self, metrics: SecurityMetrics, generation_stats: List[Dict] = None):
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(["Security Score"], [metrics.security_score])
        ax.set_xlim(0, 100)
        ax.set_title("FortiPrompt Security Score")
        return fig
