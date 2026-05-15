import os
from dotenv import load_dotenv
from typing import Dict, Optional

class CredentialManager:
    """
    Manages API keys and other credentials for Jarvis.
    Loads from environment variables, with .env file support.
    """
    def __init__(self):
        load_dotenv() # Load .env file at initialization
        self._credentials: Dict[str, str] = {}
        self._load_credentials()

    def _load_credentials(self):
        """
        Loads relevant credentials from environment variables.
        Extend this method to include any new credentials needed.
        """
        self._credentials["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
        self._credentials["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        # Add other API keys or secrets here as needed
        # self._credentials["SOME_SERVICE_API_KEY"] = os.getenv("SOME_SERVICE_API_KEY")

    def get_credential(self, key: str) -> Optional[str]:
        """
        Retrieves a specific credential by key.
        """
        return self._credentials.get(key)

    def get_all_credentials(self) -> Dict[str, str]:
        """
        Returns all loaded credentials.
        """
        return self._credentials

# Example Usage (for testing/demonstration)
if __name__ == "__main__":
    # Create a dummy test file for demonstration
    test_env = ".env.test"
    with open(test_env, "w") as f:
        f.write("GEMINI_API_KEY=test_gemini_key_123\n")
        f.write("OPENAI_API_KEY=test_openai_key_456\n")

    # In a real scenario, load_dotenv() loads from .env by default.
    # For this test, we can manually set env vars.
    os.environ["GEMINI_API_KEY"] = "test_gemini_key_123"
    os.environ["OPENAI_API_KEY"] = "test_openai_key_456"

    cm = CredentialManager()
    print(f"Gemini API Key: {cm.get_credential('GEMINI_API_KEY')}")
    print(f"OpenAI API Key: {cm.get_credential('OPENAI_API_KEY')}")
    print(f"All Credentials: {cm.get_all_credentials()}")

    # Clean up test file
    if os.path.exists(test_env):
        os.remove(test_env)
