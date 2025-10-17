import os
import json
import json
import re
import requests
import os
from dotenv import load_dotenv

load_dotenv()

"""
Simple interactive AI-like weather agent.

Behavior:
- Outer loop: continuously prompt the user for input (type 'exit' to quit).
- For each input, the agent emits a START step (user input), then runs an inner planning loop
  that may emit multiple PLAN steps. If the plan decides a tool is needed, the agent runs a
  TOOL step that calls a weather API (wttr.in) and includes the result. Finally the agent
  emits an OUTPUT step with the final answer.

Output format (JSON per step): { "step": "START" | "PLAN" | "TOOL" | "OUTPUT", "content": "..." }

This file intentionally uses a rule-based planner for offline reliability. If you have
an LLM API available, the planner section can easily call it instead.
"""


class WeatherTool:
    """Small wrapper around wttr.in for quick weather lookup without API keys.

    Uses: http://wttr.in/<location>?format=j1 which returns JSON.
    """

    BASE = "http://wttr.in"

    @staticmethod
    def get_weather(location: str) -> str:
        if not location:
            return "No location provided"

        url = f"{WeatherTool.BASE}/{requests.utils.requote_uri(location)}?format=j1"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                return f"Weather API returned status {resp.status_code}"
            data = resp.json()
            # wttr.in returns 'current_condition' and other fields
            cur = data.get("current_condition", [{}])[0]
            temp_c = cur.get("temp_C")
            weather_desc = cur.get("weatherDesc", [{}])[0].get("value") if cur.get("weatherDesc") else None
            feels_like = cur.get("FeelsLikeC")
            humidity = cur.get("humidity")
            return (
                f"Location: {location}\n"
                f"Temperature: {temp_c}°C (feels like {feels_like}°C)\n"
                f"Conditions: {weather_desc}\n"
                f"Humidity: {humidity}%"
            )
        except Exception as e:
            return f"Weather tool error: {e}"


class WeatherAgent:
    def __init__(self):
        self.tool = WeatherTool()

    def _emit(self, step: str, content: str):
        obj = {"step": step, "content": content}
        print(json.dumps(obj, ensure_ascii=False))

    def _needs_weather(self, text: str) -> bool:
        # Simple heuristic: user mentions 'weather' or 'temperature' or asks about a city
        keywords = ["weather", "temperature", "forecast", "rain", "sunny", "wind"]
        return any(k in text.lower() for k in keywords)

    def _extract_location(self, text: str) -> str | None:
        # Very basic extraction: look for 'in <place>' or last token
        m = re.search(r"in ([A-Za-z\s,]+)$", text.strip(), re.IGNORECASE)
        if m:
            return m.group(1).strip()
        # try 'weather CITY'
        m2 = re.search(r"weather\s+in\s+([A-Za-z\s,]+)", text, re.IGNORECASE)
        if m2:
            return m2.group(1).strip()
        # fallback: last word if looks like a place
        tokens = text.strip().split()
        if len(tokens) > 0:
            last = tokens[-1].strip().strip('?.!')
            if last.isalpha() and len(last) > 1:
                return last
        return None

    def handle_query(self, user_input: str):
        # START
        self._emit("START", user_input)

        # Inner planning loop
        plan_count = 0
        max_plans = 6
        did_tool = False
        plan_notes = []

        while plan_count < max_plans:
            plan_count += 1
            # Simple planner: decide whether to call the weather tool
            if self._needs_weather(user_input) and not did_tool:
                loc = self._extract_location(user_input)
                if not loc:
                    note = "I think user asks about weather but no clear location found. Ask for location."
                    self._emit("PLAN", note)
                    plan_notes.append(note)
                    # Ask the user for clarification and break to let them answer
                    return None
                else:
                    note = f"Call TOOL to fetch weather for '{loc}'"
                    self._emit("PLAN", note)
                    plan_notes.append(note)
                    # TOOL step
                    tool_result = self.tool.get_weather(loc)
                    self._emit("TOOL", tool_result)
                    did_tool = True
                    # after tool, continue planning to form final output
                    continue
            else:
                note = "No tool needed or already used; prepare final output."
                self._emit("PLAN", note)
                plan_notes.append(note)
                break

        # OUTPUT
        if did_tool:
            final = "Provided weather information above. Ask follow-up questions or enter another query."
        else:
            final = "I can fetch weather for a location. Ask something like: 'What's the weather in London?'"

        self._emit("OUTPUT", final)

    def run(self):
        print("Weather Agent — type a question (e.g. 'What's the weather in Paris?'). Type 'exit' to quit.")
        while True:
            try:
                user_input = input("You> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                print("Goodbye.")
                break

            # If planner needs clarification (returns None), ask user and continue
            result = self.handle_query(user_input)
            # result is None when planner asked for clarification and returned early
            # The handle already emitted PLAN asking for location. Prompt user next loop.


if __name__ == "__main__":
    agent = WeatherAgent()
    agent.run()
