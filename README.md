## FortiPrompt RedTeam: Automated Adversarial Prompt Generation and Synthetic Dataset Creation

**Lead:** Alex Joaquim Pereira (22B-CO-006)  
**Part of the FortiPrompt research project** – Goa Engineering College, November 2025  

### Overview
The `FortiPrompt-redteam` module constitutes the offensive security counterpart to the FortiPrompt multi-layered defense system. Its primary objectives are twofold:

1. **Automated Red-Teaming Framework**  
   Systematically generate and launch sophisticated prompt injection and jailbreak attacks against the FortiPrompt defense pipeline (and third-party LLM wrappers) to empirically measure Attack Success Rate (ASR), bypass rates per defense layer, and overall system resilience.

2. **Synthetic Dataset Generation**  
   Produce high-quality, labeled synthetic datasets of malicious and benign prompts for continual training and evaluation of FortiPrompt’s detection layers (Layer 1: anomaly detection; Layer 2: intent classification). Blocked adversarial prompts are automatically logged and transformed into training examples, enabling closed-loop improvement of the defense system.

### Key Features
- **Attack Simulation Engine**: Implements state-of-the-art black-box and white-box injection techniques, including adaptations of HOUYI-style context separation payloads [Liu et al., 2024], obfuscation (Base64, zero-width, Unicode normalization evasion), role-playing jailbreaks, and multi-turn attacks.
- **GAN-inspired Prompt Generation** (planned): Integration of generative adversarial networks and LLM-based payload mutation for creating novel, hard-to-detect adversarial examples.
- **Evaluation Dashboard**: Automated ASR computation, per-layer bypass analysis, and comparative benchmarking against baseline defenses.
- **Dataset Synthesis Pipeline**: Converts successful and failed attack logs into structured JSONL datasets with labels (`benign`, `direct_injection`, `context_separation`, `jailbreak`, etc.) suitable for fine-tuning embedding models and classifiers.
- **Responsible Disclosure Compliance**: All experiments are conducted in isolated environments; no real-world services are targeted without explicit authorization.

### Architecture (Red-Teaming Loop)
<img width="2016" height="2112" alt="redteam_diagram" src="https://github.com/user-attachments/assets/515e3424-d4ff-45f0-8321-38cfd77632b9" />


### Citation
When referencing this component in publications or reports:

> “FortiPrompt RedTeam: Automated Adversarial Testing and Synthetic Dataset Generation Module,” in *FortiPrompt: Detection and Defense Against Prompt Injection and Adversarial Prompt Attacks in Large Language Models*, Goa Engineering College, November 2025.

### References
- Perez, F., & Ribeiro, I. (2022). Ignore Previous Prompt: Attack Techniques For Language Models. arXiv preprint arXiv:2211.09527.
- Liu, Y., et al. (2024). Automatic and Universal Prompt Injection Attacks against Large Language Models. arXiv preprint arXiv:2403.04957.
- Wei, A., et al. (2023). Jailbroken: How Does LLM Safety Training Fail? arXiv preprint arXiv:2307.02483.
- Zhang, Y., et al. (2024). Evolving Security in LLMs: A Study of Jailbreak Attacks and Defenses. arXiv preprint arXiv:2402.11814.
- Sanh, V., et al. (2019). DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter. arXiv preprint arXiv:1910.01108.
- Xu, Z., et al. (2024). JailbreakTracer: Feature-Based Detection of Jailbreak Prompts. Proceedings of ACM CCS 2024.
- JailbreakHub. (2024). Community-driven repository of LLM jailbreak prompts. Hugging Face. https://huggingface.co/datasets/jailbreakhub
- Zou, A., et al. (2023). Universal and Transferable Adversarial Attacks on Aligned Language Models. arXiv preprint arXiv:2307.15043.
- Malicious Prompt Detection Dataset. (2024). Kaggle. https://www.kaggle.com/datasets/malicious-prompts
- Bhatt, M., et al. (2024). CySecBench: Generative AI-based Cybersecurity-focused Prompt Dataset. arXiv preprint arXiv:2408.08810.
- Liu, Y., et al. (2024). Automatic and Universal Prompt Injection Attacks against Large Language Models. arXiv preprint arXiv:2403.04957.
- Robey, A., et al. (2023). SmoothLLM: Defending Large Language Models Against Jailbreaking Attacks. arXiv preprint arXiv:2310.03684.
- Zhang, S., et al. (2024). Defending Large Language Models from Jailbreak Attacks via Layer-specific Editing. USENIX Security 2025.
- Zhang, Y., et al. (2024). Evolving Security in LLMs: A Study of Jailbreak Attacks and Defenses. arXiv preprint arXiv:2402.11814.

This module transforms FortiPrompt from a purely defensive system into a complete adversarial robustness research platform, aligning with contemporary red-teaming practices in LLM security [Chao et al., 2024; Xu et al., 2025].
