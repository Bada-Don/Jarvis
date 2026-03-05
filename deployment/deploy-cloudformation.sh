#!/bin/bash
# JARVIS CloudFormation Deployment Script
# This script deploys the complete AWS infrastructure using CloudFormation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="${STACK_NAME:-jarvis-infrastructure}"
KEY_NAME="${KEY_NAME:-jarvis-key}"
REGION="${AWS_REGION:-us-east-1}"
INSTANCE_TYPE="${INSTANCE_TYPE:-t3.micro}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}JARVIS CloudFormation Deployment${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Install it from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
echo -e "${YELLOW}Checking AWS credentials...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✓ AWS Account: $AWS_ACCOUNT_ID${NC}"

# Check if key pair exists
echo -e "${YELLOW}Checking EC2 key pair...${NC}"
if ! aws ec2 describe-key-pairs --key-names "$KEY_NAME" --region "$REGION" &> /dev/null; then
    echo -e "${YELLOW}Key pair '$KEY_NAME' not found. Creating...${NC}"
    aws ec2 create-key-pair \
        --key-name "$KEY_NAME" \
        --query 'KeyMaterial' \
        --output text \
        --region "$REGION" > "${KEY_NAME}.pem"
    chmod 400 "${KEY_NAME}.pem"
    echo -e "${GREEN}✓ Key pair created and saved to ${KEY_NAME}.pem${NC}"
else
    echo -e "${GREEN}✓ Key pair exists${NC}"
fi

# Check if stack already exists
echo -e "${YELLOW}Checking if stack exists...${NC}"
STACK_EXISTS=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].StackStatus' \
    --output text 2>/dev/null || echo "DOES_NOT_EXIST")

if [ "$STACK_EXISTS" != "DOES_NOT_EXIST" ]; then
    echo -e "${YELLOW}Stack '$STACK_NAME' already exists with status: $STACK_EXISTS${NC}"
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ACTION="update"
    else
        echo -e "${YELLOW}Deployment cancelled${NC}"
        exit 0
    fi
else
    ACTION="create"
fi

# Deploy CloudFormation stack
echo -e "${YELLOW}Deploying CloudFormation stack...${NC}"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo "Instance Type: $INSTANCE_TYPE"
echo "Key Pair: $KEY_NAME"
echo ""

if [ "$ACTION" == "create" ]; then
    aws cloudformation create-stack \
        --stack-name "$STACK_NAME" \
        --template-body file://jarvis-stack.yaml \
        --parameters \
            ParameterKey=KeyPairName,ParameterValue="$KEY_NAME" \
            ParameterKey=InstanceType,ParameterValue="$INSTANCE_TYPE" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$REGION"
    
    echo -e "${GREEN}✓ Stack creation initiated${NC}"
else
    aws cloudformation update-stack \
        --stack-name "$STACK_NAME" \
        --template-body file://jarvis-stack.yaml \
        --parameters \
            ParameterKey=KeyPairName,ParameterValue="$KEY_NAME" \
            ParameterKey=InstanceType,ParameterValue="$INSTANCE_TYPE" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$REGION"
    
    echo -e "${GREEN}✓ Stack update initiated${NC}"
fi

# Wait for stack to complete
echo -e "${YELLOW}Waiting for stack to complete (this may take 5-10 minutes)...${NC}"
echo "You can monitor progress in the AWS Console:"
echo "https://console.aws.amazon.com/cloudformation/home?region=$REGION#/stacks"
echo ""

if [ "$ACTION" == "create" ]; then
    aws cloudformation wait stack-create-complete \
        --stack-name "$STACK_NAME" \
        --region "$REGION"
else
    aws cloudformation wait stack-update-complete \
        --stack-name "$STACK_NAME" \
        --region "$REGION"
fi

echo -e "${GREEN}✓ Stack deployment complete!${NC}"

# Get stack outputs
echo -e "${YELLOW}Retrieving stack outputs...${NC}"
OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs')

EC2_IP=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="EC2PublicIP") | .OutputValue')
BACKEND_URL=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="BackendURL") | .OutputValue')
DYNAMODB_TABLE=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="DynamoDBTableName") | .OutputValue')
S3_BUCKET=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="S3BucketName") | .OutputValue')

# Display results
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Infrastructure Details:${NC}"
echo -e "  EC2 Public IP:    ${GREEN}$EC2_IP${NC}"
echo -e "  Backend URL:      ${GREEN}$BACKEND_URL${NC}"
echo -e "  DynamoDB Table:   ${GREEN}$DYNAMODB_TABLE${NC}"
echo -e "  S3 Bucket:        ${GREEN}$S3_BUCKET${NC}"
echo ""
echo -e "${BLUE}SSH Access:${NC}"
echo -e "  ${YELLOW}ssh -i ${KEY_NAME}.pem ec2-user@$EC2_IP${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Deploy backend code:"
echo -e "   ${YELLOW}./deploy-to-ec2.sh${NC}"
echo ""
echo "2. Update mobile app configuration:"
echo -e "   ${YELLOW}BACKEND_URL=$BACKEND_URL${NC}"
echo ""
echo "3. Test the deployment:"
echo -e "   ${YELLOW}curl $BACKEND_URL/health${NC}"
echo ""
echo "4. View logs:"
echo -e "   ${YELLOW}ssh -i ${KEY_NAME}.pem ec2-user@$EC2_IP 'sudo journalctl -u jarvis -f'${NC}"
echo ""
echo -e "${GREEN}========================================${NC}"
