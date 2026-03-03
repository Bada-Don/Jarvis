import boto3
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure this matches the region in your .env (e.g., us-east-1)
region = os.getenv('AWS_REGION', 'us-east-1')
client = boto3.client('bedrock', region_name=region)

print(f"Looking up Claude models in {region}...\n")

response = client.list_foundation_models()
for model in response['modelSummaries']:
    model_id = model['modelId']
    # Filter to only show Anthropic Claude models
    if 'claude' in model_id.lower():
        print(model_id)
print("\nDone.")
