"""
Summarization Buffer for ReAct Loop.
Summarizes long tool outputs before sending to the LLM to save tokens.
Uses Gemini Flash for intelligent summarization when outputs are very long.
"""

import os
from typing import Optional


# Token budget constants
MAX_OUTPUT_CHARS = 2000       # Max chars for raw output before summarization
MAX_OBSERVATION_CHARS = 1000  # Max chars for each observation in conversation
MAX_CONVERSATION_ENTRIES = 20 # Max conversation entries to send to LLM


class SummarizationBuffer:
    """
    Manages context window budget by summarizing long outputs
    and trimming old conversation entries.
    """
    
    def __init__(self, max_output_chars: int = MAX_OUTPUT_CHARS,
                 max_observation_chars: int = MAX_OBSERVATION_CHARS,
                 max_entries: int = MAX_CONVERSATION_ENTRIES):
        self.max_output_chars = max_output_chars
        self.max_observation_chars = max_observation_chars
        self.max_entries = max_entries
        
        # Lazy-initialized Gemini client for intelligent summarization
        self._gemini_client = None
        self._gemini_available = False
        self._init_gemini()
    
    def _init_gemini(self):
        """Initialize Gemini client for summarization (optional)."""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                from google import genai
                self._gemini_client = genai.Client(api_key=api_key)
                self._gemini_available = True
        except ImportError:
            pass
    
    def process_output(self, raw_output: str, is_error: bool = False) -> str:
        """
        Process a raw tool output for inclusion in conversation.
        
        Args:
            raw_output: Raw stdout/stderr from tool execution
            is_error: If True, this is error output (preserve more detail)
            
        Returns:
            str: Processed output (possibly summarized)
        """
        if not raw_output:
            return ""
        
        # For errors, keep more detail (up to 2x budget)
        budget = self.max_output_chars * 2 if is_error else self.max_output_chars
        
        if len(raw_output) <= budget:
            return raw_output
        
        # Try intelligent summarization with Gemini Flash
        if self._gemini_available and len(raw_output) > 5000:
            try:
                return self._summarize_with_llm(raw_output, is_error)
            except Exception:
                pass  # Fall through to truncation
        
        # Fallback: simple truncation with head/tail preservation
        return self._truncate_output(raw_output, budget)
    
    def format_conversation(self, history: list) -> list:
        """
        Format conversation history for LLM input.
        Trims old entries and summarizes long observations.
        
        Args:
            history: List of conversation entries from Session
            
        Returns:
            list: Trimmed and summarized conversation entries
        """
        if len(history) <= self.max_entries:
            # Just summarize long observations
            return [self._process_entry(entry) for entry in history]
        
        # Keep all non-observation entries, trim old observations
        result = []
        observation_count = 0
        
        for entry in history:
            if entry.get('role') == 'observation':
                observation_count += 1
                if observation_count <= 5:
                    # Keep recent observations in full
                    result.append(self._process_entry(entry))
                else:
                    # Summarize old observations
                    success = entry.get('success', True)
                    result.append({
                        'role': 'observation_summary',
                        'content': f"[Earlier step {'succeeded' if success else 'failed'}]",
                        'success': success
                    })
            else:
                result.append(entry)
        
        return result
    
    def _process_entry(self, entry: dict) -> dict:
        """Process a single conversation entry, truncating long content."""
        content = entry.get('content', '')
        if len(content) > self.max_observation_chars:
            entry = dict(entry)  # Don't mutate original
            entry['content'] = self._truncate_output(content, self.max_observation_chars)
        return entry
    
    def _truncate_output(self, output: str, max_chars: int) -> str:
        """Truncate output preserving head and tail."""
        if len(output) <= max_chars:
            return output
        
        half = max_chars // 2
        omitted = len(output) - max_chars
        return f"{output[:half]}\n... [{omitted} chars omitted] ...\n{output[-half:]}"
    
    def _summarize_with_llm(self, raw_output: str, is_error: bool) -> str:
        """Use Gemini Flash to intelligently summarize long output."""
        prompt_type = "error output" if is_error else "command output"
        prompt = (
            f"Summarize this {prompt_type} in under 500 characters. "
            f"Preserve key information: error codes, file names, and final status. "
            f"Omit repetitive lines.\n\n{raw_output[:10000]}"
        )
        
        response = self._gemini_client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        return response.text.strip()