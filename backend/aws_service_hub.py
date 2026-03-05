"""
AWS Service Hub for JARVIS Backend
Centralized boto3 client for Bedrock, S3, and DynamoDB.
Replaces Firebase services with AWS-native architecture.
"""

import boto3
import json
import time
import uuid
import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from decimal import Decimal


class AWSServiceHub:
    """
    AWS service hub for backend server.
    Manages Bedrock LLM, DynamoDB state, and S3 storage.
    """
    
    def __init__(
        self,
        region_name: str = "us-east-1",
        dynamodb_table_name: str = "JarvisState",
        s3_bucket_name: str = "jarvis-automation-assets"
    ):
        """
        Initialize AWS services.
        
        Args:
            region_name: AWS region (default: us-east-1)
            dynamodb_table_name: DynamoDB table name for state storage
            s3_bucket_name: S3 bucket name for screenshots and assets
        
        Raises:
            RuntimeError: If AWS initialization fails
        """
        self.region_name = region_name
        self.dynamodb_table_name = dynamodb_table_name
        self.s3_bucket_name = s3_bucket_name
        self.device_id = None
        
        try:
            # Initialize AWS clients
            self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=region_name)
            self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
            self.s3_client = boto3.client('s3', region_name=region_name)
            
            # Get DynamoDB table reference
            self.table = self.dynamodb.Table(dynamodb_table_name)
            
            print(f"✅ AWS Service Hub initialized")
            print(f"   Region: {region_name}")
            print(f"   DynamoDB Table: {dynamodb_table_name}")
            print(f"   S3 Bucket: {s3_bucket_name}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize AWS services: {e}")
    
    # ==================== Device Management ====================
    
    def set_device_id(self, device_id: str) -> None:
        """
        Set the device ID for this backend instance.
        
        Args:
            device_id: Unique identifier for this desktop device
        """
        self.device_id = device_id
        print(f"✅ Device ID set: {device_id}")
    
    def register_device(
        self,
        device_id: str,
        device_type: str = "desktop",
        version: str = "1.0.0"
    ) -> bool:
        """
        Register a device in DynamoDB.
        
        Args:
            device_id: Unique identifier for the device
            device_type: Type of device ("desktop" or "mobile")
            version: Application version
        
        Returns:
            True if registration successful, False otherwise
        """
        try:
            timestamp = int(time.time())
            self.table.put_item(
                Item={
                    'PK': f'DEVICE#{device_id}',
                    'SK': 'METADATA',
                    'type': device_type,
                    'paired': False,
                    'pairedDeviceId': None,
                    'lastSeen': timestamp,
                    'version': version,
                    'registeredAt': timestamp
                }
            )
            
            print(f"✅ Device registered: {device_id} ({device_type})")
            return True
            
        except ClientError as e:
            print(f"❌ Failed to register device: {e}")
            return False
    
    def update_presence(self, device_id: str) -> bool:
        """
        Update device last-seen timestamp.
        
        Args:
            device_id: Device identifier
        
        Returns:
            True if update successful, False otherwise
        """
        try:
            self.table.update_item(
                Key={
                    'PK': f'DEVICE#{device_id}',
                    'SK': 'METADATA'
                },
                UpdateExpression='SET lastSeen = :timestamp',
                ExpressionAttributeValues={
                    ':timestamp': int(time.time())
                }
            )
            return True
            
        except ClientError as e:
            print(f"❌ Failed to update presence: {e}")
            return False
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get device information from DynamoDB.
        
        Args:
            device_id: Device identifier
        
        Returns:
            Device info dictionary or None if not found
        """
        try:
            response = self.table.get_item(
                Key={
                    'PK': f'DEVICE#{device_id}',
                    'SK': 'METADATA'
                }
            )
            return response.get('Item')
            
        except ClientError as e:
            print(f"❌ Failed to get device info: {e}")
            return None
    
    def is_device_paired(self, device_id: str) -> bool:
        """
        Check if a device is paired.
        
        Args:
            device_id: Device identifier
        
        Returns:
            True if paired, False otherwise
        """
        device_info = self.get_device_info(device_id)
        if device_info:
            return device_info.get('paired', False)
        return False
    
    def pair_devices(self, desktop_id: str, mobile_id: str) -> bool:
        """
        Pair a desktop and mobile device.
        
        Args:
            desktop_id: Desktop device identifier
            mobile_id: Mobile device identifier
        
        Returns:
            True if pairing successful, False otherwise
        """
        try:
            timestamp = int(time.time())
            
            # Update desktop device
            self.table.update_item(
                Key={
                    'PK': f'DEVICE#{desktop_id}',
                    'SK': 'METADATA'
                },
                UpdateExpression='SET paired = :paired, pairedDeviceId = :mobile_id, pairedAt = :timestamp',
                ExpressionAttributeValues={
                    ':paired': True,
                    ':mobile_id': mobile_id,
                    ':timestamp': timestamp
                }
            )
            
            # Update mobile device
            self.table.update_item(
                Key={
                    'PK': f'DEVICE#{mobile_id}',
                    'SK': 'METADATA'
                },
                UpdateExpression='SET paired = :paired, pairedDeviceId = :desktop_id, pairedAt = :timestamp',
                ExpressionAttributeValues={
                    ':paired': True,
                    ':desktop_id': desktop_id,
                    ':timestamp': timestamp
                }
            )
            
            print(f"✅ Devices paired: {desktop_id} <=> {mobile_id}")
            return True
            
        except ClientError as e:
            print(f"❌ Failed to pair devices: {e}")
            return False

    
    # ==================== Task History Management ====================
    
    def save_task_history(
        self,
        device_id: str,
        task_id: str,
        task_data: Dict[str, Any],
        ttl_hours: int = 24
    ) -> bool:
        """
        Save task to history with TTL (keeps last 10 tasks).
        
        Args:
            device_id: Device identifier
            task_id: Unique task identifier
            task_data: Task data dictionary
            ttl_hours: Time-to-live in hours (default: 24)
        
        Returns:
            True if save successful, False otherwise
        """
        try:
            timestamp = int(time.time())
            ttl = timestamp + (ttl_hours * 3600)
            
            # Convert float values to Decimal for DynamoDB
            task_data_decimal = json.loads(
                json.dumps(task_data),
                parse_float=Decimal
            )
            
            self.table.put_item(
                Item={
                    'PK': f'DEVICE#{device_id}',
                    'SK': f'TASK#{timestamp}#{task_id}',
                    'taskId': task_id,
                    'timestamp': timestamp,
                    'ttl': ttl,
                    **task_data_decimal
                }
            )
            
            # Cleanup old tasks (keep only last 10)
            self._cleanup_old_tasks(device_id)
            
            return True
            
        except ClientError as e:
            print(f"❌ Failed to save task history: {e}")
            return False
    
    def _cleanup_old_tasks(self, device_id: str, keep_count: int = 10) -> None:
        """
        Keep only the most recent N tasks for a device.
        
        Args:
            device_id: Device identifier
            keep_count: Number of tasks to keep (default: 10)
        """
        try:
            # Query all tasks for device
            response = self.table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':pk': f'DEVICE#{device_id}',
                    ':sk_prefix': 'TASK#'
                },
                ScanIndexForward=False  # Sort descending (newest first)
            )
            
            tasks = response.get('Items', [])
            
            # Delete tasks beyond keep_count
            if len(tasks) > keep_count:
                for task in tasks[keep_count:]:
                    self.table.delete_item(
                        Key={
                            'PK': task['PK'],
                            'SK': task['SK']
                        }
                    )
                print(f"🧹 Cleaned up {len(tasks) - keep_count} old tasks")
                
        except ClientError as e:
            print(f"⚠️ Failed to cleanup old tasks: {e}")
    
    def get_task_history(self, device_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent task history for a device.
        
        Args:
            device_id: Device identifier
            limit: Maximum number of tasks to retrieve
        
        Returns:
            List of task dictionaries
        """
        try:
            response = self.table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':pk': f'DEVICE#{device_id}',
                    ':sk_prefix': 'TASK#'
                },
                ScanIndexForward=False,  # Sort descending (newest first)
                Limit=limit
            )
            
            return response.get('Items', [])
            
        except ClientError as e:
            print(f"❌ Failed to get task history: {e}")
            return []
    
    # ==================== Status & Command Management ====================
    
    def send_status(self, device_id: str, status: Dict[str, Any]) -> Optional[str]:
        """
        Send a status update to a device.
        
        Args:
            device_id: Target device identifier
            status: Status data dictionary
        
        Returns:
            Message ID if successful, None otherwise
        """
        try:
            message_id = str(uuid.uuid4())
            timestamp = int(time.time())
            ttl = timestamp + 3600  # 1 hour TTL
            
            # Convert float values to Decimal for DynamoDB
            status_decimal = json.loads(
                json.dumps(status),
                parse_float=Decimal
            )
            
            self.table.put_item(
                Item={
                    'PK': f'DEVICE#{device_id}',
                    'SK': f'STATUS#{timestamp}#{message_id}',
                    'messageId': message_id,
                    'type': 'status',
                    'timestamp': timestamp,
                    'ttl': ttl,
                    **status_decimal
                }
            )
            
            return message_id
            
        except ClientError as e:
            print(f"❌ Failed to send status: {e}")
            return None
    
    def send_command(self, device_id: str, command: Dict[str, Any]) -> Optional[str]:
        """
        Send a command to a device.
        
        Args:
            device_id: Target device identifier
            command: Command data dictionary
        
        Returns:
            Message ID if successful, None otherwise
        """
        try:
            message_id = str(uuid.uuid4())
            timestamp = int(time.time())
            ttl = timestamp + 3600  # 1 hour TTL
            
            # Convert float values to Decimal for DynamoDB
            command_decimal = json.loads(
                json.dumps(command),
                parse_float=Decimal
            )
            
            self.table.put_item(
                Item={
                    'PK': f'DEVICE#{device_id}',
                    'SK': f'COMMAND#{timestamp}#{message_id}',
                    'messageId': message_id,
                    'type': 'command',
                    'timestamp': timestamp,
                    'processed': False,
                    'ttl': ttl,
                    **command_decimal
                }
            )
            
            print(f"✅ Command sent to {device_id}: {message_id}")
            return message_id
            
        except ClientError as e:
            print(f"❌ Failed to send command: {e}")
            return None
    
    def poll_commands(self, device_id: str, last_timestamp: int = 0) -> List[Dict[str, Any]]:
        """
        Poll for new commands for this device.
        
        Args:
            device_id: Device identifier to poll commands for
            last_timestamp: Only return commands newer than this timestamp
        
        Returns:
            List of command dictionaries
        """
        try:
            # Query for unprocessed commands
            response = self.table.query(
                KeyConditionExpression='PK = :pk AND SK > :sk',
                FilterExpression='#processed = :false',
                ExpressionAttributeNames={
                    '#processed': 'processed'
                },
                ExpressionAttributeValues={
                    ':pk': f'DEVICE#{device_id}',
                    ':sk': f'COMMAND#{last_timestamp}',
                    ':false': False
                },
                ScanIndexForward=True,  # Sort ascending (oldest first)
                Limit=50
            )
            
            commands = response.get('Items', [])
            
            # Mark commands as processed
            for command in commands:
                try:
                    self.table.update_item(
                        Key={
                            'PK': command['PK'],
                            'SK': command['SK']
                        },
                        UpdateExpression='SET #processed = :true',
                        ExpressionAttributeNames={
                            '#processed': 'processed'
                        },
                        ExpressionAttributeValues={
                            ':true': True
                        }
                    )
                except Exception as e:
                    print(f"⚠️ Failed to mark command as processed: {e}")
            
            return commands
            
        except ClientError as e:
            print(f"❌ Failed to poll commands: {e}")
            return []
    
    def get_recent_status(self, device_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent status updates for a device.
        
        Args:
            device_id: Device identifier
            limit: Maximum number of status updates to retrieve
        
        Returns:
            List of status dictionaries
        """
        try:
            response = self.table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':pk': f'DEVICE#{device_id}',
                    ':sk_prefix': 'STATUS#'
                },
                ScanIndexForward=False,  # Sort descending (newest first)
                Limit=limit
            )
            
            return response.get('Items', [])
            
        except ClientError as e:
            print(f"❌ Failed to get recent status: {e}")
            return []
    
    # ==================== S3 Storage Management ====================
    
    def upload_screenshot(
        self,
        device_id: str,
        screenshot_data: bytes,
        filename: str,
        ttl_hours: int = 1
    ) -> Optional[str]:
        """
        Upload screenshot to S3 with TTL.
        
        Args:
            device_id: Device identifier
            screenshot_data: Screenshot image bytes
            filename: Filename for the screenshot
            ttl_hours: Time-to-live in hours (default: 1)
        
        Returns:
            S3 object key if successful, None otherwise
        """
        try:
            timestamp = int(time.time())
            object_key = f"screenshots/{device_id}/{timestamp}_{filename}"
            
            # Calculate expiration time
            expiration = datetime.utcnow() + timedelta(hours=ttl_hours)
            
            # Upload to S3 with metadata
            self.s3_client.put_object(
                Bucket=self.s3_bucket_name,
                Key=object_key,
                Body=screenshot_data,
                ContentType='image/png',
                Metadata={
                    'device-id': device_id,
                    'expiration': expiration.isoformat()
                }
            )
            
            print(f"✅ Screenshot uploaded: {object_key}")
            return object_key
            
        except ClientError as e:
            print(f"❌ Failed to upload screenshot: {e}")
            return None
    
    def get_screenshot_url(self, object_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate presigned URL for screenshot access.
        
        Args:
            object_key: S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
        
        Returns:
            Presigned URL if successful, None otherwise
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.s3_bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expiration
            )
            return url
            
        except ClientError as e:
            print(f"❌ Failed to generate presigned URL: {e}")
            return None
    
    def get_screenshot_data(self, object_key: str) -> Optional[bytes]:
        """
        Download screenshot data from S3.
        
        Args:
            object_key: S3 object key
        
        Returns:
            Screenshot bytes if successful, None otherwise
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.s3_bucket_name,
                Key=object_key
            )
            return response['Body'].read()
            
        except ClientError as e:
            print(f"❌ Failed to download screenshot: {e}")
            return None
    
    # ==================== Bedrock LLM Integration ====================
    
    def invoke_bedrock_model(
        self,
        model_id: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 4096
    ) -> Optional[str]:
        """
        Invoke Bedrock model (Claude).
        
        Args:
            model_id: Bedrock model identifier
            system_prompt: System instruction/context
            user_prompt: User's input command
            temperature: Sampling temperature (default: 0.1)
            max_tokens: Maximum tokens to generate (default: 4096)
        
        Returns:
            Generated text if successful, None otherwise
        """
        try:
            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "system": system_prompt,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload)
            )
            
            response_body = json.loads(response.get('body').read())
            return response_body.get('content')[0].get('text')
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            
            if error_code == 'AccessDeniedException':
                print(f"❌ AWS Bedrock Access Denied: Please request model access for '{model_id}' in the AWS Console.")
            elif error_code == 'ValidationException':
                print(f"❌ AWS Bedrock Validation Error: Check your payload or model ID.")
            else:
                print(f"❌ AWS Bedrock API Error: {error_code} - {error_msg}")
            
            return None
            
        except Exception as e:
            print(f"❌ Unexpected error calling AWS Bedrock: {e}")
            return None
    
    # ==================== Cleanup ====================
    
    def close(self) -> None:
        """
        Close AWS service connections and cleanup.
        """
        # boto3 clients don't need explicit closing
        print("✅ AWS Service Hub closed")
