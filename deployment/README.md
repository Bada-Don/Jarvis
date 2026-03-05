# JARVIS AWS Deployment Guide

This guide covers deploying the JARVIS backend to AWS using three different approaches:

1. **CloudFormation (Recommended)** - One-click deployment with EC2
2. **Docker + ECS Fargate** - Containerized deployment with auto-scaling
3. **Elastic Beanstalk** - Simplified PaaS deployment

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured (`aws configure`)
- Docker installed (for ECS deployment)
- Python 3.11+ (for Elastic Beanstalk)

## Option 1: CloudFormation Deployment (Recommended)

### Quick Start

1. **Prepare your AWS credentials**:
   ```bash
   aws configure
   ```

2. **Create an EC2 Key Pair** (for SSH access):
   ```bash
   aws ec2 create-key-pair --key-name jarvis-key --query 'KeyMaterial' --output text > jarvis-key.pem
   chmod 400 jarvis-key.pem
   ```

3. **Deploy the CloudFormation stack**:
   ```bash
   aws cloudformation create-stack \
     --stack-name jarvis-infrastructure \
     --template-body file://jarvis-stack.yaml \
     --parameters ParameterKey=KeyPairName,ParameterValue=jarvis-key \
     --capabilities CAPABILITY_NAMED_IAM \
     --region us-east-1
   ```

4. **Monitor deployment**:
   ```bash
   aws cloudformation describe-stacks \
     --stack-name jarvis-infrastructure \
     --query 'Stacks[0].StackStatus' \
     --region us-east-1
   ```

5. **Get the backend URL**:
   ```bash
   aws cloudformation describe-stacks \
     --stack-name jarvis-infrastructure \
     --query 'Stacks[0].Outputs[?OutputKey==`BackendURL`].OutputValue' \
     --output text \
     --region us-east-1
   ```

### Deploy Your Code to EC2

After CloudFormation completes, deploy your actual backend code:

```bash
# Get EC2 public IP
EC2_IP=$(aws cloudformation describe-stacks \
  --stack-name jarvis-infrastructure \
  --query 'Stacks[0].Outputs[?OutputKey==`EC2PublicIP`].OutputValue' \
  --output text)

# Copy backend files to EC2
scp -i jarvis-key.pem -r ../backend/* ec2-user@$EC2_IP:/tmp/jarvis/

# SSH into EC2 and setup
ssh -i jarvis-key.pem ec2-user@$EC2_IP << 'EOF'
  sudo su - jarvis
  cd /opt/jarvis
  
  # Copy files
  sudo cp -r /tmp/jarvis/* /opt/jarvis/
  sudo chown -R jarvis:jarvis /opt/jarvis
  
  # Install additional dependencies
  source venv/bin/activate
  pip install -r requirements.txt
  
  # Restart service
  sudo systemctl restart jarvis
  sudo systemctl status jarvis
EOF
```

### Verify Deployment

```bash
# Test health endpoint
curl http://$EC2_IP:5000/health

# Check logs
ssh -i jarvis-key.pem ec2-user@$EC2_IP "sudo journalctl -u jarvis -f"
```

## Option 2: Docker + ECS Fargate

### Step 1: Build and Push Docker Image

```bash
cd ../backend

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Create ECR repository
aws ecr create-repository --repository-name jarvis-backend --region us-east-1

# Build image
docker build -t jarvis-backend .

# Tag image
docker tag jarvis-backend:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/jarvis-backend:latest

# Push to ECR
docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/jarvis-backend:latest
```

### Step 2: Create ECS Task Definition

Create `ecs-task-definition.json`:

```json
{
  "family": "jarvis-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::<AWS_ACCOUNT_ID>:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::<AWS_ACCOUNT_ID>:role/JarvisEC2Role",
  "containerDefinitions": [
    {
      "name": "jarvis-backend",
      "image": "<AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/jarvis-backend:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "LLM_PROVIDER", "value": "aws_bedrock"},
        {"name": "AWS_REGION", "value": "us-east-1"},
        {"name": "AWS_DYNAMODB_TABLE_NAME", "value": "JarvisState"},
        {"name": "AWS_S3_BUCKET_NAME", "value": "jarvis-automation-assets"},
        {"name": "FIREBASE_ENABLED", "value": "false"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/jarvis-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Register the task:
```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
```

### Step 3: Create ECS Service with Load Balancer

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name jarvis-cluster --region us-east-1

# Create Application Load Balancer (ALB)
# Note: You'll need to create VPC, subnets, and security groups first
# Or use the CloudFormation stack which already has these

# Create ECS service
aws ecs create-service \
  --cluster jarvis-cluster \
  --service-name jarvis-backend-service \
  --task-definition jarvis-backend \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --region us-east-1
```

## Option 3: Elastic Beanstalk

### Step 1: Prepare Application

```bash
cd ../backend

# Create application.py (Elastic Beanstalk entry point)
cp server.py application.py

# Create .ebextensions for configuration
mkdir -p .ebextensions
```

Create `.ebextensions/01_packages.config`:

```yaml
packages:
  yum:
    gcc: []
    gcc-c++: []
    make: []

option_settings:
  aws:elasticbeanstalk:application:environment:
    LLM_PROVIDER: aws_bedrock
    AWS_REGION: us-east-1
    AWS_DYNAMODB_TABLE_NAME: JarvisState
    AWS_S3_BUCKET_NAME: jarvis-automation-assets
    FIREBASE_ENABLED: false
  aws:elasticbeanstalk:container:python:
    WSGIPath: application:app
```

### Step 2: Initialize and Deploy

```bash
# Initialize Elastic Beanstalk
eb init -p python-3.11 jarvis-backend --region us-east-1

# Create environment
eb create jarvis-production \
  --instance-type t3.micro \
  --envvars LLM_PROVIDER=aws_bedrock,AWS_REGION=us-east-1

# Deploy
eb deploy

# Get URL
eb status
```

### Step 3: Configure IAM Role

Attach the following policies to the Elastic Beanstalk instance role:
- Bedrock access
- DynamoDB access (JarvisState table)
- S3 access (jarvis-automation-assets bucket)

## WebSocket Configuration

### For ALB (ECS/Elastic Beanstalk)

Enable WebSocket support on your Application Load Balancer:

```bash
# Modify target group attributes
aws elbv2 modify-target-group-attributes \
  --target-group-arn <TARGET_GROUP_ARN> \
  --attributes Key=deregistration_delay.timeout_seconds,Value=120
```

### For CloudFormation/EC2

WebSockets work out of the box on port 5000. No additional configuration needed.

## Post-Deployment Configuration

### 1. Update Mobile App Configuration

Update `ChatInterface/.env`:

```env
BACKEND_URL=http://<EC2_IP_OR_ALB_DNS>:5000
AWS_REGION=us-east-1
AWS_DYNAMODB_TABLE_NAME=JarvisState
```

### 2. Test the Deployment

```bash
# Health check
curl http://<BACKEND_URL>/health

# Test WebSocket connection
wscat -c ws://<BACKEND_URL>
```

### 3. Enable HTTPS (Production)

For production, use AWS Certificate Manager (ACM) and configure HTTPS:

```bash
# Request certificate
aws acm request-certificate \
  --domain-name jarvis.yourdomain.com \
  --validation-method DNS \
  --region us-east-1

# Update ALB listener to use HTTPS
aws elbv2 create-listener \
  --load-balancer-arn <ALB_ARN> \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=<CERT_ARN> \
  --default-actions Type=forward,TargetGroupArn=<TARGET_GROUP_ARN>
```

## Monitoring and Logs

### CloudWatch Logs

```bash
# View logs
aws logs tail /aws/ec2/jarvis --follow --region us-east-1

# For ECS
aws logs tail /ecs/jarvis-backend --follow --region us-east-1
```

### CloudWatch Metrics

Monitor:
- CPU utilization
- Memory usage
- Network in/out
- Request count
- Error rate

## Troubleshooting

### Common Issues

1. **WebSocket connection fails**
   - Check security group allows port 5000
   - Verify ALB has WebSocket support enabled
   - Check backend logs for connection errors

2. **Bedrock access denied**
   - Verify IAM role has Bedrock permissions
   - Check model access is enabled in AWS Console
   - Confirm region supports the model

3. **DynamoDB errors**
   - Verify table exists and is active
   - Check IAM permissions
   - Confirm table name matches environment variable

4. **High latency**
   - Check EC2 instance type (upgrade if needed)
   - Monitor CloudWatch metrics
   - Consider using ECS with auto-scaling

## Cleanup

### Delete CloudFormation Stack

```bash
aws cloudformation delete-stack --stack-name jarvis-infrastructure --region us-east-1
```

### Delete ECS Resources

```bash
aws ecs delete-service --cluster jarvis-cluster --service jarvis-backend-service --force
aws ecs delete-cluster --cluster jarvis-cluster
aws ecr delete-repository --repository-name jarvis-backend --force
```

### Delete Elastic Beanstalk

```bash
eb terminate jarvis-production
```

## Cost Estimation

### CloudFormation (EC2)
- t3.micro: ~$7.50/month (Free Tier: 750 hours/month)
- DynamoDB: Pay per request (~$0.25/million reads)
- S3: ~$0.023/GB/month
- Data transfer: First 100GB free

### ECS Fargate
- 0.25 vCPU, 0.5GB: ~$10/month
- Plus DynamoDB and S3 costs

### Elastic Beanstalk
- Similar to EC2 costs
- No additional Beanstalk charges

## Next Steps

1. ✅ Deploy backend infrastructure
2. ✅ Configure DynamoDB and S3
3. ⏭️ Update mobile app to use AWS backend
4. ⏭️ Test end-to-end flow
5. ⏭️ Enable HTTPS for production
6. ⏭️ Set up monitoring and alerts

## Support

For issues or questions:
- Check CloudWatch logs
- Review AWS service quotas
- Verify IAM permissions
- Test with curl/wscat
