import logging
from rest_framework import serializers
from ..models import Task, Category, LearningTrack, UserLearningTrack
from .ai_client import mistral_client
from .ai_service import generate_track_from_prompt, extract_json_from_text

logger = logging.getLogger(__name__)


def create_custom_track(user, description, language, level):
    if language != "auto":
        prompt = f"Create a {level} track in {language} about: {description}"
    else:
        prompt = f"Create a {level} track based on: {description}. Choose the most suitable language."

    ai_response_text = generate_track_from_prompt(prompt)
    track_data = extract_json_from_text(ai_response_text)

    category_name = track_data.get('category')
    if not category_name:
        raise serializers.ValidationError("AI returned invalid track data.")

    resolved_language = track_data.get('language') or (language if language != 'auto' else 'python')

    category, _ = Category.objects.get_or_create(
        name=category_name.strip(),
        language=resolved_language
    )

    learning_track = LearningTrack.objects.create(
        title=track_data['title'],
        category=category,
        level=track_data['level'],
        is_custom=True,
        created_by=user
    )

    user_learning_track = UserLearningTrack.objects.create(
        user=user,
        learning_track=learning_track
    )

    return user_learning_track


def generate_and_save_summary(user_track):
    try:
        tasks = Task.objects.filter(
            user_learning_track=user_track,
            status="completed",
            grade__isnull=False
        ).order_by("id")

        if not tasks.exists():
            user_track.summary = "No progress yet."
            user_track.save(update_fields=["summary"])
            return user_track.summary

        progress_data = "\n".join(
            f"Title: {t.title or 'Unknown'}\n"
            f"Grade: {t.grade}/5\n"
            f"Review: {t.review.strip()}"
            for t in tasks
        )

        prompt = (
            "Please summarize my progress.\n"
            f"{progress_data}\n\n"
            "Write a short summary (3-5 lines). Speak directly to me. Start with 'You...'.\n"
            "Do NOT include greetings or titles. Be clear and motivating."
        )

        response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}],
        )
        summary = response.choices[0].message.content.strip()

        user_track.summary = summary
        user_track.save(update_fields=["summary"])
        return summary

    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        return None
