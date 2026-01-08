from enum import Enum

class AttackType(Enum):
    DIRECT_INJECTION = "direct_injection"
    RAG_POISONING = "rag_poisoning"
    JAILBREAK = "jailbreak"
    CONTEXT_MANIPULATION = "context_manipulation"
    MULTI_TURN = "multi_turn"