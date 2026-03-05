#!/bin/bash
# JARVIS Backend Deployment Script for EC2
# This script deploys the backend code to an existing EC2 instance

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="${STACK_NAME:-jarvis-infrastructure}"
KEY_FILE="${KEY_FILE:-jarvis-key.pem}"
REGION="${AWS_REGION:-us-east-1}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}JARVIS Backend Deployment to EC2${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Install it from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if key file exists
if [ ! -f "$KEY_FILE" ]; then
    echo -e "${RED}Error: Key file $KEY_FILE not found${NC}"
    echo "Create a key pair first:"
    echo "  aws ec2 create-key-pair --key-name jarvis-key --query 'KeyMaterial' --output text > jarvis-key.pem"
    echo "  chmod 400 jarvis-key.pem"
    exit 1
fi

# Get EC2 instance IP from CloudFormation
echo -e "${YELLOW}Getting EC2 instance IP...${NC}"
EC2_IP=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --query 'Stacks[0].Outputs[?OutputKey==`EC2PublicIP`].OutputValue' \
  --output text \
  --region "$REGION" 2>/dev/null)

if [ -z "$EC2_IP" ]; then
    echo -e "${RED}Error: Could not get EC2 IP from CloudFormation stack${NC}"
    echo "Make sure the stack '$STACK_NAME' exists and is deployed"
    exit 1
fi

echo -e "${GREEN}✓ EC2 Instance IP: $EC2_IP${NC}"

# Test SSH connection
echo -e "${YELLOW}Testing SSH connection...${NC}"
if ! ssh -i "$KEY_FILE" -o ConnectTimeout=10 -o StrictHostKeyChecking=no ec2-user@"$EC2_IP" "echo 'SSH connection successful'" &> /dev/null; then
    echo -e "${RED}Error: Cannot connect to EC2 instance via SSH${NC}"
    echo "Check:"
    echo "  1. Security group allows SSH from your IP"
    echo "  2. Key file has correct permissions (chmod 400)"
    echo "  3. Instance is running"
    exit 1
fi
echo -e "${GREEN}✓ SSH connection successful${NC}"

# Create temporary directory for deployment
TEMP_DIR=$(mktemp -d)
echo -e "${YELLOW}Preparing files for deployment...${NC}"

# Copy backend files to temp directory
cp -r ../backend/* "$TEMP_DIR/"

# Remove unnecessary files
rm -rf "$TEMP_DIR/__pycache__"
rm -rf "$TEMP_DIR/uploads/*"
rm -rf "$TEMP_DIR/logs/*"
rm -f "$TEMP_DIR/.env"
rm -f "$TEMP_DIR/test_*.py"

echo -e "${GREEN}✓ Files prepared${NC}"

# Upload files to EC2
echo -e "${YELLOW}Uploading files to EC2...${NC}"
ssh -i "$KEY_FILE" ec2-user@"$EC2_IP" "sudo rm -rf /tmp/jarvis && mkdir -p /tmp/jarvis"
scp -i "$KEY_FILE" -r "$TEMP_DIR"/* ec2-user@"$EC2_IP":/tmp/jarvis/

echo -e "${GREEN}✓ Files uploaded${NC}"

# Deploy on EC2
echo -e "${YELLOW}Deploying on EC2...${NC}"
ssh -i "$KEY_FILE" ec2-user@"$EC2_IP" << 'EOF'
  set -e
  
  # Stop the service
  sudo systemctl stop jarvis || true
  
  # Copy files to application directory
  sudo cp -r /tmp/jarvis/* /opt/jarvis/
  sudo chown -R jarvis:jarvis /opt/jarvis
  
  # Install/update dependencies
  sudo su - jarvis -c "cd /opt/jarvis && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"
  
  # Create necessary directories
  sudo su - jarvis -c "mkdir -p /opt/jarvis/uploads /opt/jarvis/logs /opt/jarvis/data"
  
  # Start the service
  sudo systemctl start jarvis
  sudo systemctl enable jarvis
  
  # Wait for service to start
  sleep 5
  
  # Check service status
  sudo systemctl status jarvis --no-pager
EOF

echo -e "${GREEN}✓ Deployment complete${NC}"

# Cleanup
rm -rf "$TEMP_DIR"

# Test the deployment
echo -e "${YELLOW}Testing deployment...${NC}"
sleep 3

if curl -f -s "http://$EC2_IP:5000/health" > /dev/null; then
    echo -e "${GREEN}✓ Backend is responding${NC}"
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}⚠ Warning: Health check failed${NC}"
    echo "Check logs with:"
    echo "  ssh -i $KEY_FILE ec2-user@$EC2_IP 'sudo journalctl -u jarvis -n 50'"
fi

# Display connection info
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Backend URL: ${GREEN}http://$EC2_IP:5000${NC}"
echo -e "SSH Command: ${YELLOW}ssh -i $KEY_FILE ec2-user@$EC2_IP${NC}"
echo -e "View Logs:   ${YELLOW}ssh -i $KEY_FILE ec2-user@$EC2_IP 'sudo journalctl -u jarvis -f'${NC}"
echo ""
echo -e "${GREEN}Next Steps:${NC}"
echo "1. Update mobile app BACKEND_URL to: http://$EC2_IP:5000"
echo "2. Test the connection from mobile app"
echo "3. Monitor logs for any issues"
echo ""
