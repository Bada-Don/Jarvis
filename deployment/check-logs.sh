#!/bin/bash
# Quick script to check backend logs on EC2

EC2_IP="${EC2_IP:-13.218.156.16}"
KEY_FILE="${KEY_FILE:-D:/Downloads/AWS Cred/jarvis-key.pem}"

echo "Fetching last 50 lines of JARVIS backend logs..."
echo "================================================"
ssh -i "$KEY_FILE" ec2-user@"$EC2_IP" 'sudo journalctl -u jarvis -n 50 --no-pager'
