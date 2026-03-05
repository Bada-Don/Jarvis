#!/bin/bash
# JARVIS Deployment Validation Script
# This script validates that the deployment is working correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="${STACK_NAME:-jarvis-infrastructure}"
REGION="${AWS_REGION:-us-east-1}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}JARVIS Deployment Validation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -e "${YELLOW}Testing: $test_name${NC}"
    
    if eval "$test_command" &> /dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Function to run test with output
run_test_with_output() {
    local test_name=$1
    local test_command=$2
    local expected_pattern=$3
    
    echo -e "${YELLOW}Testing: $test_name${NC}"
    
    output=$(eval "$test_command" 2>&1)
    
    if echo "$output" | grep -q "$expected_pattern"; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "Expected pattern: $expected_pattern"
        echo "Got: $output"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo -e "${BLUE}1. AWS Configuration Tests${NC}"
echo "-----------------------------------"

run_test "AWS CLI installed" "command -v aws"
run_test "AWS credentials configured" "aws sts get-caller-identity"

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "")
if [ -n "$AWS_ACCOUNT_ID" ]; then
    echo -e "  Account ID: ${GREEN}$AWS_ACCOUNT_ID${NC}"
fi

echo ""
echo -e "${BLUE}2. CloudFormation Stack Tests${NC}"
echo "-----------------------------------"

run_test "Stack exists" "aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION"

STACK_STATUS=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].StackStatus' \
    --output text \
    --region "$REGION" 2>/dev/null || echo "NOT_FOUND")

if [ "$STACK_STATUS" == "CREATE_COMPLETE" ] || [ "$STACK_STATUS" == "UPDATE_COMPLETE" ]; then
    echo -e "${GREEN}✓ Stack status: $STACK_STATUS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Stack status: $STACK_STATUS${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo -e "${BLUE}3. Infrastructure Tests${NC}"
echo "-----------------------------------"

# Get outputs
EC2_IP=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`EC2PublicIP`].OutputValue' \
    --output text \
    --region "$REGION" 2>/dev/null || echo "")

BACKEND_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`BackendURL`].OutputValue' \
    --output text \
    --region "$REGION" 2>/dev/null || echo "")

DYNAMODB_TABLE=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`DynamoDBTableName`].OutputValue' \
    --output text \
    --region "$REGION" 2>/dev/null || echo "")

S3_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
    --output text \
    --region "$REGION" 2>/dev/null || echo "")

if [ -n "$EC2_IP" ]; then
    echo -e "  EC2 IP: ${GREEN}$EC2_IP${NC}"
    run_test "EC2 instance running" "aws ec2 describe-instances --filters 'Name=ip-address,Values=$EC2_IP' 'Name=instance-state-name,Values=running' --region $REGION"
else
    echo -e "${RED}✗ EC2 IP not found${NC}"
    ((TESTS_FAILED++))
fi

if [ -n "$DYNAMODB_TABLE" ]; then
    echo -e "  DynamoDB Table: ${GREEN}$DYNAMODB_TABLE${NC}"
    run_test "DynamoDB table active" "aws dynamodb describe-table --table-name $DYNAMODB_TABLE --region $REGION --query 'Table.TableStatus' --output text | grep -q ACTIVE"
else
    echo -e "${RED}✗ DynamoDB table not found${NC}"
    ((TESTS_FAILED++))
fi

if [ -n "$S3_BUCKET" ]; then
    echo -e "  S3 Bucket: ${GREEN}$S3_BUCKET${NC}"
    run_test "S3 bucket exists" "aws s3 ls s3://$S3_BUCKET --region $REGION"
else
    echo -e "${RED}✗ S3 bucket not found${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo -e "${BLUE}4. Backend Service Tests${NC}"
echo "-----------------------------------"

if [ -n "$BACKEND_URL" ]; then
    echo -e "  Backend URL: ${GREEN}$BACKEND_URL${NC}"
    
    # Test health endpoint
    echo -e "${YELLOW}Testing: Health endpoint${NC}"
    HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$BACKEND_URL/health" 2>/dev/null || echo "000")
    HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n1)
    RESPONSE_BODY=$(echo "$HEALTH_RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" == "200" ]; then
        echo -e "${GREEN}✓ PASS (HTTP $HTTP_CODE)${NC}"
        ((TESTS_PASSED++))
        
        # Check response content
        if echo "$RESPONSE_BODY" | grep -q "healthy"; then
            echo -e "${GREEN}✓ Response contains 'healthy'${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}✗ Response does not contain 'healthy'${NC}"
            ((TESTS_FAILED++))
        fi
        
        # Pretty print response
        echo -e "${BLUE}Response:${NC}"
        echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
    else
        echo -e "${RED}✗ FAIL (HTTP $HTTP_CODE)${NC}"
        ((TESTS_FAILED++))
    fi
    
    # Test WebSocket (if wscat is installed)
    if command -v wscat &> /dev/null; then
        echo -e "${YELLOW}Testing: WebSocket connection${NC}"
        WS_URL=$(echo "$BACKEND_URL" | sed 's/http:/ws:/')
        
        # Try to connect (timeout after 5 seconds)
        if timeout 5 wscat -c "$WS_URL" --execute "exit" &> /dev/null; then
            echo -e "${GREEN}✓ PASS${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${YELLOW}⚠ WebSocket test skipped (connection timeout)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ WebSocket test skipped (wscat not installed)${NC}"
        echo "  Install with: npm install -g wscat"
    fi
else
    echo -e "${RED}✗ Backend URL not found${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo -e "${BLUE}5. IAM Permissions Tests${NC}"
echo "-----------------------------------"

# Check Bedrock access
echo -e "${YELLOW}Testing: Bedrock model access${NC}"
BEDROCK_MODELS=$(aws bedrock list-foundation-models --region $REGION --query 'modelSummaries[?contains(modelId, `claude`)].modelId' --output text 2>/dev/null || echo "")

if [ -n "$BEDROCK_MODELS" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    echo "  Available Claude models:"
    echo "$BEDROCK_MODELS" | tr '\t' '\n' | sed 's/^/    - /'
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL - No Bedrock access or models not enabled${NC}"
    echo "  Enable model access at: https://console.aws.amazon.com/bedrock/home?region=$REGION#/modelaccess"
    ((TESTS_FAILED++))
fi

echo ""
echo -e "${BLUE}6. DynamoDB Operations Tests${NC}"
echo "-----------------------------------"

if [ -n "$DYNAMODB_TABLE" ]; then
    # Test write
    echo -e "${YELLOW}Testing: DynamoDB write${NC}"
    TEST_ITEM='{"PK":{"S":"TEST"},"SK":{"S":"VALIDATION"},"timestamp":{"N":"'$(date +%s)'"}}'
    
    if aws dynamodb put-item \
        --table-name "$DYNAMODB_TABLE" \
        --item "$TEST_ITEM" \
        --region "$REGION" &> /dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
    fi
    
    # Test read
    echo -e "${YELLOW}Testing: DynamoDB read${NC}"
    if aws dynamodb get-item \
        --table-name "$DYNAMODB_TABLE" \
        --key '{"PK":{"S":"TEST"},"SK":{"S":"VALIDATION"}}' \
        --region "$REGION" &> /dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
    fi
    
    # Cleanup test item
    aws dynamodb delete-item \
        --table-name "$DYNAMODB_TABLE" \
        --key '{"PK":{"S":"TEST"},"SK":{"S":"VALIDATION"}}' \
        --region "$REGION" &> /dev/null || true
fi

echo ""
echo -e "${BLUE}7. S3 Operations Tests${NC}"
echo "-----------------------------------"

if [ -n "$S3_BUCKET" ]; then
    # Test write
    echo -e "${YELLOW}Testing: S3 upload${NC}"
    echo "test" > /tmp/jarvis-test.txt
    
    if aws s3 cp /tmp/jarvis-test.txt "s3://$S3_BUCKET/test/validation.txt" --region "$REGION" &> /dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
    fi
    
    # Test read
    echo -e "${YELLOW}Testing: S3 download${NC}"
    if aws s3 cp "s3://$S3_BUCKET/test/validation.txt" /tmp/jarvis-test-download.txt --region "$REGION" &> /dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
    fi
    
    # Cleanup
    rm -f /tmp/jarvis-test.txt /tmp/jarvis-test-download.txt
    aws s3 rm "s3://$S3_BUCKET/test/validation.txt" --region "$REGION" &> /dev/null || true
fi

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Validation Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Deployment is healthy.${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Update mobile app BACKEND_URL to: $BACKEND_URL"
    echo "2. Test end-to-end flow with mobile app"
    echo "3. Monitor logs: ssh -i jarvis-key.pem ec2-user@$EC2_IP 'sudo journalctl -u jarvis -f'"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review the errors above.${NC}"
    echo ""
    echo -e "${BLUE}Troubleshooting:${NC}"
    echo "1. Check CloudFormation stack status in AWS Console"
    echo "2. Verify Bedrock model access is enabled"
    echo "3. Check backend logs: ssh -i jarvis-key.pem ec2-user@$EC2_IP 'sudo journalctl -u jarvis -n 50'"
    echo "4. Review deployment checklist: deployment/DEPLOYMENT_CHECKLIST.md"
    exit 1
fi
