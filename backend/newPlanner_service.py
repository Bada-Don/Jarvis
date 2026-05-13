"""
Planner Service for Multi-Agent Pipeline

Skill-Based Architecture (Anthropic-style):
1. SkillManager reads skills/ directory — manifest.json + .md skill files
2. Keyword-based routing selects relevant skills (no LLM call needed)
3. System prompt = base prefix + matched skill content + output requirements
4. The Planner LLM generates the execution plan using the assembled prompt
"""

import os
import re
import json
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from llm_provider import GeminiProvider, OpenAIProvider, LocalProvider

load_dotenv()

_ROOT_DIR = Path(__file__).parent.parent
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))


# ==========================================
# 🧩 SKILL MANAGER
# ==========================================

class SkillManager:
    """Loads and manages skill definitions from the skills/ directory."""

    def __init__(self, skills_dir: str = None):
        if skills_dir is None:
            skills_dir = str(Path(__file__).parent / "skills")
        self.skills_dir = Path(skills_dir)
        self.manifest = []
        self._skill_cache = {}  # filename -> content (after frontmatter removal)
        self._load_manifest()

    def _load_manifest(self):
        manifest_path = self.skills_dir / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Skills manifest not found: {manifest_path}")
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.manifest = data.get("skills", [])
        print(f"SkillManager: Loaded {len(self.manifest)} skills from manifest")

    def _strip_frontmatter(self, content: str) -> str:
        """Remove YAML frontmatter (--- ... ---) from a skill .md file."""
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                return content[end + 3:].lstrip("\n")
        return content

    def _read_skill_file(self, filename: str) -> str:
        """Read a skill .md file, strip frontmatter, and cache the result."""
        if filename in self._skill_cache:
            return self._skill_cache[filename]

        filepath = self.skills_dir / filename
        if not filepath.exists():
            print(f"⚠️ Skill file not found: {filepath}")
            return ""

        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()

        content = self._strip_frontmatter(raw)
        self._skill_cache[filename] = content
        return content

    def route_command(self, user_command: str) -> dict:
        """Flexible routing: matches user command against skill triggers.
        Returns {"mode": str, "modules": [str]} for backward compatibility.
        """
        command_lower = user_command.lower()
        matched_skills = []

        # Check flexisign first — it overrides everything
        for skill in self.manifest:
            if skill.get("overrides_prompt"):
                for trigger in skill.get("triggers", []):
                    if trigger in command_lower:
                        return {"mode": "flexisign", "modules": ["flexisign"]}

        # Match other skills by triggers
        for skill in self.manifest:
            sid = skill["id"]
            if sid in ("out_req", "react") or skill.get("overrides_prompt"):
                continue  # Skip always-include and react_only skills here
            
            is_matched = False
            for trigger in skill.get("triggers", []):
                # Flexible matching: either substring or all words present
                if trigger in command_lower:
                    is_matched = True
                else:
                    trigger_words = trigger.split()
                    if len(trigger_words) > 1 and all(word in command_lower for word in trigger_words):
                        is_matched = True
                
                if is_matched:
                    matched_skills.append(sid)
                    break

        # Fallback: if no skills matched, include ui_os and shell as baseline
        if not matched_skills:
            matched_skills = ["ui_os", "shell"]
        else:
            # Ensure ui_os is present if we matched something but it's not there, 
            # only if we want it as a safety baseline. 
            # But the user wants "ONLY relevant", so we trust the triggers.
            pass

        return {"mode": "general", "modules": matched_skills}

    def build_prompt(self, route_data: dict, react_mode: bool = False) -> str:
        """Assemble the system prompt from skill files.

        Architecture:
        [_prefix.md base] (identity, system info, capabilities, available_skills listing)
        [matched skill content] (keyword-selected, varies per request)
        [out_req.md] (always appended — output format requirements)
        [react.md] (only when react_mode=True)
        """
        mode = route_data.get("mode", "general")
        modules = route_data.get("modules", [])

        # FlexiSIGN overrides the entire prompt
        if mode == "flexisign" or "flexisign" in modules:
            return self._read_skill_file("flexisign.md")

        # Build base prefix
        prompt = self._read_skill_file("_prefix.md")

        # Append matched skill content
        for skill in self.manifest:
            sid = skill["id"]
            if sid in ("out_req", "react", "flexisign"):
                continue  # Handled separately
            if sid in modules:
                skill_content = self._read_skill_file(skill["file"])
                if skill_content:
                    prompt += "\n\n" + skill_content

        # Always append output requirements
        out_req = self._read_skill_file("out_req.md")
        if out_req:
            prompt += "\n\n" + out_req

        # Append ReAct instructions if in react mode
        if react_mode:
            react_content = self._read_skill_file("react.md")
            if react_content:
                prompt += "\n\n" + react_content

        return prompt

    def inject_variables(self, text: str, config: dict) -> str:
        """Replace {VARIABLE_NAME} placeholders with actual values using regex.
        This is safe with JSON content in .md files — only replaces known config keys.
        Uses lambda replacement to avoid re.sub interpreting backslashes in values
        (e.g. C:\\Users\\...) as regex backreferences.
        """
        for key, value in config.items():
            text = re.sub(r'\{' + re.escape(key) + r'\}', lambda m: str(value), text)
        return text

    def clear_cache(self):
        """Clear the skill file cache (useful if skill files are updated at runtime)."""
        self._skill_cache.clear()


# ==========================================
# 🚀 PLANNER SERVICE CLASS
# ==========================================

class PlannerService:
    def __init__(self, api_key: str = None, config: dict = None):
        if config is None:
            config = {
                'WINDOWS_USERNAME': os.getenv('WINDOWS_USERNAME', 'user'),
                'DESKTOP_PATH': os.getenv('DESKTOP_PATH', r'C:\Users\user\Desktop'),
                'DOCUMENTS_PATH': os.getenv('DOCUMENTS_PATH', r'C:\Users\user\Documents'),
                'DOWNLOADS_PATH': os.getenv('DOWNLOADS_PATH', r'C:\Users\user\Downloads'),
                'STICKERS_PATH': os.getenv('STICKERS_PATH', r'D:\Stickers\New Briefcase'),
                'LLM_PROVIDER': os.getenv('LLM_PROVIDER', 'gemini'),
                'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
                'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
                'LOCAL_MODEL_NAME': os.getenv('LOCAL_MODEL_NAME', 'google/gemma-4-e2b'),
                'LOCAL_BASE_URL': os.getenv('LOCAL_BASE_URL', 'http://127.0.0.1:1234/v1')
            }

        self.llm_provider = config.get('LLM_PROVIDER', 'gemini')
        self.gemini_key = config.get('GEMINI_API_KEY', '')
        self.openai_key = config.get('OPENAI_API_KEY', '')
        self.config = config

        # Initialize SkillManager (replaces all MODULE_* constants)
        self.skill_manager = SkillManager()

        self.init_provider(api_key)

    def init_provider(self, str_api_key_override=None):
        if self.llm_provider == 'openai':
            api_key = str_api_key_override or self.openai_key or os.getenv('OPENAI_API_KEY')
            if not api_key: raise ValueError("OpenAI API key not configured.")
            self.provider = OpenAIProvider(api_key=api_key)
        elif self.llm_provider == 'local':
            model_name = self.config.get('LOCAL_MODEL_NAME', os.getenv('LOCAL_MODEL_NAME', 'gemma:2b'))
            base_url = self.config.get('LOCAL_BASE_URL', os.getenv('LOCAL_BASE_URL', 'http://localhost:11434/v1'))
            self.provider = LocalProvider(model_name=model_name, base_url=base_url)
        else:
            api_key = str_api_key_override or self.gemini_key or os.getenv('GEMINI_API_KEY')
            if not api_key: raise ValueError("Gemini API key not configured.")
            self.provider = GeminiProvider(api_key=api_key)

        self.provider_name = self.llm_provider
        self.llm = self.provider

        print(f"Initialized Planner with {self.llm_provider} provider")

    def route_command(self, user_command: str) -> dict:
        """Keyword-based routing via SkillManager (no LLM call)."""
        return self.skill_manager.route_command(user_command)

    def build_prompt(self, route_data: dict, react_mode: bool = False) -> str:
        """Build system prompt from skill files, then inject runtime variables."""
        prompt = self.skill_manager.build_prompt(route_data, react_mode=react_mode)
        # Inject actual path values into the prompt (privacy: only known config keys)
        prompt = self.skill_manager.inject_variables(prompt, self.config)
        return prompt

    def detect_mode(self, user_command: str) -> str:
        """Kept for backward compatibility."""
        flexisign_keywords = ["plate", "number plate", "numberplate", "bike", "car", "iron", "glass", "flexisign", "flexi sign", "flexi-sign", "nameplate", "name plate", "sticker", "stickers"]
        command_lower = user_command.lower()
        for keyword in flexisign_keywords:
            if keyword in command_lower: return "flexisign"
        return "general"

    def generate_plan(self, user_command: str, mode: str = None) -> dict:
        if not user_command or not user_command.strip():
            raise ValueError("User command cannot be empty")

        # 1. Route the command (keyword-based skill selection)
        route_data = self.route_command(user_command)

        # Manual override fallback
        if mode is None:
            mode = self.detect_mode(user_command)
        if mode:
            route_data["mode"] = mode

        # 2. Build the system prompt from skill files
        system_prompt = self.build_prompt(route_data)

        try:
            # 3. Generate Execution Plan
            response_text = self.provider.generate_content(
                system_prompt=system_prompt,
                user_prompt=user_command
            )
            print(f"DEBUG: RAW AI RESPONSE:\n{response_text}\n--- END RAW ---")

            # Privacy Audit
            self._log_privacy_audit(system_prompt, response_text)

            response_text = response_text.strip()

            if response_text.startswith('```'):
                lines = response_text.split('\n')[1:]
                if lines and lines[-1].strip() == '```': lines = lines[:-1]
                response_text = '\n'.join(lines)

            try:
                from local_client.json_utils import safe_json_loads
                plan = safe_json_loads(response_text)
            except ImportError:
                plan = json.loads(response_text)

            # 4. Resolve placeholders in the generated plan LOCALLY (for privacy)
            plan = self._resolve_placeholders(plan)

            self._validate_plan(plan)

            if 'sequence' in plan:
                for step in plan['sequence']:
                    if step.get('type') == 'write_file' and 'content' in step:
                        content = step['content']
                        if content.startswith('```'):
                            lines = content.split('\n')[1:]
                            if lines and lines[-1].strip() == '```': lines = lines[:-1]
                            content = '\n'.join(lines)
                        step['content'] = content

            plan['mode'] = route_data["mode"]
            return plan

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from Planner Model: {e}")
        except Exception as e:
            raise Exception(f"Failed to generate plan: {e}")

    def _resolve_placeholders(self, data):
        """Recursively resolve {VARIABLE} placeholders in strings within a dict or list."""
        if isinstance(data, str):
            try:
                return data.format(**self.config)
            except (KeyError, ValueError, IndexError):
                return data
        elif isinstance(data, list):
            return [self._resolve_placeholders(item) for item in data]
        elif isinstance(data, dict):
            return {key: self._resolve_placeholders(value) for key, value in data.items()}
        return data

    def _log_privacy_audit(self, system_prompt: str, raw_response: str):
        """Logs the system prompt and raw LLM response for privacy auditing."""
        try:
            log_base = Path(__file__).parent.parent / "local_client" / "debug_logs"
            log_dir = log_base / "privacy_audit"
            log_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_dir / f"audit_{timestamp}.txt"

            with open(log_file, "w", encoding="utf-8") as f:
                f.write("="*80 + "\n")
                f.write(f"PRIVACY AUDIT LOG - {datetime.now().isoformat()}\n")
                f.write("="*80 + "\n\n")
                f.write("--- [SYSTEM PROMPT (with resolved variables)] ---\n\n")
                f.write(system_prompt)
                f.write("\n\n" + "-"*40 + "\n\n")
                f.write("--- [RAW RESPONSE FROM LLM] ---\n\n")
                f.write(raw_response)
                f.write("\n\n" + "="*80 + "\n")

            print(f"Privacy audit log saved to: {log_file}")
        except Exception as e:
            print(f"Failed to save privacy audit log: {e}")

    def _validate_plan(self, plan: dict) -> None:
        """Validation logic kept identical"""
        if not isinstance(plan, dict): raise ValueError("Plan must be a dictionary")
        if 'sequence' not in plan: raise ValueError("Plan must contain a 'sequence' array")
        if not isinstance(plan['sequence'], list): raise ValueError("'sequence' must be an array")

        valid_types = {
            'keyboard', 'visual_click', 'click_text_fast',
            'create_text', 'set_dimensions', 'set_font', 'apply_style', 'move_object', 'ensure_designcentral',
            'open_file', 'open_folder', 'save_file', 'shell_command',
            'write_file', 'read_file', 'path_exists', 'directory_exists', 'append_file', 'create_directory',
            'replace_in_file', 'modify_lines', 'insert_at_line', 'delete_lines',
            'ai_edit_text', 'ai_edit_excel', 'ai_edit_word', 'send_email', 'web_automation'
        }

        for i, step in enumerate(plan['sequence']):
            if not isinstance(step, dict): raise ValueError(f"Step {i+1} must be a dictionary")
            if 'order' not in step: raise ValueError(f"Step {i+1} missing 'order' field")
            if 'type' not in step: raise ValueError(f"Step {i+1} missing 'type' field")

            step_type = step['type']
            if step_type not in valid_types:
                raise ValueError(f"Step {i+1} has invalid type '{step_type}'.")
                # Validate required fields for each step type
            if step_type == 'keyboard' and 'value' not in step:
                raise ValueError(f"Keyboard step {i+1} missing 'value' field")

            if step_type == 'web_automation' and 'prompt' not in step:
                raise ValueError(f"Web automation step {i+1} missing 'prompt' field")

            if step_type == 'click_text_fast':
                if 'window_title' not in step:
                    raise ValueError(f"click_text_fast step {i+1} missing 'window_title' field")
                if 'text' not in step:
                    raise ValueError(f"click_text_fast step {i+1} missing 'text' field")

            if step_type == 'visual_click' and 'target_name' not in step:
                raise ValueError(f"Visual click step {i+1} missing 'target_name' field")

            if step_type == 'create_text' and 'text' not in step:
                raise ValueError(f"Create text step {i+1} missing 'text' field")

            if step_type == 'set_dimensions':
                if 'width' not in step:
                    raise ValueError(f"Set dimensions step {i+1} missing 'width' field")
                if 'height' not in step:
                    raise ValueError(f"Set dimensions step {i+1} missing 'height' field")

            if step_type == 'set_font' and 'font_name' not in step:
                raise ValueError(f"Set font step {i+1} missing 'font_name' field")

            if step_type == 'move_object':
                if 'direction' not in step:
                    raise ValueError(f"Move object step {i+1} missing 'direction' field")
                if 'distance' not in step:
                    raise ValueError(f"Move object step {i+1} missing 'distance' field")
                if step['direction'] not in ('up', 'down', 'left', 'right'):
                    raise ValueError(
                        f"Move object step {i+1} has invalid direction '{step['direction']}'. "
                        "Must be 'up', 'down', 'left', or 'right'"
                    )

            # Validate file/folder operation step types
            if step_type in ('save_file', 'open_file', 'open_folder') and 'path' not in step:
                raise ValueError(f"{step_type} step {i+1} missing 'path' field")

            # Validate shell_command step type
            if step_type == 'shell_command' and 'command' not in step:
                raise ValueError(f"shell_command step {i+1} missing 'command' field")

            # Validate AI editing step types
            if step_type in ('ai_edit_text', 'ai_edit_excel', 'ai_edit_word'):
                if 'path' not in step:
                    raise ValueError(f"{step_type} step {i+1} missing 'path' field")
                if 'prompt' not in step:
                    raise ValueError(f"{step_type} step {i+1} missing 'prompt' field")

            # Validate Plane 2 workspace control step types
            if step_type == 'write_file':
                if 'path' not in step:
                    raise ValueError(f"write_file step {i+1} missing 'path' field")
                if 'content' not in step:
                    raise ValueError(f"write_file step {i+1} missing 'content' field")

            if step_type in ('read_file', 'path_exists', 'directory_exists', 'create_directory') and 'path' not in step:
                raise ValueError(f"{step_type} step {i+1} missing 'path' field")

            if step_type == 'append_file':
                if 'path' not in step:
                    raise ValueError(f"append_file step {i+1} missing 'path' field")
                if 'content' not in step:
                    raise ValueError(f"append_file step {i+1} missing 'content' field")

            # Validate intelligent file editing operations
            if step_type == 'replace_in_file':
                if 'path' not in step:
                    raise ValueError(f"replace_in_file step {i+1} missing 'path' field")
                if 'old_text' not in step:
                    raise ValueError(f"replace_in_file step {i+1} missing 'old_text' field")
                if 'new_text' not in step:
                    raise ValueError(f"replace_in_file step {i+1} missing 'new_text' field")

            if step_type == 'modify_lines':
                if 'path' not in step:
                    raise ValueError(f"modify_lines step {i+1} missing 'path' field")
                if 'line_number' not in step:
                    raise ValueError(f"modify_lines step {i+1} missing 'line_number' field")
                if 'new_content' not in step:
                    raise ValueError(f"modify_lines step {i+1} missing 'new_content' field")

            if step_type == 'insert_at_line':
                if 'path' not in step:
                    raise ValueError(f"insert_at_line step {i+1} missing 'path' field")
                if 'line_number' not in step:
                    raise ValueError(f"insert_at_line step {i+1} missing 'line_number' field")
                if 'content' not in step:
                    raise ValueError(f"insert_at_line step {i+1} missing 'content' field")

            if step_type == 'delete_lines':
                if 'path' not in step:
                    raise ValueError(f"delete_lines step {i+1} missing 'path' field")
                if 'start_line' not in step:
                    raise ValueError(f"delete_lines step {i+1} missing 'start_line' field")

            # Validate send_email step type
            if step_type == 'send_email':
                if 'recipient_email' not in step:
                    raise ValueError(f"send_email step {i+1} missing 'recipient_email' field")
                if 'subject' not in step:
                    raise ValueError(f"send_email step {i+1} missing 'subject' field")
                if 'body' not in step:
                    raise ValueError(f"send_email step {i+1} missing 'body' field")

    def generate_next_steps(self, session) -> dict:
        """
        ReAct Loop: Generate the next batch of steps based on session history.
        Uses the full system prompt plus ReAct instructions for iterative reasoning.
        """
        route_data = session.route_data
        if not route_data:
            route_data = self.route_command(session.user_command)
            session.route_data = route_data

        # Build the full system prompt with ReAct mode enabled
        system_prompt = self.build_prompt(route_data, react_mode=True)

        # Format conversation history
        history_context = session.get_history_for_planner()

        user_prompt = f"""USER COMMAND: {session.user_command}
CURRENT MODE: {session.mode}

EXECUTION HISTORY:
{history_context}

Generate the next 1-3 steps. If the task is complete, set is_complete to true with an empty sequence."""

        try:
            response_text = self.llm.generate_content(system_prompt=system_prompt, user_prompt=user_prompt)
            plan = self._parse_json_response(response_text)
            plan = self._resolve_placeholders(plan)
            plan = self._validate_react_plan(plan)
            plan['mode'] = route_data.get("mode", "general")
            return plan

        except Exception as e:
            print(f"✗ ReAct planning failed: {e}")
            raise

    def _validate_react_plan(self, plan: dict) -> dict:
        """Ensure ReAct plan follows the required schema."""
        if not isinstance(plan, dict):
            raise ValueError("ReAct plan must be a dictionary")
        if 'sequence' not in plan:
            plan['sequence'] = []
        if plan['sequence'] is None:
            plan['sequence'] = []
        if not isinstance(plan['sequence'], list):
            raise ValueError("ReAct plan 'sequence' must be a list")
        if 'is_complete' not in plan:
            plan['is_complete'] = False
        if 'thought' not in plan:
            plan['thought'] = "Continuing execution..."

        # Ensure steps have correct format
        for i, step in enumerate(plan['sequence']):
            if not isinstance(step, dict):
                raise ValueError(f"ReAct step {i+1} must be a dictionary")
            parameters = step.pop('parameters', None)
            if isinstance(parameters, dict):
                for key, value in parameters.items():
                    step.setdefault(key, value)
            if 'order' not in step:
                step['order'] = i + 1
            if 'desc' not in step:
                step['desc'] = f"Executing {step.get('type', 'step')}"

        return plan

    def _parse_json_response(self, response_text: str) -> dict:
        """Parse JSON from LLM response, handling markdown fences."""
        response_text = response_text.strip()
        if response_text.startswith('```'):
            lines = response_text.split('\n')[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            response_text = '\n'.join(lines)

        try:
            import sys
            from pathlib import Path
            local_client_path = Path(__file__).parent.parent / "local_client"
            if str(local_client_path) not in sys.path:
                sys.path.insert(0, str(local_client_path))
            from json_utils import safe_json_loads
            return safe_json_loads(response_text)
        except ImportError:
            return json.loads(response_text)