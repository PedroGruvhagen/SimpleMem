"""External integrations for SimpleMem"""

# OpenAI integration (primary)
from .openai import OpenAIClient, OpenAIClientManager

# OpenRouter integration (kept for backward compatibility)
from .openrouter import OpenRouterClient, OpenRouterClientManager

__all__ = [
    "OpenAIClient",
    "OpenAIClientManager",
    "OpenRouterClient",
    "OpenRouterClientManager",
]
