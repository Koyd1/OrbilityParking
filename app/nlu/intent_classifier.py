from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional


class IntentClassifier:
    """
    Placeholder NLU layer.

    For now it is a simple rule-based matcher that can be replaced with a
    transformer-based classifier later without touching the orchestrator.
    """

    def __init__(self, rules_path: Optional[Path] = None):
        self.rules_path = rules_path
        self.rules = self._load_rules(rules_path) if rules_path else {}

    def _load_rules(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def predict(self, text: str) -> dict[str, Any]:
        """
        Return a lightweight intent payload.
        """
        lowered = text.lower().strip()

        # Rule-based fallback
        for intent, pattern_config in self.rules.get("intents", {}).items():
            patterns = (
                pattern_config
                if isinstance(pattern_config, list)
                else pattern_config.get("patterns", [])
            )
            for pattern in patterns:
                if re.search(pattern, lowered):
                    return {"intent": intent, "confidence": 0.8, "slots": {}}

        # Default intent when nothing matches
        return {"intent": "fallback", "confidence": 0.2, "slots": {}}
