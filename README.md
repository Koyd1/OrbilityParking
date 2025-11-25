# OrbilityParking Voice Assistant

Голосовой ассистент для парковки: потоковое распознавание речи (STT), простая NLU/decision-логика, синтез речи (TTS) и сохранение истории в SQLite.

## Возможности
- Realtime STT на Whisper (`stt_module/stt.py`), микрофон или буфер.
- Правило-ориентированная NLU (`app/nlu/intent_classifier.py`) с шаблонами в `decision_tree.json`.
- Decision engine (`app/decision/engine.py`) строит действия/ответы.
- SQLite-персистентность транскриптов, решений и событий камер (`app/db/*`).
- TTS через Piper (`tts_module/tts.py`) с готовой моделью `tts_module/models/en_US-ryan-low.onnx`.
- CLI (`main.py`) спрашивает номер авто (имитация камеры) и запускает прослушивание микрофона.

## Установка на Windows
```bash
py install 3.10
py -3.10 -m venv .venv
.\.venv\Scripts\activate # MacOS: source3 .venv/bin/activate
pip install -r requirements.txt
```
# macOS
```
brew install python@3.10
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Конфигурация
Через переменные окружения или значения по умолчанию (`app/config.py`):
- `DATA_DIR` - каталог данных (`data/`)
- `DB_PATH` - путь к SQLite (`data/app.sqlite3`)
- `DECISION_TREE_PATH` - путь к дереву решений (`decision_tree.json`)
- `LOG_DIR`, `LOG_LEVEL`
- `STT_MODEL_SIZE` - размер модели Whisper (`small` по умолчанию)
- `TTS_VOICE_PATH` - путь к .onnx модели Piper (по умолчанию пытается `tts_module/models/en_US-ryan-low.onnx`)

## Запуск
```bash
python main.py --duration 60           # слушать 60 секунд
python main.py --duration 60 --resources  # с выводом статистики ресурсов
```


Порядок работы:
1. Запрашивает номер авто и сохраняет как событие камеры.
2. Слушает микрофон, транскрибирует, прогоняет через NLU/decision, сохраняет в БД, озвучивает ответ (если найден голос).

Прекращение - `Ctrl+C`.

## Структура
- `main.py` — CLI, точка входа.
- `app/config.py`, `app/logging_config.py` — конфиг/логирование.
- `app/orchestrator.py` — связывает STT → NLU → Decision → DB → TTS.
- `app/db/` — `Database`, `ConversationRepository` (транскрипты, решения, car_events).
- `app/db` также инициализирует таблицу `HISTORY` (схема выше) и кладёт пару демо-записей.
- `app/nlu/intent_classifier.py` — правила для интентов.
- `app/decision/engine.py` — выбор действий/ответов.
- `app/services/` — тонкие адаптеры над готовыми STT/TTS модулями.
- `decision_tree.json` — intents, паттерны и ответы.
- `tts_module/`, `stt_module/` — готовые реализации TTS/STT (не менять).

## Установка SQLite на Windows
```cmd
winget install SQLite.SQLite
sqlite3 --version 
cd D:\Projects\OrbilityParking #Your path 
sqlite3 data/app.sqlite3  
```
##### Exit: ctrl+C

## Работа с SQLite
- Файл БД по умолчанию: `data/app.sqlite3`. Создаётся автоматически при первом запуске.
- Стартовый набор данных: демо-транскрипты/решения и две записи в `HISTORY` добавляются при инициализации `ConversationRepository`.
- Открыть БД через sqlite3:
  ```bash
  sqlite3 data/app.sqlite3 ".tables"
  sqlite3 data/app.sqlite3 "SELECT ID_HISTORY, BE_N_NUMTIT, BE_D_DATTRA, BE_N_LICPLA, NB_TOTPAI FROM HISTORY;"
  ```
- Добавить запись в HISTORY вручную (пример):
  ```bash
  sqlite3 data/app.sqlite3 <<'SQL'
  INSERT INTO HISTORY (
    N_PAR, BE_N_NUMTIT, BE_D_DATTRA, BE_N_EQU, NB_TOTPAI, N_CNTPRI, T_FAMTIT, BE_N_LICPLA, TXT_COMMENT
  ) VALUES (
    3, 'TICKET-003', '2025-01-03T08:00:00', 2, 1, 'CNT-300', 1, 'C333CC77', 'Manual insert test'
  );
  SQL
  ```

## Запуск программы 
  1. Открыть Windows Powershell 
  2. cd D:\Projects\OrbilityParking #Your path 
  3. Запустить ./run.bat