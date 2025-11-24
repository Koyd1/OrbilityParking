# OrbilityParking Architecture

High-level modules:

- `main.py` — CLI entrypoint for one-off file transcription or realtime microphone mode.
- `app/config.py` — configuration model; reads environment variables and prepares folders.
- `app/logging_config.py` — console + rotating file logging setup.
- `app/db/` — SQLite access layer (`Database`) and `ConversationRepository` with transcripts/decisions tables.
- `app/nlu/` — `IntentClassifier` placeholder (rule-based now, swappable later).
- `app/decision/` — `DecisionEngine` that maps intents to actions/responses from `decision_tree.json`.
- `app/services/` — thin wrappers around existing STT (`WhisperSTT`) and TTS (`PiperTTS`) modules.
- `app/orchestrator.py` — glues STT → NLU → Decision → persistence → TTS.
- `decision_tree.json` — shared source for NLU patterns and decision responses/actions.

Suggested runtime flow:

1. `VoiceOrchestrator` initializes config, logging, DB, STT/TTS, NLU, decision engine.
2. STT produces text (`transcribe_and_handle_file` or realtime callback).
3. NLU predicts intent; decision engine builds action payload.
4. Repository stores transcript + decision in SQLite.
5. If action is `say`, TTS speaks the response; other actions can be handled by downstream integrations.

Environment variables:

- `DATA_DIR`, `DB_PATH`, `DECISION_TREE_PATH`, `LOG_DIR`, `LOG_LEVEL`
- `STT_MODEL_SIZE`, `TTS_VOICE_PATH`

Next extensions:

- Replace rule-based NLU with a trained model behind the same `IntentClassifier` interface.
- Add more actions/side-effects inside the decision engine (e.g., HTTP calls, hardware drivers).
- Expand repository with per-session context/history tables if needed.
