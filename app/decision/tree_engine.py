# tree_engine.py
import json
from app.decision.tree_actions import TreeActions


class DecisionTreeEngine:
    def __init__(self, json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            self.tree = json.load(f)

        self.actions = TreeActions()

    def run(self, start_node="start"):
        current = start_node

        while True:
            node = self.tree[current]
            print(f"\n=== NODE: {current} ===")

            # 1. Выполнить action
            if "action" in node:
                action = node["action"]
                if action.startswith("say:"):
                    text = action.split("say:", 1)[1].strip()
                    self.actions.say(text)
                elif hasattr(self.actions, action):
                    getattr(self.actions, action)()
                elif action != "end":
                    print("[WARNING] Unknown action:", action)

            if node.get("action") == "end":
                print("\n[DONE] Dialogue finished.")
                return

            # 2. Если есть listen → пропускаем (примерная логика)
            if node.get("listen"):
                print("[LISTEN] waiting for user input...")
                # user_input = input("> ")
                pass

            # 3. Проверка условий
            if "condition" in node:
                condition = node["condition"]
                result = self.actions.evaluate_condition(condition)

                if result:
                    next_node = node["yes"]
                else:
                    next_node = node["no"]

                # Если ветка "no" — вложенный объект
                if isinstance(next_node, dict):
                    # Выполнить counter
                    if "counter" in next_node:
                        getattr(self.actions, next_node["counter"])()

                    cond2 = next_node.get("condition")
                    if cond2:
                        if self.actions.evaluate_condition(cond2):
                            current = next_node["yes"]
                        else:
                            current = next_node["no"]
                        continue
                else:
                    current = next_node
                    continue

            # 4. Если нет условий — просто next
            if "next" in node:
                current = node["next"]
                continue

            print("[ERROR] Node has no next step:", current)
            return
