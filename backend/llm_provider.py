import os
import json
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

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


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
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config={
                'system_instruction': system_prompt,
                'temperature': 0.1  # Low temperature for reliable JSON
            }
        )
        return response.text


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLMProvider."""
    
    def __init__(self, api_key: str, model_name: str = 'gpt-4o'):
        if not OPENAI_AVAILABLE:
             raise ImportError("openai package is not installed. Run 'pip install openai'")
        self.client = OpenAI(api_key=api_key)
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


class AWSBedrockProvider(LLMProvider):
    """Amazon Bedrock implementation of LLMProvider for Anthropic Claude models."""
    
    def __init__(self, region_name: str = "us-east-1", model_id: str = "us.anthropic.claude-haiku-4-5-20251001-v1:0"):
        if not BOTO3_AVAILABLE:
             raise ImportError("boto3 package is not installed. Run 'pip install boto3'")
        
        # boto3 automatically picks up AWS credentials from:
        # 1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        # 2. AWS CLI config (~/.aws/credentials)
        # 3. IAM Role (if running on EC2/Lambda)
        try:
            self.client = boto3.client('bedrock-runtime', region_name=region_name)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize AWS Bedrock client: {e}")
            
        self.model_id = model_id
        print(f"✅ AWS Bedrock Provider initialized")
        print(f"   Region: {region_name}")
        print(f"   Model: {model_id}")

    def generate_content(self, system_prompt: str, user_prompt: str) -> str:
        # Bedrock requires a specific payload format for Claude 3/3.5/4.5
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "system": system_prompt,
            "temperature": 0.1,  # Low temperature for reliable JSON
            "messages":[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        }
        
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload)
            )
            
            # Read the streaming body response
            response_body = json.loads(response.get('body').read())
            
            # Extract the text content
            return response_body.get('content')[0].get('text')
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            
            if error_code == 'AccessDeniedException':
                raise PermissionError(f"AWS Bedrock Access Denied: Please request model access for '{self.model_id}' in the AWS Console. ({error_msg})")
            elif error_code == 'ValidationException':
                raise ValueError(f"AWS Bedrock Validation Error: Check your payload or model ID. ({error_msg})")
            else:
                raise RuntimeError(f"AWS Bedrock API Error: {error_code} - {error_msg}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error calling AWS Bedrock: {e}")