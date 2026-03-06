#!/bin/bash
# Setup SSL/TLS for JARVIS Backend using nginx and self-signed certificate
# This enables HTTPS access required for Amplify deployment

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}JARVIS Backend - SSL Setup${NC}"
echo -e "${GREEN}========================================${NC}"

# Configuration
EC2_IP="${EC2_IP:-13.218.156.16}"
KEY_FILE="${KEY_FILE:-D:/Downloads/AWS Cred/jarvis-key.pem}"
DOMAIN="${DOMAIN:-jarvis-backend.local}"

echo -e "${YELLOW}Installing nginx and SSL tools...${NC}"
ssh -i "$KEY_FILE" ec2-user@"$EC2_IP" << 'EOF'
  # Install nginx
  sudo dnf install -y nginx
  
  # Create SSL directory
  sudo mkdir -p /etc/nginx/ssl
  
  # Generate self-signed certificate (valid for 365 days)
  sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/jarvis.key \
    -out /etc/nginx/ssl/jarvis.crt \
    -subj "/C=US/ST=State/L=City/O=JARVIS/CN=jarvis-backend"
  
  echo "✓ SSL certificate generated"
EOF

echo -e "${YELLOW}Configuring nginx...${NC}"
ssh -i "$KEY_FILE" ec2-user@"$EC2_IP" << 'EOF'
  # Create nginx configuration
  sudo tee /etc/nginx/conf.d/jarvis.conf > /dev/null << 'NGINX_CONF'
# JARVIS Backend - HTTPS Reverse Proxy
upstream jarvis_backend {
    server 127.0.0.1:5000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name _;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/jarvis.crt;
    ssl_certificate_key /etc/nginx/ssl/jarvis.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # CORS Headers for Amplify
    add_header Access-Control-Allow-Origin "*" always;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;

    # Proxy to JARVIS backend
    location / {
        proxy_pass http://jarvis_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # WebSocket support for Socket.IO
    location /socket.io/ {
        proxy_pass http://jarvis_backend;
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
NGINX_CONF

  echo "✓ Nginx configuration created"
  
  # Test nginx configuration
  sudo nginx -t
  
  # Enable and start nginx
  sudo systemctl enable nginx
  sudo systemctl restart nginx
  
  echo "✓ Nginx started"
EOF

echo -e "${GREEN}✓ SSL setup complete${NC}"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Next Steps${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "1. Update Security Group to allow HTTPS:"
echo -e "   ${YELLOW}Port 443 (HTTPS) - 0.0.0.0/0${NC}"
echo ""
echo -e "2. Update your Amplify environment variables:"
echo -e "   ${YELLOW}NEXT_PUBLIC_BACKEND_URL=https://$EC2_IP${NC}"
echo ""
echo -e "3. Test HTTPS connection:"
echo -e "   ${YELLOW}curl -k https://$EC2_IP/health${NC}"
echo ""
echo -e "4. Redeploy your Amplify app with new backend URL"
echo ""
