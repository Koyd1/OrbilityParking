import argparse
import logging
from pathlib import Path

from app.config import AppConfig
from app.decision import engine
from app.orchestrator import VoiceOrchestrator
from stt_module.stt import WhisperSTT
from app.services.tts_service import TTSService

from app.decision.tree_engine import DecisionTreeEngine

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
        default=10,
        help="Сколько секунд слушать микрофон",
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
    try:
        stt = WhisperSTT(model_size=config.stt_model_size)
        # orchestrator.set_stt_service(stt)
    except Exception as e:
        log.error("Не удалось инициализировать STT-модуль: %s", e)

    try:
        tts = TTSService(voice_path=config.tts_voice_path)
            # orchestrator.set_tts_service(tts)
    except Exception as e:
        log.error("Не удалось инициализировать TTS-модуль: %s", e)

    # plate = input("Камера: введите номер авто: ").strip()
    # if plate:
    #     orchestrator.repo.save_car_event(plate=plate, source="camera_mock")
    #     log.info("Сохранён номер авто: %s", plate)
    #     history_hits = orchestrator.repo.find_history_by_plate(plate)
    #     if history_hits:
    #         msg = f"Номер {plate} найден в базе, билеты: {[h.get('BE_N_NUMTIT') for h in history_hits]}"
    #         print(msg)
    #         log.info(msg)
    #         if getattr(orchestrator, "tts_service", None):
    #             orchestrator.tts_service.speak(msg)
    #     else:
    #         msg = f"Номер {plate} не зарегистрирован в HISTORY"
    #         print(msg)
    #         log.info(msg)
    #         if getattr(orchestrator, "tts_service", None):
    #             orchestrator.tts_service.speak(msg)

    # try:
    #     stt = WhisperSTT(model_size=config.stt_model_size)

    #     def on_transcript(text: str, lang: str) -> None:
    #         log.info("Распознано [%s]: %s", lang, text)
    #         decision = orchestrator.handle_text(text=text, language=lang)
    #         log.info("Решение: %s", decision)

    #     log.info("Слушаю микрофон %s секунд... Нажмите Ctrl+C для выхода.", args.duration)
    #     stt.transcribe_microphone(
    #         duration=args.duration,
    #         callback=on_transcript,
    #         show_resources=args.resources,
    #     )
    #     log.info("Прослушивание завершено.")
    # except KeyboardInterrupt:
    #     log.info("Interrupted by user, stopping...")
    # finally:
    #     log.info("Завершение работы.")
    engine = DecisionTreeEngine("decision_tree.json")
    engine.actions.stt = stt
    engine.actions.tts = tts

    engine.run()

if __name__ == "__main__":
    main()
