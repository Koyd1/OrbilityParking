# OrbilityParking Voice Assistant

Голосовой ассистент для парковки: потоковое распознавание речи (STT), простая NLU/decision-логика, синтез речи (TTS) и сохранение истории в SQLite.

## Возможности
- Realtime STT на Whisper (`stt_module/stt.py`), микрофон или буфер.
- Правило-ориентированная NLU (`app/nlu/intent_classifier.py`) с шаблонами в `decision_tree.json`.
- Decision engine (`app/decision/engine.py`) строит действия/ответы.
- SQLite-персистентность транскриптов, решений и событий камер (`app/db/*`).
- TTS через Piper (`tts_module/tts.py`) с готовой моделью `tts_module/models/en_US-ryan-low.onnx`.
- CLI (`main.py`) спрашивает номер авто (имитация камеры) и запускает прослушивание микрофона.

## Установка
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Конфигурация
Через переменные окружения или значения по умолчанию (`app/config.py`):
- `DATA_DIR` — каталог данных (`data/`)
- `DB_PATH` — путь к SQLite (`data/app.sqlite3`)
- `DECISION_TREE_PATH` — путь к дереву решений (`decision_tree.json`)
- `LOG_DIR`, `LOG_LEVEL`
- `STT_MODEL_SIZE` — размер модели Whisper (`small` по умолчанию)
- `TTS_VOICE_PATH` — путь к .onnx модели Piper (по умолчанию пытается `tts_module/models/en_US-ryan-low.onnx`)

## Запуск
```bash
python main.py --duration 60           # слушать 60 секунд
python main.py --duration 60 --resources  # с выводом статистики ресурсов
```
Порядок работы:
1. Запрашивает номер авто и сохраняет как событие камеры.
2. Слушает микрофон, транскрибирует, прогоняет через NLU/decision, сохраняет в БД, озвучивает ответ (если найден голос).

Прекращение — `Ctrl+C`.

## Структура
- `main.py` — CLI, точка входа.
- `app/config.py`, `app/logging_config.py` — конфиг/логирование.
- `app/orchestrator.py` — связывает STT → NLU → Decision → DB → TTS.
- `app/db/` — `Database`, `ConversationRepository` (транскрипты, решения, car_events).
- `app/nlu/intent_classifier.py` — правила для интентов.
- `app/decision/engine.py` — выбор действий/ответов.
- `app/services/` — тонкие адаптеры над готовыми STT/TTS модулями.
- `decision_tree.json` — intents, паттерны и ответы.
- `tts_module/`, `stt_module/` — готовые реализации TTS/STT (не менять).

## Кастомизация
- Добавить паттерны/ответы: редактировать `decision_tree.json`.
- Заменить NLU на ML-модель: реализовать тот же интерфейс в `IntentClassifier`.
- Подключить другие действия: расширить `DecisionEngine` (action != "say") и добавить обработчики.
- Историю расширить — добавить таблицы/методы в `app/db`.

## Советы по отладке
- Включите `--resources` для мониторинга памяти/CPU STT.
- Проверяйте наличие `TTS_VOICE_PATH`, иначе голос не проигрывается.
- Логи: `logs/app.log`.
