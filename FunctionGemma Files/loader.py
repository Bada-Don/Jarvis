from transformers import AutoProcessor, AutoModelForCausalLM
import os

LOCAL_DIR = "./local_models/functiongemma-270m-it"
MODEL_NAME = "google/functiongemma-270m-it"

# Ensure directory exists
os.makedirs(LOCAL_DIR, exist_ok=True)

processor = AutoProcessor.from_pretrained(
    MODEL_NAME,
    cache_dir=LOCAL_DIR,
    local_files_only=True
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    cache_dir=LOCAL_DIR,
    local_files_only=True,
    device_map="auto"
)
