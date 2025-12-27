from transformers import AutoProcessor, AutoModelForCausalLM
import os

MODEL_NAME = "google/functiongemma-270m-it"
LOCAL_DIR = "./local_models/functiongemma-270m-it"

os.makedirs(LOCAL_DIR, exist_ok=True)

print("Downloading processor...")
processor = AutoProcessor.from_pretrained(
    MODEL_NAME,
    cache_dir=LOCAL_DIR
)

print("Downloading model...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    cache_dir=LOCAL_DIR
)

print("Download complete!")
print(f"Model cached inside: {LOCAL_DIR}")
