# S3 Screenshot Upload Guide

## What Changed

The vision service now automatically uploads screenshots to S3 when using vision-based automation.

## Setup

### 1. Ensure boto3 is installed

```bash
pip install boto3
```

### 2. Configure AWS credentials

The client will use AWS credentials from:
- Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
- AWS CLI configuration (~/.aws/credentials)
- IAM role (if running on EC2)

### 3. Set environment variables in `.env`

```env
AWS_REGION=us-east-1
AWS_S3_BUCKET_NAME=jarvis-assets-980850252974-us-east-1
```

## How It Works

When the vision service is used:

1. **Screenshot Capture**: `capture_screenshot()` takes a screenshot
   - Uploads to S3: `screenshots/{device_id}/{timestamp}_screenshot.png`

2. **SoM Detection**: `run_som_detection()` creates annotated image
   - Uploads to S3: `screenshots/{device_id}/{timestamp}_annotated.png`

## S3 Bucket Structure

```
jarvis-assets-980850252974-us-east-1/
└── screenshots/
    └── {device_id}/
        ├── 1709876543_screenshot.png
        ├── 1709876543_annotated.png
        ├── 1709876598_screenshot.png
        └── 1709876598_annotated.png
```

## Viewing Screenshots

### AWS Console
1. Go to https://s3.console.aws.amazon.com/
2. Open bucket: `jarvis-assets-980850252974-us-east-1`
3. Navigate to: `screenshots/{your_device_id}/`

### AWS CLI
```bash
# List all screenshots
aws s3 ls s3://jarvis-assets-980850252974-us-east-1/screenshots/ --recursive

# List for specific device
aws s3 ls s3://jarvis-assets-980850252974-us-east-1/screenshots/desktop_e054d2c4a0684c98/

# Download a screenshot
aws s3 cp s3://jarvis-assets-980850252974-us-east-1/screenshots/desktop_e054d2c4a0684c98/1709876543_screenshot.png ./
```

### Python Script
```python
import boto3

s3 = boto3.client('s3', region_name='us-east-1')
bucket = 'jarvis-assets-980850252974-us-east-1'
device_id = 'desktop_e054d2c4a0684c98'

# List screenshots for device
response = s3.list_objects_v2(
    Bucket=bucket,
    Prefix=f'screenshots/{device_id}/'
)

for obj in response.get('Contents', []):
    print(f"📸 {obj['Key']}")
    print(f"   Size: {obj['Size']/1024:.2f} KB")
    print(f"   Modified: {obj['LastModified']}")
```

## Troubleshooting

### Screenshots not uploading

1. **Check boto3 installation**:
   ```bash
   python -c "import boto3; print('boto3 installed')"
   ```

2. **Check AWS credentials**:
   ```bash
   aws s3 ls s3://jarvis-assets-980850252974-us-east-1/
   ```

3. **Check client logs**:
   Look for:
   - `✅ S3 client initialized`
   - `✅ Screenshot uploaded to S3: screenshots/...`
   
   Or errors:
   - `⚠️ boto3 not installed`
   - `⚠️ Failed to initialize S3 client`
   - `❌ Failed to upload to S3`

4. **Check device ID**:
   The device ID must be set for uploads to work. Check client logs for:
   - `✓ Using device ID from device_config.json: desktop_...`

### Permission errors

If you see `AccessDenied` errors, ensure your AWS credentials have S3 permissions:

```json
{
  "Effect": "Allow",
  "Action": [
    "s3:PutObject",
    "s3:GetObject",
    "s3:ListBucket"
  ],
  "Resource": [
    "arn:aws:s3:::jarvis-assets-980850252974-us-east-1",
    "arn:aws:s3:::jarvis-assets-980850252974-us-east-1/*"
  ]
}
```

## Lifecycle Policy

Screenshots are automatically deleted after 24 hours due to the S3 lifecycle policy.

To check the policy:
```bash
aws s3api get-bucket-lifecycle-configuration --bucket jarvis-assets-980850252974-us-east-1
```

## Testing

Test S3 upload manually:

```python
from vision_service import VisionService
import numpy as np

# Initialize vision service
vision = VisionService()
vision.set_device_id('desktop_test123')

# Create a test image
test_image = np.zeros((100, 100, 3), dtype=np.uint8)

# Upload to S3
object_key = vision.upload_to_s3(test_image, 'test.png')
print(f"Uploaded: {object_key}")
```

Then check S3:
```bash
aws s3 ls s3://jarvis-assets-980850252974-us-east-1/screenshots/desktop_test123/
```

## Next Steps

Now when you use vision-based automation:
1. Screenshots are automatically captured
2. Annotated images are created with SoM
3. Both are uploaded to S3
4. You can view them in AWS Console or download via CLI
5. They're automatically deleted after 24 hours

No manual intervention needed!
