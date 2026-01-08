# FortiPrompt - RAG Security Red Team Framework

FortiPrompt is an automated prompt injection framework designed for red team security assessments against Retrieval-Augmented Generation (RAG) chatbots and AI systems. It implements evolutionary adversarial testing using GAN-inspired techniques to systematically identify and exploit vulnerabilities in prompt-based AI applications.

## Features

- **Automated Attack Generation**: Uses advanced language models to generate sophisticated prompt injection attacks
- **Evolutionary Testing Loop**: Implements GAN-inspired adversarial optimization to iteratively improve attack effectiveness
- **Multiple Attack Types**: Supports direct injection, jailbreak attempts, context manipulation, and RAG-specific attacks
- **RAG Poisoning Testing**: Specialized module for testing document poisoning vulnerabilities in RAG systems
- **Comprehensive Evaluation**: Built-in metrics calculation and reporting with visualization capabilities
- **Flexible Configuration**: JSON-based configuration system for complex test scenarios
- **Interactive Mode**: User-friendly interactive configuration for quick testing

## Architecture

The framework consists of several key components:

- **Core Modules**:
  - `attack_generator.py`: Generates adversarial prompts using language models
  - `orchestrator.py`: Manages the evolutionary testing campaign
  - `response_analyzer.py`: Analyzes target responses for attack success
  - `target_interface.py`: Handles communication with target systems

- **RAG Poisoning**:
  - `document_generator.py`: Creates poisoned documents for RAG injection testing
  - `injection_tester.py`: Tests indirect injection through document poisoning

- **Evaluation**:
  - `metrics.py`: Calculates security metrics and success rates
  - `reporting.py`: Generates comprehensive test reports and visualizations

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AlexJoaquimPereira/FortiPrompt-redteam.git
cd FortiPrompt-redteam
```

2. Install dependencies:
```bash
pip install -r requirement.txt
```

3. Set up environment variables (create `.env` file):
```
OLLAMA_BASE_URL=http://localhost:11434
BACKEND_API_URL=http://your-target-api.com
```

## Usage

### Quick Test
Run a simple test with a single objective:
```bash
python main.py --quick --objective "reveal sensitive information"
```

### Configuration-Based Testing
Run tests using predefined configurations:
```bash
python main.py --config configs/basic_test.json --backend-url http://your-api.com
```

### Interactive Mode
Configure tests interactively:
```bash
python main.py --interactive
```

### Comparison Mode
Compare multiple configurations:
```bash
python main.py --compare --configs "configs/basic_test.json,configs/comprehensive_test.json"
```

## Configuration

Configuration files are JSON-based and support:

- Test objectives
- Attack types (direct, jailbreak, context, rag)
- Evolutionary parameters (generations, population size)
- RAG testing settings
- Target system specifications

Example configuration:
```json
{
  "name": "Basic Security Test",
  "objectives": ["reveal salary information", "bypass content filters"],
  "attack_types": ["direct", "jailbreak"],
  "max_generations": 3,
  "population_size": 9,
  "enable_rag_testing": false
}
```

## Attack Types

- **Direct Injection**: Attempts to override system prompts directly
- **Jailbreak**: Tries to coerce the model into breaking its guidelines
- **Context Manipulation**: Exploits context window vulnerabilities
- **RAG Poisoning**: Indirect attacks through poisoned documents

## Output

Tests generate:
- Detailed attack logs
- Success metrics and statistics
- Visual performance charts
- Comprehensive HTML reports
- JSON result exports

## Dependencies

- requests==2.31.0
- ollama==0.1.6
- numpy==1.24.3
- python-dotenv==1.0.0
- matplotlib==3.7.1
- pandas==2.0.3
- tqdm==4.65.0

## Security Notice

This tool is designed for authorized security testing only. Use responsibly and ensure you have explicit permission to test target systems. The authors are not responsible for misuse.

## Contributing

Contributions are welcome! Please ensure all changes include appropriate tests and documentation.

## License

[Add appropriate license information]</content>
<parameter name="filePath">c:\Users\ASUS\OneDrive\Desktop\fproj2\fortiprompt\README.md