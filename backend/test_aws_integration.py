"""
Test AWS Bedrock Integration
Verifies that AWS Bedrock can be invoked successfully.
"""

import os
from dotenv import load_dotenv
from llm_provider import AWSBedrockProvider

# Load environment variables
load_dotenv()


def test_bedrock_haiku():
    """Test Claude 4.5 Haiku (Planner model)"""
    print("=" * 60)
    print("Testing AWS Bedrock - Claude 4.5 Haiku (Planner)")
    print("=" * 60)
    
    try:
        region = os.getenv('AWS_REGION', 'us-east-1')
        model_id = os.getenv('AWS_BEDROCK_PLANNER_MODEL', 'us.anthropic.claude-haiku-4-5-20251001-v1:0')
        
        print(f"Region: {region}")
        print(f"Model: {model_id}")
        print()
        
        provider = AWSBedrockProvider(region_name=region, model_id=model_id)
        
        system_prompt = "You are a helpful assistant that generates JSON responses."
        user_prompt = "Generate a simple JSON object with a greeting message."
        
        print("Sending request to Bedrock...")
        response = provider.generate_content(system_prompt, user_prompt)
        
        print("\n✅ SUCCESS!")
        print(f"Response: {response}")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        print()
        return False


def test_bedrock_sonnet():
    """Test Claude 4.6 Sonnet (Vision model)"""
    print("=" * 60)
    print("Testing AWS Bedrock - Claude 4.6 Sonnet (Vision)")
    print("=" * 60)
    
    try:
        region = os.getenv('AWS_REGION', 'us-east-1')
        model_id = os.getenv('AWS_BEDROCK_VISION_MODEL', 'us.anthropic.claude-sonnet-4-6')
        
        print(f"Region: {region}")
        print(f"Model: {model_id}")
        print()
        
        provider = AWSBedrockProvider(region_name=region, model_id=model_id)
        
        system_prompt = "You are a helpful assistant."
        user_prompt = "What is the capital of France?"
        
        print("Sending request to Bedrock...")
        response = provider.generate_content(system_prompt, user_prompt)
        
        print("\n✅ SUCCESS!")
        print(f"Response: {response}")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        print()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AWS BEDROCK INTEGRATION TESTS")
    print("=" * 60 + "\n")
    
    # Check for AWS credentials
    if not os.getenv('AWS_ACCESS_KEY_ID') and not os.path.exists(os.path.expanduser('~/.aws/credentials')):
        print("⚠️  WARNING: No AWS credentials found!")
        print("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env")
        print("   OR configure AWS CLI: aws configure")
        print()
    
    results = []
    
    # Test Haiku (Planner)
    results.append(("Haiku (Planner)", test_bedrock_haiku()))
    
    # Test Sonnet (Vision)
    results.append(("Sonnet (Vision)", test_bedrock_sonnet()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
    print()
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return all_passed


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
