# FunctionGemma Complete Knowledge Base

**Last Updated:** December 27, 2025
**Project:** FunctionGemma-270M Local Function Calling System

## Table of Contents

1. [Project Overview](#project-overview)
2. [Model Information](#model-information)
3. [Setup & Installation](#setup--installation)
4. [Architecture](#architecture)
5. [How It Works](#how-it-works)
6. [Multi-Step Function Calling](#multi-step-function-calling)
7. [Fine-Tuning](#fine-tuning)
8. [Common Issues](#common-issues)
9. [API Reference](#api-reference)

---

## Project Overview

Local function calling system using Google's FunctionGemma-270M model to convert natural language to executable function calls. Supports multi-step tasks, runs entirely locally, includes interactive chat interface and keyboard/mouse automation via pyautogui.

---

## Model Information

**Model ID:** `google/functiongemma-270m-it`
**Size:** 270M parameters (instruction-tuned Gemma 3)
**Links:** [HuggingFace](https://huggingface.co/google/functiongemma-270m-it) | [Docs](https://ai.google.dev/gemma/docs/functiongemma)

**Training Scope:**
- ✅ Single-turn and parallel function calling
- ❌ NOT trained on multi-turn conversations (but can generalize with fine-tuning)

**Output Format:**
```
<start_function_call>call:function_name{arg1:<escape>value1<escape>,arg2:123}<end_function_call>
```
- Strings use `<escape>` tags
- Numbers/booleans don't
- Can generate multiple calls per turn

---

## Setup & Installation

**Requirements:** Python 3.10+, 8GB RAM (16GB recommended), ~2GB storage

**Quick Setup:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install transformers torch huggingface-hub accelerate pyautogui
huggingface-cli login  # Token needs "Access content in gated repos"
python download_functiongemma.py
```

**CRITICAL:** Accept model terms at https://huggingface.co/google/functiongemma-270m-it before downloading.

**Common Issues:**
- 401/403 errors → Create new token with gated repo access
- Model not found → Use `google/functiongemma-270m-it` (with `-it`)
- accelerate missing → `pip install accelerate>=0.20.0`

---

## Architecture

**Key Files:**
- `interactive_demo.py` - Interactive chat (recommended)
- `proper_multistep.py` - Multi-step execution
- `functions.py` - Function implementations
- `schemas.py` - Function schemas
- `dispatcher.py` - Function router
- `loader.py` / `download_functiongemma.py` - Model management

**Important:** Use `AutoProcessor` (NOT `AutoTokenizer`)

---

## How It Works

**Required System Prompt:**
```python
messages = [
    {"role": "developer", "content": "You are a model that can do function calling with the following functions"},
    {"role": "user", "content": "Turn WiFi on"}
]
```

**Tool Schema:**
```python
tools = [{
    "type": "function",
    "function": {
        "name": "toggle_wifi",
        "description": "Turn WiFi on or off",
        "parameters": {
            "type": "object",
            "properties": {
                "state": {"type": "string", "enum": ["on", "off"]}
            },
            "required": ["state"]
        }
    }
}]
```

**Generation:**
```python
inputs = processor.apply_chat_template(messages, tools=tools, add_generation_prompt=True, return_dict=True, return_tensors="pt")
outputs = model.generate(**inputs.to(model.device), pad_token_id=processor.eos_token_id, max_new_tokens=128)
response = processor.decode(outputs[0][len(inputs["input_ids"][0]):], skip_special_tokens=True)
```

**Parsing (Official):**
```python
def extract_tool_calls(text):
    def cast(v):
        try: return int(v)
        except:
            try: return float(v)
            except: return {'true': True, 'false': False}.get(v.lower(), v.strip("'\""))
    return [{
        "name": name,
        "arguments": {k: cast((v1 or v2).strip()) for k, v1, v2 in re.findall(r"(\w+):(?:<escape>(.*?)<escape>|([^,}]*))", args)}
    } for name, args in re.findall(r"<start_function_call>call:(\w+)\{(.*?)\}<end_function_call>", text, re.DOTALL)]
```

---

## Multi-Step Function Calling

**Two Approaches:**
1. **Parallel calls** - Multiple functions in one turn
2. **Conversation turns** - Sequential calls with context

**Parallel Example:**
```
User: "Open notepad and type Hello World"
Output: call:open_app{app_name:<escape>notepad<escape>}
        call:type_text{text:<escape>Hello World<escape>}
```

**Conversation Pattern:**
```python
for turn in range(max_turns):
    inputs = processor.apply_chat_template(messages, tools=tools, ...)
    output = model.generate(...)
    calls = extract_tool_calls(output)
    results = [execute_function(call) for call in calls]
    
    # Add to conversation for next turn
    messages.append({"role": "assistant", "tool_calls": calls})
    messages.append({"role": "tool", "content": results})
```

**Test Results:**
- ✅ "Open notepad and type Hello World" - Perfect execution
- ⚠️ "Open calculator and then open notepad" - Works but occasionally hallucinates extra steps

**Note:** Fine-tuning reduces hallucinations.

---

## Fine-Tuning

**Why:** Achieve 95-99%+ accuracy, reduce hallucinations, adapt to custom functions

**Quick Config:**
```python
from trl import SFTConfig, SFTTrainer

args = SFTConfig(
    output_dir="./fine-tuned-model",
    num_train_epochs=2,
    per_device_train_batch_size=4,
    learning_rate=1e-5,
    completion_only_loss=True,  # Only train on function calls
    bf16=True
)
```

**Data Format:**
```python
def apply_format(sample):
    prompt_and_completion = tokenizer.apply_chat_template(messages, tools=tools, tokenize=False, add_generation_prompt=False)
    prompt = tokenizer.apply_chat_template(messages[:-1], tools=tools, tokenize=False, add_generation_prompt=True)
    completion = prompt_and_completion[len(prompt):]
    return {"prompt": prompt, "completion": completion}
```

**Resources:**
- Full fine-tuning: A100 (40GB), ~8 min/epoch, ~20GB VRAM
- LoRA: RTX 3090/4090 (24GB), 1-3 hours, ~12GB VRAM

**Expected Accuracy:**
- Before: 85-90%
- After (500 examples): 95-98%
- After (1000+ examples): 98-99%+

**Reference:** See `Finetune_FunctionGemma_270M_for_Mobile_Actions_with_Hugging_Face.md`

---

## Common Issues

**Installation:**
- 401/403 errors → Create token with "Access content in gated repos" at https://huggingface.co/settings/tokens
- Model not found → Use `google/functiongemma-270m-it` (with `-it`)
- accelerate missing → `pip install accelerate>=0.20.0`

**Runtime:**
- App won't open → Use app mapping: `{'notepad': 'notepad.exe', 'calculator': 'calc.exe'}`
- Typing doesn't work → Add `time.sleep(0.8)` before `pyautogui.write()`
- Model generates garbage → Check system prompt includes exact phrase
- Leading/trailing spaces → Always `.strip()` parsed values
- Hallucinated steps → Fine-tuning reduces this

---


## API Reference

**Model Loading:**
```python
processor = AutoProcessor.from_pretrained("google/functiongemma-270m-it")  # NOT AutoTokenizer!
model = AutoModelForCausalLM.from_pretrained("google/functiongemma-270m-it", device_map="auto")
```

**Generation:**
```python
inputs = processor.apply_chat_template(messages, tools=tools, add_generation_prompt=True, return_dict=True, return_tensors="pt")
outputs = model.generate(**inputs.to(model.device), pad_token_id=processor.eos_token_id, max_new_tokens=128)
response = processor.decode(outputs[0][len(inputs["input_ids"][0]):], skip_special_tokens=True)
```

**Demo Functions:** `open_app(app_name)`, `type_text(text)`, `press_key(key)`, `search_web(query)`, `set_volume(level)`

**Quick Start:**
```cmd
python -m venv venv && venv\Scripts\activate
pip install transformers torch huggingface-hub accelerate pyautogui
huggingface-cli login
python download_functiongemma.py
python interactive_demo.py
```

**Key Takeaways:**
1. Use `AutoProcessor`, not `AutoTokenizer`
2. System prompt must be exact: "You are a model that can do function calling with the following functions"
3. Model supports parallel calls and conversation turns
4. Always `.strip()` parsed values
5. Fine-tuning recommended for production (95-99%+ accuracy)

**Links:** [Model](https://huggingface.co/google/functiongemma-270m-it) | [Docs](https://ai.google.dev/gemma/docs/functiongemma) | [Dataset](https://huggingface.co/datasets/google/mobile-actions)
