#!/bin/bash
# Quick script to update .env file on EC2 without reinstalling dependencies

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
EC2_IP="${EC2_IP:-13.218.156.16}"
KEY_FILE="${KEY_FILE:-D:/Downloads/AWS Cred/jarvis-key.pem}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Updating .env on EC2${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if local .env exists
if [ ! -f "../backend/.env" ]; then
    echo -e "${RED}Error: backend/.env not found${NC}"
    exit 1
fi

echo -e "${YELLOW}Uploading .env file...${NC}"
scp -i "$KEY_FILE" ../backend/.env ec2-user@"$EC2_IP":/tmp/.env

echo -e "${YELLOW}Updating .env on EC2...${NC}"
ssh -i "$KEY_FILE" ec2-user@"$EC2_IP" << 'EOF'
  # Copy .env to application directory
  sudo cp /tmp/.env /opt/jarvis/.env
  sudo chown jarvis:jarvis /opt/jarvis/.env
  sudo chmod 600 /opt/jarvis/.env
  
  # Restart the service
  echo "Restarting JARVIS service..."
  sudo systemctl restart jarvis
  
  # Wait for service to start
  sleep 3
  
  # Check service status
  sudo systemctl status jarvis --no-pager | head -20
EOF

echo -e "${GREEN}✓ .env updated and service restarted${NC}"

# Test the deployment
echo -e "${YELLOW}Testing backend...${NC}"
sleep 2

if curl -f -s "http://$EC2_IP:5000/health" > /dev/null; then
    echo -e "${GREEN}✓ Backend is responding${NC}"
else
    echo -e "${RED}⚠ Warning: Health check failed${NC}"
fi

echo ""
echo -e "${GREEN}Done! Check logs with:${NC}"
echo -e "${YELLOW}ssh -i \"$KEY_FILE\" ec2-user@$EC2_IP 'sudo journalctl -u jarvis -f'${NC}"
