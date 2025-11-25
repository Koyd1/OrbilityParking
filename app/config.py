from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class AppConfig:
    """Application-wide configuration."""

    data_dir: Path = Path("data")
    db_path: Path = Path("data/app.sqlite3")
    decision_tree_path: Path = Path("decision_tree.json")
    log_dir: Path = Path("logs")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    stt_model_size: str = os.getenv("STT_MODEL_SIZE", "small")
    tts_voice_path: Optional[str] = "tts_module/models/en_US-ryan-low.onnx"

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Construct config reading overrides from environment variables."""
        data_dir = Path(os.getenv("DATA_DIR", cls.data_dir))
        db_path = Path(os.getenv("DB_PATH", data_dir / "app.sqlite3"))
        decision_tree_path = Path(
            os.getenv("DECISION_TREE_PATH", cls.decision_tree_path)
        )
        log_dir = Path(os.getenv("LOG_DIR", cls.log_dir))
        log_level = os.getenv("LOG_LEVEL", cls.log_level)
        stt_model_size = os.getenv("STT_MODEL_SIZE", cls.stt_model_size)
        tts_voice_path = os.getenv("TTS_VOICE_PATH", cls.tts_voice_path)

        return cls(
            data_dir=data_dir,
            db_path=db_path,
            decision_tree_path=decision_tree_path,
            log_dir=log_dir,
            log_level=log_level,
            stt_model_size=stt_model_size,
            tts_voice_path=tts_voice_path,
        )

    def prepare_directories(self) -> None:
        """Create folders for DB/logs if missing."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

