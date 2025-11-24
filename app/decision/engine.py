from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional


class DecisionEngine:
    """
    Converts NLU output into concrete system actions.
    """

    def __init__(self, decision_tree_path: Optional[Path] = None):
        self.decision_tree_path = decision_tree_path
        self.decision_tree = self._load_tree(decision_tree_path) if decision_tree_path else {}

    def _load_tree(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def decide(self, text: str, nlu_result: dict[str, Any]) -> dict[str, Any]:
        """
        Build an action payload the orchestrator can handle.
        """
        intent = nlu_result.get("intent", "fallback")
        node = self.decision_tree.get("intents", {}).get(intent, {})

        response = node.get("response") or "Я пока не знаю, что ответить на это."
        action = node.get("action", "say")
        extra = node.get("payload", {})

        return {
            "intent": intent,
            "action": action,
            "response": response,
            "payload": extra,
            "confidence": nlu_result.get("confidence", 0.0),
            "slots": nlu_result.get("slots", {}),
            "raw_text": text,
        }

