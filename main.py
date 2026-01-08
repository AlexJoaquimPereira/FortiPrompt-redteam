"""
FortiPrompt Main Entry Point
File: FortiPrompt/main.py

Run red team security assessments against your RAG chatbot
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add core modules to path
sys.path.append(str(Path(__file__).parent))

from core.target_interface import TargetSystemInterface, EnhancedTargetInterface
from core.orchestrator import RedTeamOrchestrator
from core.attack_generator import AttackGenerator
from core.response_analyzer import ResponseAnalyzer
from rag_poisoning.document_generator import RAGPoisoningGenerator
from rag_poisoning.injection_tester import RAGInjectionTester
from evaluation.metrics import MetricsCalculator
from evaluation.reporting import ReportGenerator
from utils.attack_types import AttackType
from utils.config import load_config, save_results


def print_banner():
    """Print FortiPrompt banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║              ███████╗ ██████╗ ██████╗ ████████╗██╗       ║
    ║              ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██║       ║
    ║              █████╗  ██║   ██║██████╔╝   ██║   ██║       ║
    ║              ██╔══╝  ██║   ██║██╔══██╗   ██║   ██║       ║
    ║              ██║     ╚██████╔╝██║  ██║   ██║   ██║       ║
    ║              ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝       ║
    ║                                                           ║
    ║         FortiPrompt - RAG Security Red Team               ║
    ║         Automated Prompt Injection Framework              ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_quick_test(args):
    """Run a quick test with minimal configuration"""
    print_banner()
    print("\n[QUICK TEST MODE]")
    print(f"Objective: {args.objective}")
    print(f"Backend: {args.backend_url}\n")
    
    # Initialize components
    target = EnhancedTargetInterface(base_url=args.backend_url)
    generator = AttackGenerator(model_name=args.model)
    analyzer = ResponseAnalyzer(model_name=args.model)
    
    # Create orchestrator
    orchestrator = RedTeamOrchestrator(
        generator=generator,
        analyzer=analyzer,
        target=target
    )
    
    # Run quick campaign
    attack_types = [
        AttackType.DIRECT_INJECTION,
        AttackType.JAILBREAK
    ]
    
    results = orchestrator.run_campaign(
        objective=args.objective,
        attack_types=attack_types,
        max_generations=2,
        population_size=6
    )
    
    # Calculate metrics
    calculator = MetricsCalculator()
    metrics = calculator.calculate_metrics(
        direct_attack_results=results['attacks'],
        generation_stats=results['generation_stats']
    )
    
    # Generate report
    reporter = ReportGenerator()
    report = reporter.generate_report(
        metrics=metrics,
        test_name="Quick Test"
    )
    
    print("\n" + report)
    
    # Save results
    output_dir = Path(args.output_dir) / f"quick_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    save_results(output_dir, results, metrics, report)
    
    print(f"\n✓ Results saved to: {output_dir}")
    
    target.print_statistics()


def run_config_test(args):
    """Run test from configuration file"""
    print_banner()
    
    # Load configuration
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"✗ Configuration file not found: {config_path}")
        return
    
    config = load_config(config_path)
    
    print(f"\n[RUNNING: {config['name']}]")
    print(f"Configuration: {config_path}")
    print(f"Backend: {args.backend_url}\n")
    
    # Initialize components
    target = EnhancedTargetInterface(base_url=args.backend_url)
    generator = AttackGenerator(model_name=args.model)
    analyzer = ResponseAnalyzer(model_name=args.model)
    
    orchestrator = RedTeamOrchestrator(
        generator=generator,
        analyzer=analyzer,
        target=target
    )
    
    # Parse attack types
    attack_types = [AttackType[at.upper()] for at in config['attack_types']]
    
    # Phase 1: Direct attacks
    print("="*60)
    print("PHASE 1: DIRECT PROMPT INJECTION")
    print("="*60)
    
    all_results = []
    all_gen_stats = []
    
    for objective in config['objectives']:
        print(f"\n[Objective] {objective}")
        
        results = orchestrator.run_campaign(
            objective=objective,
            attack_types=attack_types,
            max_generations=config['max_generations'],
            population_size=config['population_size']
        )
        
        all_results.extend(results['attacks'])
        all_gen_stats.extend(results['generation_stats'])
    
    # Phase 2: RAG poisoning (if enabled)
    indirect_results = []
    
    if config.get('enable_rag_testing', False):
        print("\n" + "="*60)
        print("PHASE 2: RAG DOCUMENT POISONING")
        print("="*60)
        
        rag_generator = RAGPoisoningGenerator(model_name=args.model)
        rag_tester = RAGInjectionTester(target, rag_generator)
        
        rag_report = rag_tester.run_rag_poisoning_campaign(
            topics=config.get('rag_topics', []),
            injection_objectives=config['objectives'],
            test_queries=config.get('test_queries', [])
        )
        
        indirect_results = rag_report['test_results']
        
        print(f"\n✓ RAG Tests Complete")
        print(f"  Documents: {rag_report['total_documents']}")
        print(f"  Tests: {rag_report['total_tests']}")
        print(f"  Successful: {rag_report['successful_injections']}")
    
    # Phase 3: Metrics & Reporting
    print("\n" + "="*60)
    print("PHASE 3: EVALUATION & REPORTING")
    print("="*60)
    
    calculator = MetricsCalculator()
    metrics = calculator.calculate_metrics(
        direct_attack_results=all_results,
        indirect_attack_results=indirect_results,
        generation_stats=all_gen_stats
    )
    
    reporter = ReportGenerator()
    report = reporter.generate_report(
        metrics=metrics,
        test_name=config['name']
    )
    
    print("\n" + report)
    
    # Save results
    output_dir = Path(args.output_dir) / f"{config['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    full_results = {
        'config': config,
        'direct_attacks': [r.__dict__ for r in all_results],
        'indirect_attacks': indirect_results,
        'metrics': metrics.to_dict(),
        'generation_stats': all_gen_stats
    }
    
    save_results(output_dir, full_results, metrics, report)
    
    # Generate visualization
    try:
        reporter.create_visualization(
            metrics=metrics,
            generation_stats=all_gen_stats,
            output_path=output_dir / 'visualization.png'
        )
        print(f"✓ Visualization saved")
    except Exception as e:
        print(f"⚠ Could not generate visualization: {e}")
    
    print(f"\n✓ All results saved to: {output_dir}")
    
    target.print_statistics()


def run_interactive_mode(args):
    """Run interactive test configuration"""
    print_banner()
    print("\n[INTERACTIVE MODE]")
    print("Configure your red team test interactively\n")
    
    # Get test details
    test_name = input("Test name: ").strip() or "Interactive Test"
    
    print("\nObjectives (comma-separated):")
    print("  Example: reveal salary, bypass policies")
    objectives_input = input("> ").strip()
    objectives = [obj.strip() for obj in objectives_input.split(',')]
    
    print("\nAttack types (space-separated):")
    print("  Options: direct jailbreak context rag")
    attack_input = input("> ").strip() or "direct jailbreak"
    attack_types = [
        AttackType[at.upper().replace('-', '_').replace('DIRECT', 'DIRECT_INJECTION')]
        for at in attack_input.split()
    ]
    
    max_gen = int(input("\nMax generations [3]: ").strip() or "3")
    pop_size = int(input("Population size [9]: ").strip() or "9")
    
    enable_rag = input("\nEnable RAG testing? (y/n) [n]: ").strip().lower() == 'y'
    
    rag_topics = []
    test_queries = []
    
    if enable_rag:
        print("\nRAG topics (comma-separated):")
        topics_input = input("> ").strip()
        rag_topics = [t.strip() for t in topics_input.split(',')]
        
        print("\nTest queries (comma-separated):")
        queries_input = input("> ").strip()
        test_queries = [q.strip() for q in queries_input.split(',')]
    
    # Create config
    config = {
        'name': test_name,
        'objectives': objectives,
        'attack_types': [at.value for at in attack_types],
        'max_generations': max_gen,
        'population_size': pop_size,
        'enable_rag_testing': enable_rag,
        'rag_topics': rag_topics,
        'test_queries': test_queries
    }
    
    # Save config
    config_dir = Path('configs')
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / f"{test_name.replace(' ', '_').lower()}.json"
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✓ Configuration saved to: {config_file}")
    print("\nStarting test...\n")
    
    # Run test
    args.config = str(config_file)
    run_config_test(args)


def run_comparison(args):
    """Compare multiple configurations"""
    print_banner()
    print("\n[COMPARISON MODE]")
    
    config_files = args.configs.split(',')
    
    print(f"Comparing {len(config_files)} configurations:")
    for cf in config_files:
        print(f"  - {cf}")
    print()
    
    all_results = []
    
    for config_file in config_files:
        config_file = config_file.strip()
        print(f"\n{'='*60}")
        print(f"Running: {config_file}")
        print('='*60)
        
        args.config = config_file
        # Store original output dir
        original_output = args.output_dir
        # Run test
        run_config_test(args)
        # Restore output dir
        args.output_dir = original_output
    
    print("\n" + "="*60)
    print("COMPARISON COMPLETE")
    print("="*60)
    print("\nCheck individual result directories for details")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='FortiPrompt - Red Team Framework for RAG Systems',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test
  python main.py --quick --objective "reveal salary information"
  
  # Run from config
  python main.py --config configs/basic_test.json
  
  # Interactive mode
  python main.py --interactive
  
  # Compare configs
  python main.py --compare --configs "configs/basic.json,configs/advanced.json"
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--quick', action='store_true',
                           help='Run quick test mode')
    mode_group.add_argument('--config', type=str,
                           help='Path to test configuration file')
    mode_group.add_argument('--interactive', action='store_true',
                           help='Interactive test configuration')
    mode_group.add_argument('--compare', action='store_true',
                           help='Compare multiple configurations')
    
    # Quick test options
    parser.add_argument('--objective', type=str,
                       default='reveal sensitive information',
                       help='Objective for quick test')
    
    # Comparison options
    parser.add_argument('--configs', type=str,
                       help='Comma-separated config files to compare')
    
    # Common options
    parser.add_argument('--backend-url', type=str,
                       default='http://localhost:8000',
                       help='URL of your RAG backend (default: http://localhost:8000)')
    parser.add_argument('--model', type=str,
                       default='llama2',
                       help='Ollama model to use (default: llama2)')
    parser.add_argument('--output-dir', type=str,
                       default='results',
                       help='Output directory for results')
    
    args = parser.parse_args()
    
    # Create output directory
    Path(args.output_dir).mkdir(exist_ok=True)
    
    try:
        if args.quick:
            run_quick_test(args)
        elif args.config:
            run_config_test(args)
        elif args.interactive:
            run_interactive_mode(args)
        elif args.compare:
            if not args.configs:
                print("Error: --configs required for comparison mode")
                return
            run_comparison(args)
    
    except KeyboardInterrupt:
        print("\n\n✗ Test interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()