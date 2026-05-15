"""
Session Manager for ReAct Loop.
Maintains conversation thread and execution history for each session.
Persists to JSON files for durability across backend restarts.
"""

import os
import json
import time
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any, TypedDict


# Type aliases for Warp's Task-Exchange model
TaskId = str
AIAgentExchangeId = str

class Exchange(TypedDict, total=False):
    exchange_id: AIAgentExchangeId
    input: Dict[str, Any]  # User query or system trigger
    output: Dict[str, Any] # LLM reasoning and requested AIAgentActions
    result: Dict[str, Any] # Outcome of tool execution
    timestamp: float
    parent_task_id: TaskId

class Task(TypedDict, total=False):
    task_id: TaskId
    parent_task_id: Optional[TaskId]
    user_command: str
    exchanges: List[Exchange]
    status: str # e.g., "running", "completed", "failed"
    created_at: float
    updated_at: float

class V4AHunk(TypedDict):
    pre_context: List[str]
    old: List[str]
    new: List[str]
    post_context: List[str]
    change_context: str # e.g., "@@ -1,5 +1,5 @@"

class FileEdit(TypedDict):
    path: str
    hunks: List[V4AHunk]

# Session status constants
SESSION_STATUS_RUNNING = "running"
SESSION_STATUS_COMPLETED = "completed"
SESSION_STATUS_FAILED = "failed"
SESSION_STATUS_ABORTED = "aborted"
SESSION_STATUS_WAITING_PERMISSION = "waiting_permission"
SESSION_STATUS_WAITING_CLARIFICATION = "waiting_clarification"


class Session:
    """
    Represents a single ReAct session with conversation history and execution log.
    """
    
    def __init__(self, session_id: str = None, user_command: str = ""):
        self.session_id = session_id or f"sess_{uuid.uuid4().hex[:12]}"
        self.user_command = user_command
        self.execution_log: List[Dict[str, Any]] = []
        self.current_plan: Optional[Dict] = None
        self.steps_executed: int = 0
        self.status: str = SESSION_STATUS_RUNNING
        self.mode: str = "general"
        self.created_at: float = time.time()
        self.updated_at: float = time.time()
        self.reflection_retries: int = 0
        self.max_reflection_retries: int = int(os.getenv('MAX_REFLECTION_RETRIES', '3'))
        self.route_data: Optional[Dict] = None  # Cached router result

        # Warp-inspired Task-Exchange model attributes
        self.current_task_id: Optional[TaskId] = None
        self.tasks: Dict[TaskId, Task] = {}

    def create_task(self, user_command: str, parent_task_id: Optional[TaskId] = None) -> TaskId:
        """Create a new task and set it as the current task."""
        task_id: TaskId = f"task_{uuid.uuid4().hex[:12]}"
        new_task: Task = {
            "task_id": task_id,
            "parent_task_id": parent_task_id,
            "user_command": user_command,
            "exchanges": [],
            "status": SESSION_STATUS_RUNNING,
            "created_at": time.time(),
            "updated_at": time.time()
        }
        self.tasks[task_id] = new_task
        self.current_task_id = task_id
        self.updated_at = time.time()
        return task_id

    def add_exchange_to_task(self, task_id: TaskId, exchange: Exchange):
        """Add an exchange to a specific task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task with ID {task_id} not found.")
        self.tasks[task_id]["exchanges"].append(exchange)
        self.tasks[task_id]["updated_at"] = time.time()
        self.updated_at = time.time()

    def update_task_status(self, task_id: TaskId, status: str):
        """Update the status of a specific task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task with ID {task_id} not found.")
        self.tasks[task_id]["status"] = status
        self.tasks[task_id]["updated_at"] = time.time()
        self.updated_at = time.time()

    def add_thought(self, content: str):
        """Add a 'thought' entry to the current task's exchanges."""
        if not self.current_task_id:
            raise ValueError("No current task to add thought to.")
        exchange: Exchange = {
            "exchange_id": f"exch_{uuid.uuid4().hex[:12]}",
            "input": {"role": "thought", "content": content},
            "timestamp": time.time(),
            "parent_task_id": self.current_task_id
        }
        self.add_exchange_to_task(self.current_task_id, exchange)

    def add_action(self, step: Dict):
        """Add an 'action' entry to the current task's exchanges."""
        if not self.current_task_id:
            raise ValueError("No current task to add action to.")
        exchange: Exchange = {
            "exchange_id": f"exch_{uuid.uuid4().hex[:12]}",
            "input": {"role": "action", "content": f"Executing step {step.get('order', '?')}: {step.get('desc', step.get('type', 'unknown'))}", "step": step},
            "timestamp": time.time(),
            "parent_task_id": self.current_task_id
        }
        self.add_exchange_to_task(self.current_task_id, exchange)

    def add_observation(self, content: str, success: bool = True):
        """Add an 'observation' entry to the current task's exchanges."""
        if not self.current_task_id:
            raise ValueError("No current task to add observation to.")
        exchange: Exchange = {
            "exchange_id": f"exch_{uuid.uuid4().hex[:12]}",
            "result": {"role": "observation", "content": content, "success": success},
            "timestamp": time.time(),
            "parent_task_id": self.current_task_id
        }
        self.add_exchange_to_task(self.current_task_id, exchange)

    def add_error(self, error_context: str):
        """Add an error observation to the current task's exchanges."""
        if not self.current_task_id:
            raise ValueError("No current task to add error to.")
        exchange: Exchange = {
            "exchange_id": f"exch_{uuid.uuid4().hex[:12]}",
            "result": {"role": "observation", "content": error_context, "success": False},
            "timestamp": time.time(),
            "parent_task_id": self.current_task_id
        }
        self.add_exchange_to_task(self.current_task_id, exchange)
        self.reflection_retries += 1

    def add_user_response(self, response: str):
        """Add a user clarification/permission response to the current task's exchanges."""
        if not self.current_task_id:
            raise ValueError("No current task to add user response to.")
        exchange: Exchange = {
            "exchange_id": f"exch_{uuid.uuid4().hex[:12]}",
            "input": {"role": "user", "content": response},
            "timestamp": time.time(),
            "parent_task_id": self.current_task_id
        }
        self.add_exchange_to_task(self.current_task_id, exchange)
    
    def add_step_result(self, step_result: Dict):
        """Add step result to execution log."""
        self.execution_log.append(step_result)
        self.steps_executed += 1
        self.updated_at = time.time()
    
    def can_retry(self) -> bool:
        """Check if we can still retry after a failure."""
        return self.reflection_retries < self.max_reflection_retries
    
    def is_terminal(self) -> bool:
        """Check if session is in a terminal state."""
        return self.status in [SESSION_STATUS_COMPLETED, SESSION_STATUS_FAILED, SESSION_STATUS_ABORTED]
    
    def get_conversation_for_llm(self, max_observations: int = 10) -> List[Dict[str, Any]]:
        """
        Get conversation history formatted for LLM context from the current task's exchanges.
        Trims old observations to stay within token budget.
        """
        if not self.current_task_id or self.current_task_id not in self.tasks:
            return []

        current_task = self.tasks[self.current_task_id]
        exchanges = current_task["exchanges"]
        
        result = []
        observation_count = 0
        
        for exchange in reversed(exchanges):
            if "result" in exchange: # This is an observation
                entry = exchange["result"]
                observation_count += 1
                if observation_count <= max_observations:
                    result.append({
                        "role": entry["role"],
                        "content": entry["content"],
                        "success": entry.get("success", True)
                    })
                else:
                    # Summarize old observations
                    result.append({
                        "role": "observation_summary",
                        "content": f"[Earlier observation: {'success' if entry.get('success') else 'failure'}]",
                        "success": entry.get("success", True)
                    })
            elif "input" in exchange: # This is a thought, action, or user response
                entry = exchange["input"]
                result.append({
                    "role": entry["role"],
                    "content": entry["content"]
                })
        
        # Reverse back to chronological order
        result.reverse()
        return result
    
    def get_history_for_planner(self, max_observations: int = 10) -> str:
        """Format conversation history as a text string for the planner."""
        entries = self.get_conversation_for_llm(max_observations)
        parts = []
        for entry in entries:
            role = entry.get('role', 'unknown')
            content = entry.get('content', '')
            success = entry.get('success')
            if role == 'thought':
                parts.append(f"[THOUGHT] {content}")
            elif role == 'action':
                parts.append(f"[ACTION] {content}")
            elif role == 'observation':
                mark = "OK" if success else "FAIL"
                parts.append(f"[OBSERVATION {mark}] {content}")
            elif role == 'observation_summary':
                parts.append(f"[OBSERVATION SUMMARY] {content}")
            elif role == 'user':
                parts.append(f"[USER] {content}")
        return "\n".join(parts)
    
    def to_dict(self) -> dict:
        """Serialize session to dictionary."""
        return {
            'session_id': self.session_id,
            'user_command': self.user_command,
            'execution_log': self.execution_log,
            'current_plan': self.current_plan,
            'steps_executed': self.steps_executed,
            'status': self.status,
            'mode': self.mode,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'reflection_retries': self.reflection_retries,
            'max_reflection_retries': self.max_reflection_retries,
            'route_data': self.route_data,
            'current_task_id': self.current_task_id,
            'tasks': self.tasks
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Session':
        """Deserialize session from dictionary."""
        session = cls(
            session_id=data.get('session_id'),
            user_command=data.get('user_command', '')
        )
        session.execution_log = data.get('execution_log', [])
        session.current_plan = data.get('current_plan')
        session.steps_executed = data.get('steps_executed', 0)
        session.status = data.get('status', SESSION_STATUS_RUNNING)
        session.mode = data.get('mode', 'general')
        session.created_at = data.get('created_at', time.time())
        session.updated_at = data.get('updated_at', time.time())
        session.reflection_retries = data.get('reflection_retries', 0)
        session.max_reflection_retries = data.get('max_reflection_retries', 3)
        session.route_data = data.get('route_data')
        session.current_task_id = data.get('current_task_id')
        session.tasks = data.get('tasks', {})
        return session


class SessionManager:
    """
    Manages ReAct sessions with in-memory cache and JSON file persistence.
    """
    
    def __init__(self, sessions_dir: str = None):
        if sessions_dir is None:
            sessions_dir = str(Path(__file__).parent.parent / 'data' / 'sessions')
        self.sessions_dir = sessions_dir
        self._sessions: Dict[str, Session] = {}
        
        # Ensure sessions directory exists
        os.makedirs(self.sessions_dir, exist_ok=True)
        print(f"✓ SessionManager initialized (dir: {self.sessions_dir})")
    
    def create_session(self, user_command: str, mode: str = "general") -> Session:
        """Create a new session and persist it."""
        session = Session(user_command=user_command)
        session.mode = mode
        self._sessions[session.session_id] = session
        self._save_to_file(session)
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID, loading from file if not in memory."""
        if session_id in self._sessions:
            return self._sessions[session_id]
        
        # Try loading from file
        session = self._load_from_file(session_id)
        if session:
            self._sessions[session_id] = session
        return session
    
    def update_session(self, session: Session):
        """Update a session in memory and persist to file."""
        session.updated_at = time.time()
        self._sessions[session.session_id] = session
        self._save_to_file(session)
    
    def delete_session(self, session_id: str):
        """Remove a session from memory and delete its file."""
        if session_id in self._sessions:
            del self._sessions[session_id]
        
        filepath = os.path.join(self.sessions_dir, f"{session_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
    
    def list_sessions(self, status: str = None) -> List[Session]:
        """List all sessions, optionally filtered by status."""
        sessions = list(self._sessions.values())
        if status:
            sessions = [s for s in sessions if s.status == status]
        return sessions
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Remove sessions older than max_age_hours."""
        cutoff = time.time() - (max_age_hours * 3600)
        to_remove = []
        for sid, session in self._sessions.items():
            if session.updated_at < cutoff and session.is_terminal():
                to_remove.append(sid)
        
        for sid in to_remove:
            self.delete_session(sid)
        
        if to_remove:
            print(f"✓ Cleaned up {len(to_remove)} old sessions")
    
    def _save_to_file(self, session: Session):
        """Save session to JSON file."""
        try:
            filepath = os.path.join(self.sessions_dir, f"{session.session_id}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Error saving session {session.session_id}: {e}")
    
    def _load_from_file(self, session_id: str) -> Optional[Session]:
        """Load session from JSON file."""
        try:
            filepath = os.path.join(self.sessions_dir, f"{session_id}.json")
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return Session.from_dict(data)
        except Exception as e:
            print(f"⚠️ Error loading session {session_id}: {e}")
        return None
