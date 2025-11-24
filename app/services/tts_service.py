from __future__ import annotations

from typing import Optional

from tts_module.tts import PiperTTS


class TTSService:
    """
    Service wrapper around PiperTTS.
    """

    def __init__(self, voice_path: str):
        self.engine = PiperTTS(voice=voice_path)

    def speak(self, text: str, voice_path: Optional[str] = None) -> None:
        """
        Synthesize and play the given text.
        """
        self.engine.synth_and_play(text, voice=voice_path)

