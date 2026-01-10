import json
import os
from google import genai
from google.genai import types
from flask import current_app

class SongRoaster:
    def __init__(
        self,
        model: str = None,
        temperature: float = 1.1,
        max_tokens: int = 5,
        api_key: str = None,
    ):
        self.client = genai.Client(api_key=api_key)
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.temperature = temperature
        self.max_tokens = max_tokens

        self.system_instruction = """
        You are a funny, snarky, judgy music critic.

        Rules:
        - Roast the TRACK, not the listener.
        - Keep it playful, not hateful.
        - 1–2 sentences, max 35 words.
        - Include exactly one emoji.
        - Add 1 emoji, no insults, no harassment.
        """

    def roast_track(self, track: dict) -> str:
        prompt = (
            "Here is the currently playing track as JSON:\n"
            f"{json.dumps(track, ensure_ascii=False)}\n\n"
            "Write the roast following the rules."
        )

        resp = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction),
        )
        print(resp)

        return (resp.text or "").strip()