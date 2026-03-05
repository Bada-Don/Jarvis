#!/bin/bash
# JARVIS Elastic Beanstalk Deployment Script
# This script deploys the backend to AWS Elastic Beanstalk

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REGION="${AWS_REGION:-us-east-1}"
APP_NAME="${APP_NAME:-jarvis-backend}"
ENV_NAME="${ENV_NAME:-jarvis-production}"
INSTANCE_TYPE="${INSTANCE_TYPE:-t3.micro}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}JARVIS Elastic Beanstalk Deployment${NC}"
echo -e "${BLUE}========================================${NC}"

# Check prerequisites
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    exit 1
fi

if ! command -v eb &> /dev/null; then
    echo -e "${YELLOW}EB CLI not found. Installing...${NC}"
    pip install awsebcli
fi

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✓ AWS Account: $AWS_ACCOUNT_ID${NC}"

# Prepare application directory
echo -e "${YELLOW}Preparing application...${NC}"
cd ../backend

# Create application.py (Elastic Beanstalk entry point)
if [ ! -f "application.py" ]; then
    cp server.py application.py
    echo -e "${GREEN}✓ Created application.py${NC}"
fi

# Create .ebextensions directory
mkdir -p .ebextensions

# Create configuration files
cat > .ebextensions/01_packages.config << 'EOF'
packages:
  yum:
    gcc: []
    gcc-c++: []
    make: []

option_settings:
  aws:elasticbeanstalk:application:environment:
    LLM_PROVIDER: aws_bedrock
    AWS_REGION: us-east-1
    AWS_BEDROCK_PLANNER_MODEL: us.anthropic.claude-haiku-4-5-20251001-v1:0
    AWS_BEDROCK_VISION_MODEL: us.anthropic.claude-sonnet-4-6
    AWS_DYNAMODB_TABLE_NAME: JarvisState
    AWS_S3_BUCKET_NAME: jarvis-automation-assets
    FIREBASE_ENABLED: false
  aws:elasticbeanstalk:container:python:
    WSGIPath: application:app
  aws:elasticbeanstalk:environment:proxy:
    ProxyServer: nginx
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: static
EOF

cat > .ebextensions/02_python.config << 'EOF'
option_settings:
  aws:elasticbeanstalk:container:python:
    NumProcesses: 1
    NumThreads: 15
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: /var/app/current
EOF

cat > .ebextensions/03_websockets.config << 'EOF'
files:
  "/etc/nginx/conf.d/websockets.conf":
    mode: "000644"
    owner: root
    group: root
    content: |
      upstream backend {
        server 127.0.0.1:8000;
      }
      
      server {
        listen 80;
        
        location / {
          proxy_pass http://backend;
          proxy_http_version 1.1;
          proxy_set_header Upgrade $http_upgrade;
          proxy_set_header Connection "upgrade";
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
          proxy_read_timeout 86400;
        }
      }

commands:
  01_reload_nginx:
    command: "service nginx reload"
EOF

echo -e "${GREEN}✓ Configuration files created${NC}"

# Initialize Elastic Beanstalk (if not already initialized)
if [ ! -d ".elasticbeanstalk" ]; then
    echo -e "${YELLOW}Initializing Elastic Beanstalk...${NC}"
    eb init -p python-3.11 "$APP_NAME" --region "$REGION"
    echo -e "${GREEN}✓ Elastic Beanstalk initialized${NC}"
fi

# Check if environment exists
echo -e "${YELLOW}Checking environment...${NC}"
ENV_EXISTS=$(eb list | grep "$ENV_NAME" || echo "")

if [ -z "$ENV_EXISTS" ]; then
    # Create environment
    echo -e "${YELLOW}Creating Elastic Beanstalk environment...${NC}"
    echo "This may take 5-10 minutes..."
    
    eb create "$ENV_NAME" \
        --instance-type "$INSTANCE_TYPE" \
        --region "$REGION" \
        --envvars \
            LLM_PROVIDER=aws_bedrock,\
AWS_REGION="$REGION",\
AWS_DYNAMODB_TABLE_NAME=JarvisState,\
AWS_S3_BUCKET_NAME=jarvis-automation-assets-"$AWS_ACCOUNT_ID",\
FIREBASE_ENABLED=false
    
    echo -e "${GREEN}✓ Environment created${NC}"
else
    # Deploy to existing environment
    echo -e "${YELLOW}Deploying to existing environment...${NC}"
    eb deploy "$ENV_NAME"
    echo -e "${GREEN}✓ Deployment complete${NC}"
fi

# Get environment URL
echo -e "${YELLOW}Getting environment URL...${NC}"
ENV_URL=$(eb status "$ENV_NAME" | grep "CNAME" | awk '{print $2}')

if [ -n "$ENV_URL" ]; then
    BACKEND_URL="http://$ENV_URL"
    echo -e "${GREEN}✓ Backend URL: $BACKEND_URL${NC}"
fi

# Configure IAM role for Bedrock, DynamoDB, and S3 access
echo -e "${YELLOW}Configuring IAM role...${NC}"
INSTANCE_PROFILE=$(aws elasticbeanstalk describe-configuration-settings \
    --application-name "$APP_NAME" \
    --environment-name "$ENV_NAME" \
    --query 'ConfigurationSettings[0].OptionSettings[?OptionName==`IamInstanceProfile`].Value' \
    --output text \
    --region "$REGION")

if [ -n "$INSTANCE_PROFILE" ]; then
    ROLE_NAME=$(echo "$INSTANCE_PROFILE" | sed 's/.*\///')
    
    # Attach policies
    aws iam attach-role-policy \
        --role-name "$ROLE_NAME" \
        --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess \
        --region "$REGION" 2>/dev/null || true
    
    # Create inline policy for DynamoDB and S3
    cat > /tmp/jarvis-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:$REGION:$AWS_ACCOUNT_ID:table/JarvisState"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::jarvis-automation-assets-$AWS_ACCOUNT_ID",
        "arn:aws:s3:::jarvis-automation-assets-$AWS_ACCOUNT_ID/*"
      ]
    }
  ]
}
EOF
    
    aws iam put-role-policy \
        --role-name "$ROLE_NAME" \
        --policy-name JarvisAccessPolicy \
        --policy-document file:///tmp/jarvis-policy.json \
        --region "$REGION" 2>/dev/null || true
    
    rm /tmp/jarvis-policy.json
    echo -e "${GREEN}✓ IAM role configured${NC}"
fi

# Test deployment
echo -e "${YELLOW}Testing deployment...${NC}"
sleep 10

if [ -n "$BACKEND_URL" ]; then
    if curl -f -s "$BACKEND_URL/health" > /dev/null; then
        echo -e "${GREEN}✓ Health check passed${NC}"
    else
        echo -e "${YELLOW}⚠ Health check failed (may still be starting)${NC}"
    fi
fi

# Display results
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Elastic Beanstalk Details:${NC}"
echo -e "  Application:  ${GREEN}$APP_NAME${NC}"
echo -e "  Environment:  ${GREEN}$ENV_NAME${NC}"
if [ -n "$BACKEND_URL" ]; then
    echo -e "  Backend URL:  ${GREEN}$BACKEND_URL${NC}"
fi
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo -e "  View status:  ${YELLOW}eb status $ENV_NAME${NC}"
echo -e "  View logs:    ${YELLOW}eb logs $ENV_NAME${NC}"
echo -e "  SSH access:   ${YELLOW}eb ssh $ENV_NAME${NC}"
echo -e "  Open console: ${YELLOW}eb console $ENV_NAME${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Test the deployment:"
if [ -n "$BACKEND_URL" ]; then
    echo -e "   ${YELLOW}curl $BACKEND_URL/health${NC}"
fi
echo "2. Update mobile app BACKEND_URL"
echo "3. Monitor logs: eb logs $ENV_NAME --stream"
echo ""
echo -e "${BLUE}To update:${NC}"
echo -e "  ${YELLOW}eb deploy $ENV_NAME${NC}"
echo ""
echo -e "${BLUE}To terminate:${NC}"
echo -e "  ${YELLOW}eb terminate $ENV_NAME${NC}"
echo ""
