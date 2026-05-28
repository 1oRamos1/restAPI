import json
import re
import logging
from rest_framework.exceptions import ValidationError
from .ai_client import openai, mistral_client

logger = logging.getLogger(__name__)


def use_openai(user) -> bool:
    return hasattr(user, "profile") and user.profile.is_pro


def get_chat_completion(user, prompt: str, system_msg: str = "You are a helpful coding mentor.") -> str:
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": prompt},
    ]
    try:
        if use_openai(user):
            response = openai.ChatCompletion.create(
                model="gpt-4.1",
                messages=messages,
                temperature=0.7,
                timeout=10,
            )
            return response.choices[0].message["content"]
        else:
            response = mistral_client.chat.complete(
                model="ministral-3b-latest",
                messages=messages,
                temperature=0.7,
            )
            return response.choices[0].message.content
    except Exception as e:
        logger.error(f"AI Service Failure: {str(e)}")
        raise ConnectionError("AI service is temporarily unavailable.")


def extract_json_from_text(text: str):
    if "```" in text:
        text = text.replace("```json", "").replace("```", "").strip()
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if not match:
        raise ValidationError("AI response does not contain valid JSON.")
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        raise ValidationError(f"AI response JSON is malformed: {str(e)}")


def generate_track_from_prompt(prompt: str) -> str:
    system_msg = (
        "You are an AI that converts a user's learning goal into a structured JSON object. "
        "Return ONLY valid JSON, no markdown, no explanations."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=1200,
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        raise ValidationError(f"Failed to generate track: {str(e)}")