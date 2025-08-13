import openai
import json
import re
from django.conf import settings
from rest_framework.exceptions import ValidationError
from .models import Category

VALID_LEVELS = ['beginner', 'advanced', 'master']


def generate_custom_track_options(goal, language):
    prompt = f"""
The user wants to learn: "{goal}"
They prefer the programming language: {language}.

Generate 3 to 5 unique learning track options that:
- Are realistic and coherent.
- Each one has: a title, category, level (beginner/advanced/master), and a short description.
- Use categories like: Web, AI, Backend, Frontend, DevOps, Game Dev, Security, Algorithms, Data Science, etc.
- Format strictly as JSON list like:
[
  {{
    "title": "Mastering Algorithms with C++",
    "category": "Algorithms",
    "level": "advanced",
    "short_description": "Learn advanced algorithms using C++ with real-world challenges."
  }},
  ...
]
Only return a valid JSON array. No preamble, no markdown, no explanations.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=900
        )
        raw_content = response.choices[0].message.content.strip()
        print("🔍 AI TRACK OPTIONS RESPONSE:", repr(raw_content))

        options = extract_json_from_text(raw_content)
        cleaned = []

        for opt in options:
            level = opt.get("level", "").lower()
            category = opt.get("category", "").strip()

            if level not in VALID_LEVELS or not category:
                continue

            cat_obj, _ = Category.objects.get_or_create(
                name=category,
                defaults={'language': language}
            )

            cleaned.append({
                "title": opt.get("title", "").strip(),
                "category": cat_obj.name,
                "level": level,
                "short_description": opt.get("short_description", "").strip()
            })

        return cleaned

    except Exception as e:
        raise Exception(f"AI track generation failed: {str(e)}")


def extract_json_from_text(text: str):
    """
    Extracts a JSON object or array from a string. Handles responses with code blocks or trailing text.
    """
    # Strip markdown/code block fences
    if "```" in text:
        text = text.replace("```json", "").replace("```", "").strip()

    # Try to match the first JSON object or array
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if not match:
        raise ValidationError("AI response does not contain valid JSON.")

    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        raise ValidationError(f"AI response JSON is malformed. Error: {str(e)}")


def generate_track_from_prompt(prompt: str) -> str:
    """
    Uses OpenAI's ChatCompletion API to convert a learning goal into a structured learning track JSON.
    Returns the raw string for post-processing.
    """
    openai.api_key = settings.OPENAI_API_KEY

    system_msg = (
        "You are an AI that converts a user's learning goal into a structured JSON object "
        "with this exact format:\n\n"
        "{\n"
        '  "title": "Track Title",\n'
        '  "category": "Category Name",\n'
        '  "language": "python|js|cpp",\n'
        '  "level": "beginner|advanced|master",\n'
        "}\n\n"
        "Only return valid JSON. No markdown, no extra text, no explanations."
    )

    user_msg = f"Learning goal: {prompt}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.6,
            max_tokens=1200
        )

        content = response.choices[0].message['content'].strip()
        print("🔍 AI FULL TRACK RAW:", repr(content))
        return content

    except Exception as e:
        raise ValidationError(f"Failed to generate track: {str(e)}")
