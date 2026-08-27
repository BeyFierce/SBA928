from __future__ import annotations

import os
from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class StructuredLLM:
    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def run(self, instructions: str, input_text: str, schema: type[T]) -> T:
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": input_text},
            ],
            response_format=schema,
        )
        message = completion.choices[0].message
        if message.parsed is None:
            raise RuntimeError(message.refusal or "The model returned no structured output.")
        return message.parsed

