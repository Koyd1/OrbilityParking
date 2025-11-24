from __future__ import annotations

import logging
from typing import Optional

from app.config import AppConfig
from app.decision.engine import DecisionEngine
from app.db import ConversationRepository, Database
from app.logging_config import init_logging
from app.nlu.intent_classifier import IntentClassifier
from app.services.stt_service import STTService
from app.services.tts_service import TTSService


class VoiceOrchestrator:
    """
    Coordinates STT -> NLU -> Decision -> TTS and persistence flow.
    """

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig.from_env()
        init_logging(self.config)
        self.logger = logging.getLogger(__name__)

        self.db = Database(self.config.db_path)
        self.repo = ConversationRepository(self.db)
        self.repo.seed_sample_data()
        self.repo.seed_history_sample()

        self.nlu = IntentClassifier(rules_path=self.config.decision_tree_path)
        self.decision_engine = DecisionEngine(self.config.decision_tree_path)
        self.stt_service = STTService(model_size=self.config.stt_model_size)
        self.tts_service = (
            TTSService(self.config.tts_voice_path)
            if self.config.tts_voice_path
            else None
        )

    def handle_text(self, text: str, language: str | None = None) -> dict:
        self.logger.info("Transcript received: %s", text)
        transcript_id = self.repo.save_transcript(text=text, language=language)

        nlu_result = self.nlu.predict(text)
        decision = self.decision_engine.decide(text, nlu_result)
        self.repo.save_decision(transcript_id, decision["intent"], decision)

        if decision.get("action") == "say" and self.tts_service:
            self.tts_service.speak(decision.get("response", ""))

        return decision

    def transcribe_and_handle_file(self, audio_path: str) -> dict:
        """
        Convenience flow: transcribe an audio file and run the decision engine.
        """
        text = self.stt_service.transcribe_file(audio_path)
        return self.handle_text(text=text, language=None)

    def start_realtime(self) -> None:
        """
        Start streaming STT; each utterance runs through the NLU/decision layer.
        """

        def on_transcript(text: str, language: str) -> None:
            decision = self.handle_text(text=text, language=language)
            self.logger.debug("Decision result: %s", decision)

        self.logger.info("Starting realtime transcription...")
        self.stt_service.start_realtime(callback=on_transcript)

    def stop_realtime(self) -> None:
        self.stt_service.stop_realtime()
