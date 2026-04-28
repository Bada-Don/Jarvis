import os
import json
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Optional

# Try importing dependencies
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate_content(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate content from the LLM.
        
        Args:
            system_prompt: The system instruction/context.
            user_prompt: The user's input command.
            
        Returns:
            str: The generated text response.
        """
        pass


class GeminiProvider(LLMProvider):
    """Gemini implementation of LLMProvider."""
    
    def __init__(self, api_key: str, model_name: str = 'gemini-2.5-flash'):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-genai package is not installed. Run 'pip install google-genai'")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_content(self, system_prompt: str, user_prompt: str) -> str:
        import time
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config={
                        'system_instruction': system_prompt,
                        'temperature': 0.1  # Low temperature for reliable JSON
                    }
                )
                return response.text
            except Exception as e:
                # Handle 503 UNAVAILABLE or other temporary issues
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"⚠️ Gemini API unavailable (503). Retrying in {delay}s... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        continue
                raise e
        return "" # Should not reach here due to raise e


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLMProvider."""
    
    def __init__(self, api_key: str, model_name: str = 'gpt-4o', base_url: Optional[str] = None):
        if not OPENAI_AVAILABLE:
             raise ImportError("openai package is not installed. Run 'pip install openai'")
        
        # supports OpenRouter by passing base_url="https://openrouter.ai/api/v1"
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name

    def generate_content(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=0.1,  # Low temperature for reliable JSON
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content


class LocalProvider(LLMProvider):
    """LM Studio / OpenAI-compatible local LLM provider"""

    # Appended to system prompt to enforce JSON-only output
    JSON_SUFFIX = (
        "\n\nCRITICAL: Output ONLY valid JSON. "
        "No markdown, no explanations, no extra text."
    )

    def __init__(
        self,
        model_name: str = "google/gemma-4-e2b",
        base_url: str = "http://127.0.0.1:1234/v1",
        timeout: float = 120.0,
        max_retries: int = 3,
    ):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package is not installed. Run 'pip install openai'")

        self.client = OpenAI(
            api_key="lm-studio",
            base_url=base_url,
            timeout=timeout,
        )
        self.model_name = model_name
        self.max_retries = max_retries
        self.base_url = base_url.rstrip("/")

    def _extract_json(self, text: str) -> str:
        """Extract JSON from model output, handling markdown fences, extra text, and partial responses."""
        stripped = text.strip()

        # Case 1: Strip markdown code fences
        if stripped.startswith("```"):
            lines = stripped.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            stripped = "\n".join(lines).strip()

        # Case 2: Extra text before/after JSON — find outermost { ... }
        first_brace = stripped.find("{")
        if first_brace == -1:
            first_brace = stripped.find("[")
        if first_brace > 0:
            # Find matching closing brace
            last_brace = stripped.rfind("}")
            if last_brace == -1:
                last_brace = stripped.rfind("]")
            if last_brace > first_brace:
                stripped = stripped[first_brace:last_brace + 1]

        # Case 3: Partial/truncated response — try to close unclosed braces
        stripped = self._repair_json(stripped)

        return stripped

    def _repair_json(self, text: str) -> str:
        """Attempt to repair truncated or malformed JSON by balancing braces."""
        open_curly = text.count("{") - text.count("}")
        open_square = text.count("[") - text.count("]")

        # Close unclosed brackets
        if open_square > 0:
            text += "]" * open_square
        if open_curly > 0:
            text += "}" * open_curly

        # Try to parse — if it fails, try more aggressive fixes
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            pass

        # Aggressive: truncate at last valid comma or colon to remove broken tail
        # e.g. {"status":  -> {"status": ""}
        for i in range(len(text) - 1, 0, -1):
            if text[i] in (",", ":"):
                # Remove the broken fragment after this delimiter
                candidate = text[:i]
                # Re-balance braces
                open_curly = candidate.count("{") - candidate.count("}")
                open_square = candidate.count("[") - candidate.count("]")
                if open_square > 0:
                    candidate += "]" * open_square
                if open_curly > 0:
                    candidate += "}" * open_curly
                try:
                    json.loads(candidate)
                    return candidate
                except json.JSONDecodeError:
                    continue

        # Last resort: return as-is (caller will handle json.JSONDecodeError)
        return text

    def _check_server_available(self) -> bool:
        """Quick health check: hit /models endpoint to verify server is reachable."""
        try:
            url = f"{self.base_url}/models"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False

    def generate_content(self, system_prompt: str, user_prompt: str) -> str:
        import time

        strict_system_prompt = system_prompt + self.JSON_SUFFIX

        # Pre-flight: check if server is reachable before wasting time on retries
        if not self._check_server_available():
            print(f"LocalProvider: Server at {self.base_url} not reachable. Waiting for startup...")
            for wait_attempt in range(self.max_retries):
                time.sleep(3 * (wait_attempt + 1))  # 3s, 6s, 9s
                if self._check_server_available():
                    print(f"LocalProvider: Server available after {(wait_attempt + 1) * 3}s wait")
                    break
            else:
                raise RuntimeError(
                    f"LocalProvider: Cannot reach server at {self.base_url}. "
                    f"Ensure LM Studio (or your local LLM server) is running and the model is loaded."
                )

        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    temperature=0.0,
                    max_tokens=4096,
                    messages=[
                        {"role": "system", "content": strict_system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )

                message = response.choices[0].message
                content = message.content

                # Thinking/reasoning models may put output in reasoning_content
                # with content left empty
                if not content:
                    reasoning = getattr(message, 'reasoning_content', None)
                    if reasoning:
                        content = reasoning

                if not content:
                    raise ValueError("Empty response from model (both content and reasoning_content are empty)")

                return self._extract_json(content)

            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                is_connection_error = any(kw in error_str for kw in ['connection', 'connect', 'refused', 'timeout'])

                if attempt < self.max_retries - 1:
                    # Longer delays for connection errors (server may be starting)
                    delay = (2 ** attempt) * (3 if is_connection_error else 1)
                    print(f"LocalProvider retry {attempt + 1}/{self.max_retries} after {delay}s: {e}")
                    time.sleep(delay)

        raise RuntimeError(
            f"LocalProvider failed after {self.max_retries} retries: {last_error}. "
            f"Check if LM Studio is running at {self.base_url} with model '{self.model_name}' loaded."
        )