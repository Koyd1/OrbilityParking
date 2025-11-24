"""Runner script to call PiperTTS in a separate process.

This module is executed by `app/services/tts_service.py` via subprocess
to isolate crashes in the native TTS stack from the main process.
"""
import argparse
import logging
import sys

from tts_module.tts import PiperTTS


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="TTS runner")
    parser.add_argument("text", help="Text to speak")
    parser.add_argument("--voice", required=True, help="Path to ONNX voice model")
    args = parser.parse_args(argv)

    import tempfile
    import os
    import subprocess

    try:
        tts = PiperTTS(voice=args.voice)
        # Synthesize to a temporary WAV file, then play using a platform
        # appropriate player. Preference order aims for system players
        # (stable) and falls back to Python playback if no system player
        # is present.
        fd, tmp = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        try:
            tts.synthesize_to_file(args.text, tmp, voice=args.voice)

            # choose player by platform
            plat = sys.platform
            player_cmds = []
            if plat.startswith("darwin"):
                # macOS: afplay
                player_cmds = [["afplay", tmp]]
            elif plat.startswith("linux"):
                # Linux: try paplay (PulseAudio), aplay (ALSA), ffplay (ffmpeg), play (sox)
                player_cmds = [
                    ["paplay", tmp],
                    ["aplay", tmp],
                    ["ffplay", "-nodisp", "-autoexit", tmp],
                    ["play", tmp],
                ]
            elif plat.startswith("win") or plat.startswith("cygwin"):
                # Windows: use PowerShell SoundPlayer sync call
                ps_cmd = [
                    "powershell",
                    "-Command",
                    f"(New-Object Media.SoundPlayer '{tmp}').PlaySync();",
                ]
                player_cmds = [ps_cmd]
            else:
                player_cmds = []

            played = False
            last_exc = None
            for cmd in player_cmds:
                try:
                    # On some players (ffplay) we don't need output, so allow it
                    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    played = True
                    break
                except FileNotFoundError as fe:
                    last_exc = fe
                    continue
                except subprocess.CalledProcessError as cpe:
                    last_exc = cpe
                    continue

            if not played:
                logging.warning("No suitable system player found or playback failed: %s; falling back to Python playback", last_exc)
                # final fallback: use Python playback which may load native libs
                try:
                    tts.play_file(tmp)
                    played = True
                except Exception:
                    logging.exception("Fallback Python playback failed")

        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
        return 0
    except Exception:
        logging.exception("TTS runner failed")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
