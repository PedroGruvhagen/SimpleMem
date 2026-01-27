"""
Unified API Client - Interface for LLM and Embedding operations
Supports both OpenRouter and OpenAI APIs through configuration.

- OpenRouter: Use base_url="https://openrouter.ai/api/v1" with sk-or- keys
- OpenAI: Use base_url="https://api.openai.com/v1" with sk- or sk-proj- keys

Synchronous implementation optimized for Claude Skills.
"""

import json
import re
from typing import List, Dict, Any, Optional


class OpenRouterClient:
    """
    Unified API client for LLM and Embedding operations.
    Supports both OpenRouter and OpenAI APIs through configuration.

    OpenRouter: Use base_url="https://openrouter.ai/api/v1" with sk-or- keys
    OpenAI: Use base_url="https://api.openai.com/v1" with sk- or sk-proj- keys

    Synchronous implementation optimized for Claude Skills.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        llm_model: str = "openai/gpt-4.1-mini",
        embedding_model: str = "qwen/qwen3-embedding-8b",
        app_name: str = "SimpleMem Skill",
    ):
        """
        Initialize API client

        Args:
            api_key: API key (OpenRouter: sk-or-, OpenAI: sk- or sk-proj-)
            base_url: API base URL (OpenRouter or OpenAI)
            llm_model: Model for chat completions
            embedding_model: Model for embeddings
            app_name: Application name for tracking (OpenRouter only)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.app_name = app_name

        # Use requests for synchronous HTTP calls
        import requests
        self.session = requests.Session()

        # Base headers for all providers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # OpenRouter-specific headers (only for sk-or- keys)
        if self.api_key and self.api_key.startswith("sk-or-"):
            headers["HTTP-Referer"] = "http://simplemem.cloud"
            headers["X-Title"] = self.app_name

        self.session.headers.update(headers)

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None,
    ) -> str:
        """
        Call LLM for chat completion

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            response_format: Optional response format (e.g., {"type": "json_object"})

        Returns:
            Generated text content
        """
        payload = {
            "model": self.llm_model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        if response_format:
            payload["response_format"] = response_format

        url = f"{self.base_url}/chat/completions"
        response = self.session.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

    def create_embedding(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        """
        Create embeddings for texts

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        payload = {
            "model": self.embedding_model,
            "input": texts,
        }

        url = f"{self.base_url}/embeddings"
        response = self.session.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        # Sort by index to ensure correct order
        embeddings_data = sorted(data["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in embeddings_data]

    def create_single_embedding(self, text: str) -> List[float]:
        """Create embedding for a single text"""
        embeddings = self.create_embedding([text])
        return embeddings[0]

    def verify_api_key(self) -> tuple[bool, Optional[str]]:
        """
        Verify that the API key is valid.
        Works with both OpenRouter (sk-or-*) and OpenAI (sk-*, sk-proj-*) keys.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.api_key:
            return False, "API key is required"

        try:
            # OpenRouter validation: use /auth/key endpoint
            if self.api_key.startswith("sk-or-"):
                url = f"{self.base_url}/auth/key"
                response = self.session.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    if data.get("data"):
                        return True, None
                    return False, "Invalid API key"
                elif response.status_code == 401:
                    return False, "Invalid or expired API key"
                elif response.status_code == 403:
                    return False, "API key access denied"
                else:
                    return False, f"API error: {response.status_code}"

            # OpenAI validation: use /models endpoint (no /auth/key)
            else:
                url = f"{self.base_url}/models"
                response = self.session.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    if data.get("data") and len(data["data"]) > 0:
                        return True, None
                    return False, "API key valid but no models accessible"
                elif response.status_code == 401:
                    return False, "Invalid OpenAI API key. Get yours at platform.openai.com/api-keys"
                elif response.status_code == 403:
                    return False, "API key access denied"
                else:
                    return False, f"API error: {response.status_code}"

        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def extract_json(self, text: str) -> Any:
        """
        Extract JSON from LLM response text with robust parsing

        Args:
            text: Raw text that may contain JSON

        Returns:
            Parsed JSON object
        """
        if not text:
            return None

        # Strategy 1: Direct JSON parsing
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        # Strategy 2: Extract from ```json ``` blocks
        json_block_pattern = r"```json\s*([\s\S]*?)\s*```"
        matches = re.findall(json_block_pattern, text, re.IGNORECASE)
        if matches:
            try:
                return json.loads(matches[0].strip())
            except json.JSONDecodeError:
                pass

        # Strategy 3: Extract from generic ``` ``` blocks
        generic_block_pattern = r"```\s*([\s\S]*?)\s*```"
        matches = re.findall(generic_block_pattern, text)
        if matches:
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue

        # Strategy 4: Find balanced JSON object/array
        start_obj = text.find("{")
        start_arr = text.find("[")

        if start_obj == -1 and start_arr == -1:
            return None

        if start_arr == -1 or (start_obj != -1 and start_obj < start_arr):
            json_str = self._extract_balanced_braces(text[start_obj:], "{", "}")
        else:
            json_str = self._extract_balanced_braces(text[start_arr:], "[", "]")

        if json_str:
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        return None

    def _extract_balanced_braces(self, text: str, open_char: str, close_char: str) -> Optional[str]:
        """Extract balanced braces/brackets from text"""
        if not text or text[0] != open_char:
            return None

        depth = 0
        in_string = False
        escape = False

        for i, char in enumerate(text):
            if escape:
                escape = False
                continue

            if char == "\\":
                escape = True
                continue

            if char == '"' and not in_string:
                in_string = True
            elif char == '"' and in_string:
                in_string = False

            if not in_string:
                if char == open_char:
                    depth += 1
                elif char == close_char:
                    depth -= 1
                    if depth == 0:
                        return text[:i+1]

        return None

    def close(self):
        """Close the HTTP session"""
        self.session.close()
