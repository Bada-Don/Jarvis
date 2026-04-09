
import os
import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_provider import GeminiProvider, OpenAIProvider
from newPlanner_service import PlannerService

class TestLLMProviders(unittest.TestCase):
    def setUp(self):
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'GEMINI_API_KEY': 'fake_gemini_key',
            'OPENAI_API_KEY': 'fake_openai_key'
        })
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    @patch('llm_provider.genai.Client')
    def test_gemini_provider(self, mock_client):
        # Setup mock
        mock_response = MagicMock()
        mock_response.text = '{"sequence": []}'
        mock_client.return_value.models.generate_content.return_value = mock_response

        # Test
        provider = GeminiProvider(api_key='test_key')
        response = provider.generate_content("system", "user")
        
        # Verify
        self.assertEqual(response, '{"sequence": []}')
        mock_client.return_value.models.generate_content.assert_called_once()

    @patch('llm_provider.OpenAI')
    @patch('llm_provider.OPENAI_AVAILABLE', True) # Force available
    def test_openai_provider(self, mock_openai):
        # Setup mock
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='{"sequence": []}'))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        # Test
        provider = OpenAIProvider(api_key='test_key')
        response = provider.generate_content("system", "user")

        # Verify
        self.assertEqual(response, '{"sequence": []}')
        mock_openai.return_value.chat.completions.create.assert_called_once()


    @patch('newPlanner_service.GeminiProvider')
    def test_planner_service_default(self, mock_gemini):
        # Configure mock
        mock_gemini.return_value.generate_content.return_value = '{"sequence": []}'
        
        # Test default init (should use Gemini)
        config = {
            'WINDOWS_USERNAME': 'testuser',
            'DESKTOP_PATH': 'desktop',
            'DOCUMENTS_PATH': 'docs',
            'DOWNLOADS_PATH': 'downloads',
            'STICKERS_PATH': 'stickers'
        }
        service = PlannerService(config=config)
        service.generate_plan("open notepad")
        
        # Verify provider was initialized
        self.assertTrue(isinstance(service.provider, MagicMock)) # Since we mocked GeminiProvider class
        
    @patch('newPlanner_service.OpenAIProvider')
    def test_planner_service_openai(self, mock_openai):
        # Test OpenAI init
        config = {
            'LLM_PROVIDER': 'openai', 
            'OPENAI_API_KEY': 'test',
            'WINDOWS_USERNAME': 'testuser',
            'DESKTOP_PATH': 'desktop',
            'DOCUMENTS_PATH': 'docs',
            'DOWNLOADS_PATH': 'downloads',
            'STICKERS_PATH': 'stickers'
        }
        service = PlannerService(config=config)
        
        # We need to manually set provider if the mock replaces the class but not the instance creation logic perfectly in init_provider
        # Actually init_provider instantiates the class. Since we patched the class in planner_service namespace, it return a mock.
        
        self.assertEqual(service.llm_provider, 'openai')
        
if __name__ == '__main__':
    unittest.main()
