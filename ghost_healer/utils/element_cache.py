import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from ghost_framework.config.framework_config import config

CACHE_DIR = Path(config.memory_dir)

class ElementCache:
    """Manages local storage of element attributes to help AI healing."""
    
    def __init__(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.cache_file = CACHE_DIR / "knowledge_base.json"
        self._memory: Dict[str, Any] = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def get_memory(self, selector: str) -> Optional[Dict[str, Any]]:
        """Retrieve the last known 'healthy' state of an element."""
        return self._memory.get(selector)

    def learn(self, selector: str, attributes: Dict[str, Any]):
        """Save the current healthy state of an element."""
        # Only update if attributes actually changed or it's new
        if self._memory.get(selector) != attributes:
            self._memory[selector] = attributes
            self._save_cache()

    def _save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self._memory, f, indent=2)

# Singleton instance
element_memory = ElementCache()
