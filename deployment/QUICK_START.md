# JARVIS AWS Deployment - Quick Start Guide

Get your JARVIS backend running on AWS in under 15 minutes!

## Prerequisites (5 minutes)

1. **AWS Account**
   - Create account at https://aws.amazon.com
   - Verify email and add payment method

2. **Install AWS CLI**
   ```bash
   # Windows (PowerShell)
   msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
   
   # macOS
   brew install awscli
   
   # Linux
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

3. **Configure AWS Credentials**
   ```bash
   aws configure
   # Enter your AWS Access Key ID
   # Enter your AWS Secret Access Key
   # Default region: us-east-1
   # Default output format: json
   ```

4. **Enable Bedrock Models**
   - Go to: https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess
   - Click "Manage model access"
   - Enable: Claude 3.5 Haiku and Claude 3.5 Sonnet
   - Click "Save changes"

## Deployment (10 minutes)

### Option 1: One-Click CloudFormation (Recommended)

```bash
cd deployment
chmod +x deploy-cloudformation.sh deploy-to-ec2.sh
./deploy-cloudformation.sh
```

Wait for the stack to complete (5-7 minutes), then:

```bash
./deploy-to-ec2.sh
```

That's it! Your backend is now running on AWS.

### Option 2: Docker + ECS Fargate

```bash
cd deployment
chmod +x deploy-ecs.sh
./deploy-ecs.sh
```

### Option 3: Elastic Beanstalk

```bash
cd deployment
chmod +x deploy-elasticbeanstalk.sh
./deploy-elasticbeanstalk.sh
```

## Verify Deployment

1. **Get your backend URL:**
   ```bash
   aws cloudformation describe-stacks \
     --stack-name jarvis-infrastructure \
     --query 'Stacks[0].Outputs[?OutputKey==`BackendURL`].OutputValue' \
     --output text
   ```

2. **Test the health endpoint:**
   ```bash
   curl http://<BACKEND_URL>/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "message": "JARVIS Backend is running",
     "services": {
       "planner": true,
       "aws": true,
       "firebase": false
     }
   }
   ```

3. **Test WebSocket connection:**
   ```bash
   npm install -g wscat
   wscat -c ws://<BACKEND_URL>
   ```

## Update Mobile App

1. **Edit ChatInterface/.env:**
   ```env
   BACKEND_URL=http://<YOUR_EC2_IP>:5000
   AWS_REGION=us-east-1
   AWS_DYNAMODB_TABLE_NAME=JarvisState
   ```

2. **Rebuild the app:**
   ```bash
   cd ChatInterface
   npm install
   npx expo start
   ```

## Test End-to-End

1. Open mobile app
2. Scan QR code to pair with desktop
3. Send command: "open notepad"
4. Verify notepad opens on desktop
5. Check status updates in mobile app

## Common Issues

### "Access Denied" when calling Bedrock
- Go to Bedrock console and enable model access
- Wait 1-2 minutes for permissions to propagate

### "Cannot connect to backend"
- Check security group allows port 5000
- Verify EC2 instance is running
- Check backend logs: `ssh -i jarvis-key.pem ec2-user@<EC2_IP> 'sudo journalctl -u jarvis -f'`

### "WebSocket connection failed"
- Verify port 5000 is open in security group
- Check if backend service is running
- Test with curl first: `curl http://<BACKEND_URL>/health`

## View Logs

```bash
# SSH into EC2
ssh -i jarvis-key.pem ec2-user@<EC2_IP>

# View backend logs
sudo journalctl -u jarvis -f

# Check service status
sudo systemctl status jarvis
```

## Update Backend Code

After making changes to backend code:

```bash
cd deployment
./deploy-to-ec2.sh
```

This will:
1. Upload new code to EC2
2. Install any new dependencies
3. Restart the service
4. Verify deployment

## Cost Estimate

With AWS Free Tier:
- EC2 t3.micro: FREE (750 hours/month)
- DynamoDB: FREE (25GB storage, 25 read/write units)
- S3: FREE (5GB storage, 20,000 GET requests)
- Data Transfer: FREE (first 100GB/month)

**Total: $0/month for first year** (within free tier limits)

After free tier:
- EC2 t3.micro: ~$7.50/month
- DynamoDB: ~$0.25/month (pay per request)
- S3: ~$0.50/month
- **Total: ~$8-10/month**

## Next Steps

1. ✅ Backend deployed and running
2. ✅ Mobile app connected
3. ⏭️ Test all commands
4. ⏭️ Enable HTTPS (optional)
5. ⏭️ Set up monitoring
6. ⏭️ Configure auto-scaling (optional)

## Support

- **Deployment Issues:** Check `DEPLOYMENT_CHECKLIST.md`
- **Detailed Guide:** See `README.md`
- **AWS Console:** https://console.aws.amazon.com
- **CloudWatch Logs:** https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups

## Cleanup

When you're done and want to delete everything:

```bash
aws cloudformation delete-stack --stack-name jarvis-infrastructure
```

This will delete:
- EC2 instance
- DynamoDB table
- S3 bucket
- All networking resources
- IAM roles

**Note:** This is permanent and cannot be undone!

---

**Estimated Time:** 15 minutes  
**Difficulty:** Easy  
**Cost:** Free (with AWS Free Tier)
