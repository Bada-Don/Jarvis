import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Add necessary paths
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "local_client"))
sys.path.insert(0, str(root_dir / "backend"))

# Load env variables for BROWSER_PATH and BROWSER_USER_DATA
load_dotenv()

# We need a mock VisionService just to instantiate PlanExecutor
class MockVisionService:
    pass

from plan_executor import PlanExecutor

# Create executor instance
executor = PlanExecutor(vision_service=MockVisionService())

# Define a test plan with a web_automation step
test_plan = {
    "mode": "general",
    "sequence": [
        {
            "order": 1,
            "type": "web_automation",
            "prompt": "Go to Google and search for the current Python latest release version, then print the result.",
            "desc": "Test web automation execution"
        }
    ]
}

print("Running test plan execution...")
result = executor.execute_plan(test_plan, verify=False)
print("Execution Result:", result)
