from __future__ import annotations

from typing import Callable, Optional

from stt_module.stt import WhisperSTT


class STTService:
    """
    Service wrapper around WhisperSTT to keep the orchestrator decoupled.
    """

    def __init__(self, model_size: str = "small"):
        self.engine = WhisperSTT(model_size=model_size)

    def transcribe_file(self, audio_path: str) -> str:
        return self.engine.transcribe_file(audio_path)

    def start_realtime(self, callback: Optional[Callable[[str, str], None]] = None) -> None:
        self.engine.start_realtime_transcription(callback=callback)

    def stop_realtime(self) -> None:
        self.engine.stop_realtime_transcription()

    def feed_audio(self, chunk) -> None:
        self.engine.add_audio_chunk(chunk)
        
    def extract_plate_num(self, text: str) -> str:
        return self.engine.extract_plate_num(text)
