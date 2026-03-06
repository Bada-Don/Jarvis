#!/bin/bash
# Fix WebSocket SSL connection issues

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

EC2_IP="${EC2_IP:-13.218.156.16}"
KEY_FILE="${KEY_FILE:-/d/Downloads/AWS Cred/jarvis-key.pem}"

echo -e "${YELLOW}Checking nginx configuration...${NC}"

ssh -i "$KEY_FILE" ec2-user@"$EC2_IP" << 'EOF'
  # Check if nginx is running
  sudo systemctl status nginx --no-pager | head -10
  
  echo ""
  echo "Checking nginx error logs..."
  sudo tail -20 /var/log/nginx/error.log
  
  echo ""
  echo "Testing backend connection..."
  curl -s http://localhost:5000/health
  
  echo ""
  echo "Testing HTTPS endpoint..."
  curl -k -s https://localhost/health
EOF

echo ""
echo -e "${GREEN}Diagnostics complete${NC}"
echo ""
echo "If you see connection errors, the issue might be:"
echo "1. Self-signed certificate rejected by browser"
echo "2. WebSocket upgrade not working properly"
echo "3. CORS issues"
echo ""
echo "Try accessing https://13.218.156.16/health in your browser"
echo "Accept the security warning to trust the certificate"
