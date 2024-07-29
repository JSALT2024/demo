from typing import List, Optional


class ContextTracker:
    """
    Tracks context between clips during video translation;
    context to be passed to the LLM during the translation
    of the next clip.
    """
    def __init__(self, max_length: int):
        self.max_length = max_length
        self._previous_clips: List[str] = []
        self._total_length = 0
    
    def add_next_output(self, output: str):
        """Adds next LLM output to the context to enlarge the context"""
        self._previous_clips.append(output)
        self._total_length += len(output)
        self._truncate_length()
    
    def _truncate_length(self):
        """Removes oldest entries until the context size drops below the limit"""
        while self._total_length > self.max_length:
            if len(self._previous_clips) == 0:
                return
            size_delta = len(self._previous_clips[0])
            self._previous_clips.pop(0)
            self._total_length -= size_delta

    def get_current_context(self) -> Optional[str]:
        """Returns the context string for the next clip to be translated"""
        if len(self._previous_clips) == 0:
            return None
        return " ".join(self._previous_clips)
