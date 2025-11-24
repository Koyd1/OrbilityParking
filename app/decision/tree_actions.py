class TreeActions:
    def __init__(self):
        self.context = {
            "plate_recognized": False,
            "failures": 0,
            "BS_N_LICPLA": "",
            "BE_N_LICPLA": [],
            "T_MONTANT": 0,
            "NB_TOTPAI": 0,
            "CUR_TIME": 0,
            "DHMP": 0,
            "N": 20
        }

    # ----- ДЕЙСТВИЯ -----

    def detect_car(self):
        print("[ACTION] detect_car")
        return True

    def detect_plate(self):
        print("[ACTION] detect_plate")
        # пример: ставим plate_recognized=True
        self.context["plate_recognized"] = True
        return True

    def say(self, text):
        print("[SAY]", text)
        return True

    def open_barrier(self):
        print("[ACTION] open_barrier")
        return True

    def call_operator(self):
        print("[ACTION] call_operator")
        return True

    # ----- СЧЕТЧИКИ -----

    def increment_failures(self):
        self.context["failures"] += 1
        print(f"[COUNTER] failures = {self.context['failures']}")
        return True

    # ----- УСЛОВИЯ -----

    def evaluate_condition(self, expression: str) -> bool:
        """
        expression — строка вида:
           "plate_recognized"
           "T_MONTANT == 0"
           "BS_N_LICPLA in BE_N_LICPLA"
           "failures >= 2"
        """
        try:
            return bool(eval(expression, {}, self.context))
        except Exception as e:
            print("[ERROR] evaluate_condition:", expression, e)
            return False
