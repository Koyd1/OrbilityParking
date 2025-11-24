import time

from app.config import AppConfig
from app.db.database import Database
from app.db.repository import ConversationRepository
class TreeActions:
    def __init__(self, tree: dict, stt=None, tts=None):
        self.session_payload = {
            "interactions": []  # каждый элемент: {"action": ..., "response": ..., "raw_text": ...}
        }
        cfg = AppConfig.from_env()
        db = Database(cfg.db_path)
        self.repo = ConversationRepository(db)
        self.tree = tree
        self.stt = stt
        self.tts = tts
        # Определяем стартовый узел
        self.start_node = "start"
        if self.start_node not in tree:
            raise ValueError("В дереве отсутствует узел 'start'")

        # Контекст переменных
        self.context = {
            "plate_recognized": False,
            "failures": 0,
            "BS_N_LICPLA": "",
            "BE_N_LICPLA": [],
            "T_MONTANT": 0,
            "NB_TOTPAI": 0,
            "CUR_TIME": 0,
            "DHMP": 0,
            "N": 20,
            "last_input": ""
        }

    # ----- ДЕЙСТВИЯ -----

    def detect_car(self):
        print("[ACTION] detect_car")
        return True
    
    def check_plate_recognized(self):
        """
        Проверка, распознан ли номер и есть ли он в истории.
        """
        plate = self.context.get("BS_N_LICPLA", "")
        if not plate:
            self.context["plate_recognized"] = False
            return False

        history = self.repo.find_history_by_plate(plate)
        recognized = len(history) > 0
        self.context["plate_recognized"] = recognized
        print(f"[CHECK] plate_recognized = {recognized}")
        self.context["T_MONTANT"] = history[0].get("T_MONTANT", 0) if recognized else 0
        return recognized

    # def detect_plate(self):
    #     print("[ACTION] detect_plate")
    #     self.context["plate_recognized"] = True
    #     return True

    def say(self, text: str):
        print("[SAY]", text)
        if self.tts:
            try:
                import threading
                t = threading.Thread(target=self.tts.speak, args=(text,))
                t.start()
                t.join() 
            except Exception as e:
                print("[ERROR] TTS failed:", e)
        return True

    def check_payment_status(self):
        print("[ACTION] check_payment_status")
        # Проверяем контекст на наличие неоплаченного долга
        has_no_debt = self.repo.has_no_debt(self.context.get("BS_N_LICPLA", ""))
        self.context["T_MONTANT"] = has_no_debt
        if has_no_debt:
            print("[CHECK] Долга нет")
        else:
            debt = self.repo.find_history_debts_by_plate(self.context.get("BS_N_LICPLA", ""))
            print(f"[CHECK] Есть долг: {debt}")
            return False
        
        return True

    def open_barrier(self):
        print("[ACTION] open_barrier")
        return True

    def call_operator(self):
        print("[ACTION] call_operator")
        return True

    def listen(self, duration=7, timeout=10):
        if self.stt is None:
            raise ValueError("STT-модуль не инициализирован!")

        result_queue = []

        def on_transcript(text: str, lang: str) -> None:
            print(f"[LISTEN] Распознано [{lang}]: {text}")
            result_queue.append(text)

        print(f"[LISTEN] Слушаю микрофон {duration} секунд...")
        self.stt.transcribe_microphone(
            duration=duration,
            callback=on_transcript,
            show_resources=False
        )

        waited = 0
        while not result_queue and waited < timeout:
            time.sleep(0.1)
            waited += 0.1
        if not result_queue:
            print("[WARN] Время ожидания превышено, результат не получен")
            self.context["last_input"] = ""
            return ""

        user_input = result_queue[0]
        self.context["last_input"] = user_input

        print(f"[LISTEN] Итоговый результат: {user_input}")
        user_plate = self.stt.extract_plate_num(user_input)
        print(f"[LISTEN] Распознанный номер: {user_plate}")
        self.context["BS_N_LICPLA"] = user_plate
        return user_plate
   
    
    # ----- СЧЕТЧИКИ -----

    def increment_failures(self):
        self.context["failures"] += 1
        print(f"[COUNTER] failures = {self.context['failures']}")
        return True

    # ----- УСЛОВИЯ -----

    def evaluate_condition(self, expression: str) -> bool:
        # Если expression — имя метода класса
        if hasattr(self, expression.replace("()", "")):
            return getattr(self, expression.replace("()", ""))()
        try:
            return bool(eval(expression, {}, self.context))
        except Exception as e:
            print("[ERROR] eval:", expression, e)
            return False

#логирование взаимодействий с пользователем
    def buffer_interaction(self, action: str, response: str):
        """
        Добавляем одно взаимодействие в буфер, не сохраняя в БД сразу
        """
        self.session_payload["interactions"].append({
            "action": action,
            "response": response,
            "raw_text": self.context.get("last_input", "")
        })
    def commit_session(self, final_intent: str, confidence: float = 1.0, slots: dict | None = None):
        """
        Сохраняем все накопленные взаимодействия за проход в один decision
        """
        slots = slots or {}
        payload = {
            "intent": final_intent,
            "payload": self.session_payload, 
            "slots": slots
        }

        # Сохраняем как один transcript и decision
        transcript_id = self.repo.save_transcript(
            text=" | ".join([i["raw_text"] for i in self.session_payload["interactions"]]),
            language=self.stt.last_detected_language if hasattr(self.stt, "last_detected_language") else None
        )

        self.repo.save_decision(
            transcript_id=transcript_id,
            intent=final_intent,
            payload=payload
        )

        print(f"[LOG] Session committed with intent '{final_intent}'")
        # Очищаем буфер
        self.session_payload = {"interactions": []}
