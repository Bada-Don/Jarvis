#!/usr/bin/env python3
"""
Setup AWS Resources for JARVIS
Creates DynamoDB table and S3 bucket if they don't exist.
Includes schema fix functionality for existing tables.
"""

import boto3
import os
import sys
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv('backend/.env')

def create_dynamodb_table(force_recreate=False):
    """
    Create the JarvisState DynamoDB table.
    
    Args:
        force_recreate: If True, delete and recreate table without prompting
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    region = os.getenv('AWS_REGION', 'us-east-1')
    table_name = os.getenv('AWS_DYNAMODB_TABLE_NAME', 'JarvisState')
    
    print(f"\n🔧 Setting up DynamoDB table: {table_name}")
    print(f"   Region: {region}")
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name=region)
        
        # Check if table already exists
        try:
            table = dynamodb.Table(table_name)
            table.load()
            
            # Display current schema
            print(f"\n📋 Current table schema:")
            for key in table.key_schema:
                print(f"   {key['AttributeName']} ({key['KeyType']})")
            
            # Check if it has the correct schema
            key_schema = table.key_schema
            has_correct_schema = (
                len(key_schema) == 2 and
                any(k['AttributeName'] == 'PK' and k['KeyType'] == 'HASH' for k in key_schema) and
                any(k['AttributeName'] == 'SK' and k['KeyType'] == 'RANGE' for k in key_schema)
            )
            
            if has_correct_schema:
                print(f"✅ Table '{table_name}' already exists with correct schema")
                print(f"   Status: {table.table_status}")
                return True
            else:
                print(f"\n⚠️ Table '{table_name}' exists but has incorrect schema")
                print(f"   Current keys: {[k['AttributeName'] for k in key_schema]}")
                print(f"   Expected keys: ['PK', 'SK']")
                
                if not force_recreate:
                    # Ask user if they want to recreate
                    print(f"\n⚠️ This will DELETE the existing table and recreate it!")
                    print(f"⚠️ All data in the table will be lost!")
                    print(f"\n❓ Do you want to delete and recreate the table? (yes/no)")
                    response = input("   > ").strip().lower()
                    
                    if response not in ['yes', 'y']:
                        print(f"❌ Keeping existing table. AWS features may not work correctly.")
                        return False
                
                # Delete old table
                print(f"\n🗑️ Deleting table '{table_name}'...")
                table.delete()
                print(f"⏳ Waiting for table to be deleted...")
                table.wait_until_not_exists()
                print(f"✅ Table deleted")
                
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceNotFoundException':
                raise
            print(f"\n✅ Table doesn't exist, will create new one")
        
        # Create table with correct schema (PK/SK pattern)
        print(f"\n📝 Creating table with correct schema...")
        print(f"   Primary Key: PK (String)")
        print(f"   Sort Key: SK (String)")
        
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'PK',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'SK',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'PK',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'SK',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'type',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'N'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'TypeTimestampIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'type',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'timestamp',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # Wait for table to be created
        print(f"⏳ Waiting for table to be created...")
        table.wait_until_exists()
        
        print(f"\n✅ Table '{table_name}' created successfully!")
        print(f"   Status: {table.table_status}")
        
        # Display new schema
        print(f"\n📋 New table schema:")
        table.reload()
        for key in table.key_schema:
            print(f"   {key['AttributeName']} ({key['KeyType']})")
        
        return True
        
    except ClientError as e:
        print(f"❌ Error creating DynamoDB table: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def create_s3_bucket():
    """Create the S3 bucket for JARVIS assets."""
    
    region = os.getenv('AWS_REGION', 'us-east-1')
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'jarvis-automation-assets')
    
    print(f"\n🔧 Creating S3 bucket: {bucket_name}")
    print(f"   Region: {region}")
    
    try:
        s3 = boto3.client('s3', region_name=region)
        
        # Check if bucket already exists
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' already exists")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code != '404':
                print(f"⚠️ Error checking bucket: {e}")
                return False
        
        # Create bucket
        print(f"📝 Creating bucket '{bucket_name}'...")
        
        if region == 'us-east-1':
            # us-east-1 doesn't need LocationConstraint
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        # Enable versioning (optional but recommended)
        s3.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        
        print(f"✅ Bucket '{bucket_name}' created successfully!")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyOwnedByYou':
            print(f"✅ Bucket '{bucket_name}' already exists and is owned by you")
            return True
        elif error_code == 'BucketAlreadyExists':
            print(f"❌ Bucket name '{bucket_name}' is already taken by another AWS account")
            print(f"   Please choose a different bucket name in your .env file")
            return False
        else:
            print(f"❌ Error creating S3 bucket: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def verify_aws_credentials():
    """Verify AWS credentials are configured."""
    
    print("\n🔍 Verifying AWS credentials...")
    
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"✅ AWS credentials verified")
        print(f"   Account ID: {identity['Account']}")
        print(f"   User ARN: {identity['Arn']}")
        return True
        
    except ClientError as e:
        print(f"❌ AWS credentials are invalid: {e}")
        return False
    except Exception as e:
        print(f"❌ Error verifying credentials: {e}")
        return False


def fix_schema_only():
    """Fix DynamoDB schema only (force recreate without S3 setup)."""
    
    print("=" * 60)
    print("🔧 Fixing DynamoDB Table Schema")
    print("=" * 60)
    
    # Verify credentials first
    if not verify_aws_credentials():
        print("\n❌ Fix failed: Invalid AWS credentials")
        return 1
    
    # Force recreate table
    if create_dynamodb_table(force_recreate=False):
        print(f"\n✅ Schema fix complete!")
        print(f"\nYou can now start JARVIS with: python JARVIS.py")
        return 0
    else:
        return 1


def main():
    """Main setup function."""
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--fix-schema', '-f']:
            return fix_schema_only()
        elif sys.argv[1] in ['--help', '-h']:
            print("=" * 60)
            print("🚀 JARVIS AWS Resources Setup")
            print("=" * 60)
            print("\nUsage:")
            print("  python setup_aws_resources.py           # Full setup (DynamoDB + S3)")
            print("  python setup_aws_resources.py --fix-schema  # Fix DynamoDB schema only")
            print("  python setup_aws_resources.py --help    # Show this help")
            print("\nOptions:")
            print("  --fix-schema, -f    Delete and recreate DynamoDB table with correct schema")
            print("  --help, -h          Show this help message")
            return 0
    
    print("=" * 60)
    print("🚀 JARVIS AWS Resources Setup")
    print("=" * 60)
    
    # Verify credentials first
    if not verify_aws_credentials():
        print("\n❌ Setup failed: Invalid AWS credentials")
        print("\nPlease check your .env file and ensure:")
        print("  - AWS_ACCESS_KEY_ID is set")
        print("  - AWS_SECRET_ACCESS_KEY is set")
        print("  - Credentials have necessary permissions")
        return 1
    
    # Create DynamoDB table
    dynamodb_success = create_dynamodb_table()
    
    # Create S3 bucket
    s3_success = create_s3_bucket()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Setup Summary")
    print("=" * 60)
    print(f"DynamoDB Table: {'✅ Ready' if dynamodb_success else '❌ Failed'}")
    print(f"S3 Bucket:      {'✅ Ready' if s3_success else '❌ Failed'}")
    
    if dynamodb_success and s3_success:
        print("\n✅ All AWS resources are ready!")
        print("\nYou can now start JARVIS with: python JARVIS.py")
        return 0
    else:
        print("\n⚠️ Some resources failed to create")
        print("Please check the errors above and try again")
        return 1


if __name__ == '__main__':
    sys.exit(main())
