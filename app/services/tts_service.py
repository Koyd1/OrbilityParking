from __future__ import annotations

from typing import Optional
import subprocess
import sys
import logging
from pathlib import Path

from tts_module.tts import PiperTTS


class TTSService:
    """
    Service wrapper around PiperTTS.

    To avoid crashes in the main process caused by native libraries used
    by the TTS backend, `speak` executes a small runner script in a
    separate subprocess. If the subprocess crashes (segfault), the main
    application continues running and logs the failure.
    """

    def __init__(self, voice_path: str):
        self.engine = PiperTTS(voice=voice_path)

    def speak(self, text: str, voice_path: Optional[str] = None) -> None:
        """
        Synthesize and play the given text in a separate process.

        This isolates native crashes (segfaults) to the child process.
        """
        voice = voice_path or self.engine.voice
        if not voice:
            logging.getLogger(__name__).warning("TTS voice not provided; skipping speak")
            return

        # runner script path relative to this file: project_root/tts_module/runner.py
        # Run the runner as a module so imports inside tts_module work
        # reliably. This requires the current working directory to include
        # the project root (which is the typical case when running main.py).
        cmd = [sys.executable, "-m", "tts_module.runner", text, "--voice", str(voice)]

        try:
            # Run the TTS in a separate process; capture output for diagnostics.
            res = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=120)
            if res.returncode != 0:
                logging.getLogger(__name__).error(
                    "TTS subprocess failed (code=%s). stderr=%s stdout=%s",
                    res.returncode,
                    (res.stderr or "").strip(),
                    (res.stdout or "").strip(),
                )
        except Exception as e:
            logging.getLogger(__name__).exception("Failed to run TTS subprocess: %s", e)

