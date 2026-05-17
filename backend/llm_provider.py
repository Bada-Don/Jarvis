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
    
    def __init__(self):
        self.last_usage: Optional[Dict[str, Any]] = None

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
        super().__init__()
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
                
                # Capture token usage metadata
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    self.last_usage = {
                        'prompt_tokens': response.usage_metadata.prompt_token_count,
                        'candidates_tokens': response.usage_metadata.candidates_token_count,
                        'total_tokens': response.usage_metadata.total_token_count,
                    }
                    if hasattr(response.usage_metadata, 'thoughts_token_count'):
                        self.last_usage['thoughts_tokens'] = response.usage_metadata.thoughts_token_count
                
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
        super().__init__()
        if not OPENAI_AVAILABLE:
             raise ImportError("openai package is not installed. Run 'pip install openai'")
        
        # supports OpenRouter by passing base_url="https://openrouter.ai/api/v1"
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name

    def generate_content(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=0.1,  # Low temperature for reliable JSON
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Capture token usage metadata
        if hasattr(response, 'usage') and response.usage:
            self.last_usage = {
                'prompt_tokens': response.usage.prompt_tokens,
                'candidates_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens,
            }

        return response.choices[0].message.content


class LocalProvider(LLMProvider):
    """LM Studio / OpenAI-compatible local LLM provider"""

    # Appended to system prompt to enforce JSON-only output
    JSON_SUFFIX = (
        "\n\nACT AS A PURE JSON API. "
        "DO NOT provide explanations. DO NOT provide conversational text. "
        "Output ONLY the raw JSON object. "
        "If you include any text outside the JSON, the system will fail. "
        "No markdown fences, no thinking, no extra output."
    )

    def __init__(
        self,
        model_name: str = "google/gemma-4-e2b",
        base_url: str = "http://127.0.0.1:1234/v1",
        timeout: float = 120.0,
        max_retries: int = 3,
    ):
        super().__init__()
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
        self.cache_stats = {"total_requests": 0, "cached_tokens": 0, "total_input_tokens": 0}

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

    def _track_cache_stats(self, response) -> None:
        """Extract and log KV cache hit metrics from the API response."""
        try:
            usage = getattr(response, 'usage', None)
            if usage is None:
                return

            input_tokens = getattr(usage, 'prompt_tokens', 0) or 0
            self.cache_stats["total_requests"] += 1
            self.cache_stats["total_input_tokens"] += input_tokens

            # LM Studio returns cached_tokens in input_tokens_details
            input_details = getattr(usage, 'prompt_tokens_details', None)
            if input_details:
                # prompt_tokens_details is a list of CompletionTokensDetails
                for detail in (input_details if isinstance(input_details, list) else [input_details]):
                    cached = getattr(detail, 'cached_tokens', 0) or 0
                    if cached > 0:
                        self.cache_stats["cached_tokens"] += cached
                        hit_pct = (cached / input_tokens * 100) if input_tokens > 0 else 0
                        print(f"  KV Cache: {cached}/{input_tokens} tokens cached ({hit_pct:.0f}%)")
                        return

            # Also check for OpenAI-style nested dict
            if hasattr(usage, 'model_dump'):
                usage_dict = usage.model_dump()
                cached = usage_dict.get("prompt_tokens_details", {}).get("cached_tokens", 0)
                if cached > 0:
                    self.cache_stats["cached_tokens"] += cached
                    hit_pct = (cached / input_tokens * 100) if input_tokens > 0 else 0
                    print(f"  KV Cache: {cached}/{input_tokens} tokens cached ({hit_pct:.0f}%)")
        except Exception:
            pass  # Cache stats are best-effort, never fail the request

    def warmup_cache(self, system_prompt: str) -> bool:
        """Pre-warm the KV cache by sending a lightweight request with the system prompt.
        
        This populates the KV cache for the system prompt prefix so that
        subsequent real requests benefit from cache hits immediately.
        Returns True if warmup succeeded, False otherwise.
        """
        import time

        if not self._check_server_available():
            print("LocalProvider: Warmup skipped — server not reachable")
            return False

        try:
            start = time.perf_counter()
            warmup_prompt = system_prompt + self.JSON_SUFFIX
            response = self.client.chat.completions.create(
                model=self.model_name,
                temperature=0.0,
                max_tokens=64,  # Reasoning models need room to produce content.
                messages=[
                    {"role": "system", "content": warmup_prompt},
                    {"role": "user", "content": "Reply with: {\"status\":\"ready\"}"},
                ],
            )
            elapsed = time.perf_counter() - start
            self._track_cache_stats(response)
            print(f"LocalProvider: KV cache warmed up in {elapsed:.1f}s (subsequent requests will be faster)")
            return True
        except Exception as e:
            print(f"LocalProvider: Warmup failed (non-critical): {e}")
            return False

    def get_cache_stats(self) -> dict:
        """Return current cache hit statistics."""
        stats = dict(self.cache_stats)
        if stats["total_input_tokens"] > 0:
            stats["cache_hit_pct"] = round(
                stats["cached_tokens"] / stats["total_input_tokens"] * 100, 1
            )
        else:
            stats["cache_hit_pct"] = 0.0
        return stats

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
                start_time = time.perf_counter()
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    temperature=0.0,
                    max_tokens=4096,
                    messages=[
                        {"role": "system", "content": strict_system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                elapsed = time.perf_counter() - start_time

                # Track cache hit metrics
                self._track_cache_stats(response)

                # Capture token usage metadata
                if hasattr(response, 'usage') and response.usage:
                    self.last_usage = {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'candidates_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens,
                    }

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

                print(f"LocalProvider: Response in {elapsed:.1f}s")
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
