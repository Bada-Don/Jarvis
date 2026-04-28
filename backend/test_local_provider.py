import os
import sys
import json
import time
from pathlib import Path

backend_path = Path(__file__).parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from llm_provider import LocalProvider, GeminiProvider, OpenAIProvider
from dotenv import load_dotenv

load_dotenv()


def test_local_provider_init():
    """Test LocalProvider initialization and config."""
    print("=== Test 1: LocalProvider Initialization ===")
    model_name = os.getenv('LOCAL_MODEL_NAME', 'google/gemma-4-e2b')
    base_url = os.getenv('LOCAL_BASE_URL', 'http://127.0.0.1:1234/v1')

    try:
        provider = LocalProvider(model_name=model_name, base_url=base_url)
        assert provider.model_name == model_name
        assert callable(provider.generate_content)
        print(f"  PASS: model={model_name}, base_url={base_url}")
        return provider
    except Exception as e:
        print(f"  FAIL: {repr(e)}")
        return None


def test_local_provider_generation(provider):
    """Test content generation (requires LM Studio running)."""
    print("\n=== Test 2: Content Generation ===")
    if provider is None:
        print("  SKIP: Provider not initialized")
        return

    try:
        start = time.perf_counter()
        response = provider.generate_content(
            system_prompt="You are a helpful assistant. Respond with only a JSON object.",
            user_prompt='Return JSON: {"status": "ok", "message": "hello"}'
        )
        elapsed = time.perf_counter() - start
        print(f"  PASS: {len(response)} chars in {elapsed:.2f}s")
        print(f"  Response: {response[:200]}")
    except Exception as e:
        print(f"  FAIL (is LM Studio running?): {e}")


def test_json_extraction(provider):
    """Test that markdown-wrapped JSON is extracted properly."""
    print("\n=== Test 3: JSON Extraction ===")
    if provider is None:
        print("  SKIP: Provider not initialized")
        return

    cases = [
        # Basic cases
        ('```json\n{"a": 1}\n```', '{"a": 1}'),
        ('```\n{"b": 2}\n```', '{"b": 2}'),
        ('{"c": 3}', '{"c": 3}'),
        ('  \n{"d": 4}\n  ', '{"d": 4}'),
        # Case 1: Extra text before JSON
        ('Sure! Here is your result:\n{"status": "ok"}', '{"status": "ok"}'),
        ('The answer is: {"x": 1} and done', '{"x": 1}'),
        # Case 3: Partial/truncated response
        ('{"status":', '{"status":""}'),  # repaired
        ('{"a": 1, "b":', '{"a": 1}'),    # truncated at comma, repaired
    ]
    for input_text, expected in cases:
        result = provider._extract_json(input_text)
        status = "PASS" if result == expected else f"FAIL (got {result!r})"
        print(f"  {status}: {input_text!r} -> {result!r}")

def test_broken_json_handling(provider):
    """Test that broken/malformed JSON is handled gracefully."""
    print("\n=== Test 6: Broken JSON Handling ===")
    if provider is None:
        print("  SKIP: Provider not initialized")
        return

    # Simulate what planner_service does with the response
    broken_cases = [
        '{"status": "ok", "msg": hello}',      # unquoted value
        '{"status": "ok"',                      # missing closing brace
        'Here it is: {"a":1}',                  # extra text prefix
    ]
    for raw in broken_cases:
        extracted = provider._extract_json(raw)
        try:
            parsed = json.loads(extracted)
            print(f"  PASS: Repaired -> {parsed}")
        except json.JSONDecodeError:
            print(f"  WARN: Could not repair -> {extracted!r}")

def test_json_parse_real_response(provider):
    """Verify real model response parses as JSON."""
    print("\n=== Test 4: JSON Parse Check ===")
    if provider is None:
        print("  SKIP: Provider not initialized")
        return

    try:
        response = provider.generate_content(
            system_prompt="Return a JSON object with keys: status, message.",
            user_prompt="What is the status?"
        )
        try:
            parsed = json.loads(response)
            print(f"  PASS: Valid JSON — {list(parsed.keys())}")
        except json.JSONDecodeError as e:
            print(f"  FAIL: Not valid JSON — {e}")
            print(f"  Raw: {response[:300]}")
    except Exception as e:
        print(f"  FAIL: {e}")


def test_provider_switching():
    """Test switching between providers."""
    print("\n=== Test 5: Provider Switching ===")
    for provider_name in ['local', 'gemini', 'openai']:
        try:
            if provider_name == 'local':
                p = LocalProvider()
                print(f"  PASS: LocalProvider created")
            elif provider_name == 'gemini':
                api_key = os.getenv('GEMINI_API_KEY', '')
                if api_key:
                    p = GeminiProvider(api_key=api_key)
                    print(f"  PASS: GeminiProvider created")
                else:
                    print(f"  SKIP: No GEMINI_API_KEY")
            elif provider_name == 'openai':
                api_key = os.getenv('OPENAI_API_KEY', '')
                if api_key:
                    p = OpenAIProvider(api_key=api_key)
                    print(f"  PASS: OpenAIProvider created")
                else:
                    print(f"  SKIP: No OPENAI_API_KEY")
        except Exception as e:
            print(f"  FAIL [{provider_name}]: {e}")


if __name__ == "__main__":
    provider = test_local_provider_init()
    test_local_provider_generation(provider)
    test_json_extraction(provider)
    test_broken_json_handling(provider)
    test_json_parse_real_response(provider)
    test_provider_switching()
    print("\nDone. Ensure LM Studio server is running at http://127.0.0.1:1234/v1")