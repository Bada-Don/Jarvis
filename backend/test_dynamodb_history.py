"""
Test DynamoDB Task History
Verifies that task history is saved and retrieved correctly.
"""

import os
import time
from dotenv import load_dotenv
from aws_service_hub import AWSServiceHub

# Load environment variables
load_dotenv()


def test_device_registration():
    """Test device registration in DynamoDB"""
    print("=" * 60)
    print("Test 1: Device Registration")
    print("=" * 60)
    
    try:
        region = os.getenv('AWS_REGION', 'us-east-1')
        table_name = os.getenv('AWS_DYNAMODB_TABLE_NAME', 'JarvisState')
        bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'jarvis-automation-assets')
        
        aws_service = AWSServiceHub(
            region_name=region,
            dynamodb_table_name=table_name,
            s3_bucket_name=bucket_name
        )
        
        device_id = f"test_device_{int(time.time())}"
        print(f"Registering device: {device_id}")
        
        success = aws_service.register_device(device_id, device_type="desktop", version="1.0.0-test")
        
        if success:
            print("✅ Device registered successfully")
            
            # Verify registration
            device_info = aws_service.get_device_info(device_id)
            if device_info:
                print(f"✅ Device info retrieved: {device_info}")
                return True, device_id
            else:
                print("❌ Failed to retrieve device info")
                return False, None
        else:
            print("❌ Device registration failed")
            return False, None
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False, None


def test_task_history(device_id):
    """Test saving and retrieving task history"""
    print("\n" + "=" * 60)
    print("Test 2: Task History")
    print("=" * 60)
    
    try:
        region = os.getenv('AWS_REGION', 'us-east-1')
        table_name = os.getenv('AWS_DYNAMODB_TABLE_NAME', 'JarvisState')
        bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'jarvis-automation-assets')
        
        aws_service = AWSServiceHub(
            region_name=region,
            dynamodb_table_name=table_name,
            s3_bucket_name=bucket_name
        )
        
        # Save 5 test tasks
        print(f"Saving 5 test tasks for device: {device_id}")
        for i in range(1, 6):
            task_id = f"task_{i}_{int(time.time())}"
            task_data = {
                "command": f"Test command {i}",
                "status": "completed",
                "progress": 100,
                "message": f"Test task {i} completed successfully"
            }
            
            success = aws_service.save_task_history(device_id, task_id, task_data)
            if success:
                print(f"  ✅ Task {i} saved: {task_id}")
            else:
                print(f"  ❌ Task {i} failed to save")
                return False
            
            time.sleep(0.5)  # Small delay to ensure different timestamps
        
        # Retrieve task history
        print(f"\nRetrieving task history for device: {device_id}")
        tasks = aws_service.get_task_history(device_id, limit=10)
        
        if tasks:
            print(f"✅ Retrieved {len(tasks)} tasks")
            for idx, task in enumerate(tasks, 1):
                print(f"  Task {idx}: {task.get('taskId')} - {task.get('status')}")
            
            if len(tasks) == 5:
                print("✅ All 5 tasks retrieved successfully")
                return True
            else:
                print(f"⚠️  Expected 5 tasks, got {len(tasks)}")
                return False
        else:
            print("❌ No tasks retrieved")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_task_cleanup(device_id):
    """Test that old tasks are cleaned up (keeps last 10)"""
    print("\n" + "=" * 60)
    print("Test 3: Task Cleanup (Last 10 Tasks)")
    print("=" * 60)
    
    try:
        region = os.getenv('AWS_REGION', 'us-east-1')
        table_name = os.getenv('AWS_DYNAMODB_TABLE_NAME', 'JarvisState')
        bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'jarvis-automation-assets')
        
        aws_service = AWSServiceHub(
            region_name=region,
            dynamodb_table_name=table_name,
            s3_bucket_name=bucket_name
        )
        
        # Save 15 tasks (should keep only last 10)
        print(f"Saving 15 test tasks for device: {device_id}")
        for i in range(1, 16):
            task_id = f"cleanup_task_{i}_{int(time.time())}"
            task_data = {
                "command": f"Cleanup test command {i}",
                "status": "completed",
                "progress": 100
            }
            
            aws_service.save_task_history(device_id, task_id, task_data)
            time.sleep(0.3)
        
        print("✅ All 15 tasks saved")
        
        # Retrieve task history
        print(f"\nRetrieving task history (should be max 10)...")
        tasks = aws_service.get_task_history(device_id, limit=20)
        
        if tasks:
            print(f"✅ Retrieved {len(tasks)} tasks")
            
            if len(tasks) <= 10:
                print("✅ Cleanup working correctly (max 10 tasks kept)")
                return True
            else:
                print(f"⚠️  Expected max 10 tasks, got {len(tasks)}")
                return False
        else:
            print("❌ No tasks retrieved")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("DYNAMODB TASK HISTORY TESTS")
    print("=" * 60 + "\n")
    
    # Check for AWS credentials
    if not os.getenv('AWS_ACCESS_KEY_ID') and not os.path.exists(os.path.expanduser('~/.aws/credentials')):
        print("⚠️  WARNING: No AWS credentials found!")
        print("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env")
        print("   OR configure AWS CLI: aws configure")
        print()
    
    results = []
    
    # Test 1: Device Registration
    success, device_id = test_device_registration()
    results.append(("Device Registration", success))
    
    if not success or not device_id:
        print("\n❌ Cannot continue tests without device registration")
        return False
    
    # Test 2: Task History
    success = test_task_history(device_id)
    results.append(("Task History", success))
    
    # Test 3: Task Cleanup
    success = test_task_cleanup(device_id)
    results.append(("Task Cleanup", success))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
    print()
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return all_passed


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
