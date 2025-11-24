import argparse
import logging
from pathlib import Path

from app.config import AppConfig
from app.orchestrator import VoiceOrchestrator
from stt_module.stt import WhisperSTT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OrbilityParking voice pipeline")
    parser.add_argument(
        "--mode",
        choices=["listen"],
        default="listen",
        help="listen: realtime microphone mode",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Сколько секунд слушать микрофон (demo режим)",
    )
    parser.add_argument(
        "--resources",
        action="store_true",
        help="Показывать использование ресурсов во время прослушивания",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = AppConfig.from_env()
    log = logging.getLogger("main")

    if not config.tts_voice_path:
        default_voice = Path("tts_module/models/en_US-ryan-low.onnx")
        if default_voice.exists():
            config.tts_voice_path = str(default_voice)
            log.info("Использую голос по умолчанию: %s", default_voice)
        else:
            log.warning("TTS voice не задан (env TTS_VOICE_PATH) и файл по умолчанию не найден.")

    orchestrator = VoiceOrchestrator(config)

    plate = input("Камера: введите номер авто: ").strip()
    if plate:
        orchestrator.repo.save_car_event(plate=plate, source="camera_mock")
        log.info("Сохранён номер авто: %s", plate)

    try:
        stt = WhisperSTT(model_size=config.stt_model_size)

        def on_transcript(text: str, lang: str) -> None:
            log.info("Распознано [%s]: %s", lang, text)
            decision = orchestrator.handle_text(text=text, language=lang)
            log.info("Решение: %s", decision)

        log.info("Слушаю микрофон %s секунд... Нажмите Ctrl+C для выхода.", args.duration)
        stt.transcribe_microphone(
            duration=args.duration,
            callback=on_transcript,
            show_resources=args.resources,
        )
        log.info("Прослушивание завершено.")
    except KeyboardInterrupt:
        log.info("Interrupted by user, stopping...")
    finally:
        log.info("Завершение работы.")


if __name__ == "__main__":
    main()
