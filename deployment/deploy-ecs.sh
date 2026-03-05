#!/bin/bash
# JARVIS ECS Fargate Deployment Script
# This script builds and deploys the backend to AWS ECS Fargate

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REGION="${AWS_REGION:-us-east-1}"
CLUSTER_NAME="${CLUSTER_NAME:-jarvis-cluster}"
SERVICE_NAME="${SERVICE_NAME:-jarvis-backend-service}"
TASK_FAMILY="${TASK_FAMILY:-jarvis-backend}"
ECR_REPO_NAME="${ECR_REPO_NAME:-jarvis-backend}"
CONTAINER_NAME="${CONTAINER_NAME:-jarvis-backend}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}JARVIS ECS Fargate Deployment${NC}"
echo -e "${BLUE}========================================${NC}"

# Check prerequisites
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✓ AWS Account: $AWS_ACCOUNT_ID${NC}"

ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO_NAME"

# Step 1: Create ECR repository if it doesn't exist
echo -e "${YELLOW}Checking ECR repository...${NC}"
if ! aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$REGION" &> /dev/null; then
    echo -e "${YELLOW}Creating ECR repository...${NC}"
    aws ecr create-repository \
        --repository-name "$ECR_REPO_NAME" \
        --region "$REGION" \
        --image-scanning-configuration scanOnPush=true
    echo -e "${GREEN}✓ ECR repository created${NC}"
else
    echo -e "${GREEN}✓ ECR repository exists${NC}"
fi

# Step 2: Login to ECR
echo -e "${YELLOW}Logging in to ECR...${NC}"
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
echo -e "${GREEN}✓ Logged in to ECR${NC}"

# Step 3: Build Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
cd ../backend
docker build -t "$ECR_REPO_NAME:latest" .
echo -e "${GREEN}✓ Docker image built${NC}"

# Step 4: Tag and push to ECR
echo -e "${YELLOW}Pushing image to ECR...${NC}"
docker tag "$ECR_REPO_NAME:latest" "$ECR_URI:latest"
docker push "$ECR_URI:latest"
echo -e "${GREEN}✓ Image pushed to ECR${NC}"

cd ../deployment

# Step 5: Create ECS cluster if it doesn't exist
echo -e "${YELLOW}Checking ECS cluster...${NC}"
if ! aws ecs describe-clusters --clusters "$CLUSTER_NAME" --region "$REGION" --query 'clusters[0].status' --output text 2>/dev/null | grep -q "ACTIVE"; then
    echo -e "${YELLOW}Creating ECS cluster...${NC}"
    aws ecs create-cluster --cluster-name "$CLUSTER_NAME" --region "$REGION"
    echo -e "${GREEN}✓ ECS cluster created${NC}"
else
    echo -e "${GREEN}✓ ECS cluster exists${NC}"
fi

# Step 6: Create CloudWatch log group
echo -e "${YELLOW}Creating CloudWatch log group...${NC}"
aws logs create-log-group --log-group-name "/ecs/$TASK_FAMILY" --region "$REGION" 2>/dev/null || true
echo -e "${GREEN}✓ Log group ready${NC}"

# Step 7: Create/Update task definition
echo -e "${YELLOW}Registering ECS task definition...${NC}"

# Get VPC and subnet info from CloudFormation stack (if exists)
STACK_NAME="jarvis-infrastructure"
VPC_ID=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`VpcId`].OutputValue' \
    --output text \
    --region "$REGION" 2>/dev/null || echo "")

if [ -z "$VPC_ID" ]; then
    echo -e "${YELLOW}Note: Using default VPC (CloudFormation stack not found)${NC}"
fi

# Create task definition JSON
cat > ecs-task-definition.json << EOF
{
  "family": "$TASK_FAMILY",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/JarvisEC2Role",
  "containerDefinitions": [
    {
      "name": "$CONTAINER_NAME",
      "image": "$ECR_URI:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "LLM_PROVIDER", "value": "aws_bedrock"},
        {"name": "AWS_REGION", "value": "$REGION"},
        {"name": "AWS_BEDROCK_PLANNER_MODEL", "value": "us.anthropic.claude-haiku-4-5-20251001-v1:0"},
        {"name": "AWS_BEDROCK_VISION_MODEL", "value": "us.anthropic.claude-sonnet-4-6"},
        {"name": "AWS_DYNAMODB_TABLE_NAME", "value": "JarvisState"},
        {"name": "AWS_S3_BUCKET_NAME", "value": "jarvis-automation-assets-$AWS_ACCOUNT_ID"},
        {"name": "FIREBASE_ENABLED", "value": "false"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/$TASK_FAMILY",
          "awslogs-region": "$REGION",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
EOF

aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json --region "$REGION"
echo -e "${GREEN}✓ Task definition registered${NC}"

# Step 8: Get default VPC and subnets (if not using CloudFormation)
if [ -z "$VPC_ID" ]; then
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text --region "$REGION")
fi

SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[*].SubnetId' --output text --region "$REGION" | tr '\t' ',')

# Get or create security group
SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=JarvisSecurityGroup" "Name=vpc-id,Values=$VPC_ID" \
    --query 'SecurityGroups[0].GroupId' \
    --output text \
    --region "$REGION" 2>/dev/null || echo "")

if [ -z "$SG_ID" ] || [ "$SG_ID" == "None" ]; then
    echo -e "${YELLOW}Creating security group...${NC}"
    SG_ID=$(aws ec2 create-security-group \
        --group-name JarvisSecurityGroup \
        --description "Security group for JARVIS ECS tasks" \
        --vpc-id "$VPC_ID" \
        --region "$REGION" \
        --query 'GroupId' \
        --output text)
    
    # Add ingress rules
    aws ec2 authorize-security-group-ingress \
        --group-id "$SG_ID" \
        --protocol tcp \
        --port 5000 \
        --cidr 0.0.0.0/0 \
        --region "$REGION"
    
    echo -e "${GREEN}✓ Security group created${NC}"
fi

# Step 9: Create or update ECS service
echo -e "${YELLOW}Checking ECS service...${NC}"
SERVICE_EXISTS=$(aws ecs describe-services \
    --cluster "$CLUSTER_NAME" \
    --services "$SERVICE_NAME" \
    --region "$REGION" \
    --query 'services[0].status' \
    --output text 2>/dev/null || echo "MISSING")

if [ "$SERVICE_EXISTS" == "ACTIVE" ]; then
    echo -e "${YELLOW}Updating ECS service...${NC}"
    aws ecs update-service \
        --cluster "$CLUSTER_NAME" \
        --service "$SERVICE_NAME" \
        --task-definition "$TASK_FAMILY" \
        --force-new-deployment \
        --region "$REGION"
    echo -e "${GREEN}✓ Service updated${NC}"
else
    echo -e "${YELLOW}Creating ECS service...${NC}"
    aws ecs create-service \
        --cluster "$CLUSTER_NAME" \
        --service-name "$SERVICE_NAME" \
        --task-definition "$TASK_FAMILY" \
        --desired-count 1 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" \
        --region "$REGION"
    echo -e "${GREEN}✓ Service created${NC}"
fi

# Wait for service to stabilize
echo -e "${YELLOW}Waiting for service to stabilize...${NC}"
aws ecs wait services-stable \
    --cluster "$CLUSTER_NAME" \
    --services "$SERVICE_NAME" \
    --region "$REGION"

echo -e "${GREEN}✓ Service is stable${NC}"

# Get task public IP
echo -e "${YELLOW}Getting task public IP...${NC}"
TASK_ARN=$(aws ecs list-tasks \
    --cluster "$CLUSTER_NAME" \
    --service-name "$SERVICE_NAME" \
    --region "$REGION" \
    --query 'taskArns[0]' \
    --output text)

if [ -n "$TASK_ARN" ] && [ "$TASK_ARN" != "None" ]; then
    ENI_ID=$(aws ecs describe-tasks \
        --cluster "$CLUSTER_NAME" \
        --tasks "$TASK_ARN" \
        --region "$REGION" \
        --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
        --output text)
    
    PUBLIC_IP=$(aws ec2 describe-network-interfaces \
        --network-interface-ids "$ENI_ID" \
        --region "$REGION" \
        --query 'NetworkInterfaces[0].Association.PublicIp' \
        --output text)
    
    echo -e "${GREEN}✓ Task Public IP: $PUBLIC_IP${NC}"
fi

# Display results
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}ECS Details:${NC}"
echo -e "  Cluster:      ${GREEN}$CLUSTER_NAME${NC}"
echo -e "  Service:      ${GREEN}$SERVICE_NAME${NC}"
echo -e "  Task Family:  ${GREEN}$TASK_FAMILY${NC}"
echo -e "  ECR Image:    ${GREEN}$ECR_URI:latest${NC}"
if [ -n "$PUBLIC_IP" ]; then
    echo -e "  Backend URL:  ${GREEN}http://$PUBLIC_IP:5000${NC}"
fi
echo ""
echo -e "${BLUE}View Logs:${NC}"
echo -e "  ${YELLOW}aws logs tail /ecs/$TASK_FAMILY --follow --region $REGION${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Test the deployment:"
if [ -n "$PUBLIC_IP" ]; then
    echo -e "   ${YELLOW}curl http://$PUBLIC_IP:5000/health${NC}"
fi
echo "2. Update mobile app BACKEND_URL"
echo "3. Monitor CloudWatch logs for any issues"
echo ""
