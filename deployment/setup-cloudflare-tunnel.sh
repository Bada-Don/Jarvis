#!/bin/bash
# Setup CloudFlare Tunnel for JARVIS Backend (Free SSL)

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

EC2_IP="${EC2_IP:-13.218.156.16}"
KEY_FILE="${KEY_FILE:-/d/Downloads/AWS Cred/jarvis-key.pem}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}CloudFlare Tunnel Setup${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "${YELLOW}Installing cloudflared on EC2...${NC}"

ssh -i "$KEY_FILE" ec2-user@"$EC2_IP" << 'EOF'
  # Download cloudflared
  wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
  sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
  sudo chmod +x /usr/local/bin/cloudflared
  
  echo "✓ cloudflared installed"
  
  # Create systemd service
  sudo tee /etc/systemd/system/cloudflared.service > /dev/null << 'SERVICE'
[Unit]
Description=CloudFlare Tunnel
After=network.target

[Service]
Type=simple
User=ec2-user
ExecStart=/usr/local/bin/cloudflared tunnel --url http://localhost:5000 --no-autoupdate
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

  echo "✓ Service file created"
  
  # Enable and start the service
  sudo systemctl daemon-reload
  sudo systemctl enable cloudflared
  sudo systemctl start cloudflared
  
  echo "✓ Service started"
  
  # Wait for tunnel to establish
  echo "Waiting for tunnel to establish..."
  sleep 5
  
  # Get the tunnel URL
  echo ""
  echo "=========================================="
  echo "Your CloudFlare Tunnel URL:"
  echo "=========================================="
  sudo journalctl -u cloudflared -n 50 | grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' | head -1
  echo "=========================================="
  echo ""
  echo "Use this URL in Amplify:"
  echo "NEXT_PUBLIC_BACKEND_URL=<the URL above>"
EOF

echo ""
echo -e "${GREEN}✓ CloudFlare Tunnel is running!${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Copy the tunnel URL from above"
echo "2. Update Amplify environment variable with that URL"
echo "3. Redeploy Amplify app"
echo "4. Judges can access without any security warnings!"
