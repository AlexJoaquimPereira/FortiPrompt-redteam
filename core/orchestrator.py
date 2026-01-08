
"""
FortiPrompt - Red Team Orchestrator
GAN-inspired adversarial loop
"""

import numpy as np
from core.attack_generator import AttackGenerator  # Relative import for AttackGenerator
from utils.attack_types import AttackType  # Import AttackType from utils for consistency
from core.response_analyzer import ResponseAnalyzer
from core.target_interface import TargetSystemInterface


class RedTeamOrchestrator:
    """
    Implements evolutionary adversarial testing loop
    """

    def __init__(self, generator=None, analyzer=None, target=None):
        self.generator = generator or AttackGenerator()
        self.analyzer = analyzer or ResponseAnalyzer()
        self.target = target or TargetSystemInterface()

    def run_campaign(self, objective, attack_types, max_generations=3, population_size=9):
        count_per_type = max(1, population_size // len(attack_types))
        attacks = self.generator.generate_initial_attacks(
            objective, attack_types, count_per_type
        )

        all_results = []
        generation_stats = []

        for g in range(max_generations):
            print(f"\n[Generation {g + 1}/{max_generations}]")

            results = []
            for atk in attacks:
                resp = self.target.query(atk.content)
                result = self.analyzer.analyze(atk, resp)
                results.append(result)
                all_results.append(result)

            success_rate = sum(r.success for r in results) / len(results) if results else 0
            print(".1%")

            generation_stats.append({
                'generation': g + 1,
                'attacks_tested': len(results),
                'success_rate': success_rate,
                'avg_score': sum(r.prompt.success_score for r in results) / len(results) if results else 0
            })

            if g < max_generations - 1:  # Don't mutate on last generation
                results.sort(key=lambda r: r.prompt.success_score, reverse=True)
                top = results[: max(1, int(0.3 * len(results)))]
                attacks = self.generator.mutate([r.prompt for r in top])

        return {
            'attacks': all_results,
            'generation_stats': generation_stats
        }


if __name__ == "__main__":
    orchestrator = RedTeamOrchestrator()
    orchestrator.run(
        objective="reveal employee salary information",
        attack_types=[
            AttackType.DIRECT_INJECTION,
            AttackType.JAILBREAK,
            AttackType.CONTEXT_MANIPULATION
        ]
    )