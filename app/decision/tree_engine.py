# tree_engine.py
import json
from app.decision.tree_actions import TreeActions

class DecisionTreeEngine:
    def __init__(self, json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            self.tree = json.load(f)

        self.actions = TreeActions(tree=self.tree)

    def run(self, start_node="start", final_intent="fallback"):
        current = start_node

        while True:
            node = self.tree[current]
            print(f"\n=== NODE: {current} ===")

            # ----- 1. Выполнить action -----
            if "action" in node:
                action = node["action"]

                if action.startswith("say:"):
                    text = action.split("say:", 1)[1].strip()
                    self.actions.say(text)
                    self.actions.buffer_interaction(action="say", response=text)

                elif hasattr(self.actions, action):
                    getattr(self.actions, action)()
                    self.actions.buffer_interaction(action=action, response="")

                elif action == "end":
                    # Конец диалога — сохраняем всю сессию одним решением
                    self.actions.commit_session(final_intent=final_intent)
                    print("\n[DONE] Dialogue finished.")
                    return

                else:
                    print("[WARNING] Unknown action:", action)

            # ----- 2. Слушаем пользователя -----
            if node.get("listen"):
                listen_for = node.get("listen_for", "plate")
                expect_plate = listen_for == "plate"
                user_input = self.actions.listen(expect_plate=expect_plate)
                print(f"[CONTEXT] last_input = {user_input}")
                self.actions.buffer_interaction(action="listen", response="")

            # ----- 3. Проверка условий -----
            if "condition" in node:
                condition = node["condition"]
                result = self.actions.evaluate_condition(condition)

                if result:
                    next_node = node["yes"]
                else:
                    next_node = node["no"]

                # Если ветка "no" — вложенный объект с counter/condition
                if isinstance(next_node, dict):
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

            # ----- 4. Просто next -----
            elif "next" in node:
                current = node["next"]
                continue

            else:
                # Нет next и нет action — диалог закончился
                self.actions.commit_session(final_intent=final_intent)
                print("[ERROR] Node has no next step, committing session:", current)
                return
