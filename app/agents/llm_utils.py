"""
Shared helper for calling Groq (OpenAI-compatible SDK).
Groq free tier has generous limits, but we still space calls
slightly as a safety net.
"""

import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
_MODEL_NAME = "openai/gpt-oss-120b"

_MIN_SECONDS_BETWEEN_CALLS = 2
_last_call_time = [0]


def call_llm(prompt: str, max_retries: int = 3) -> str:
    """
    Call Groq's chat completion API with a single user prompt.
    Returns the raw text response. Retries on transient errors.
    """
    elapsed = time.time() - _last_call_time[0]
    if elapsed < _MIN_SECONDS_BETWEEN_CALLS:
        time.sleep(_MIN_SECONDS_BETWEEN_CALLS - elapsed)

    for attempt in range(max_retries):
        try:
            response = _client.chat.completions.create(
                model=_MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
            )
            _last_call_time[0] = time.time()
            return response.choices[0].message.content
        except Exception as e:
            wait_time = 10
            print(f"LLM call failed ({e}). Retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})...")
            time.sleep(wait_time)

    raise RuntimeError("Max retries exceeded calling Groq.")