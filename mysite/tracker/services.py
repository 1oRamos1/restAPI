import logging
from .models import Task
from mistralai import Mistral
from django.conf import settings

mistral_client = Mistral(api_key=settings.MISTRAL_API_KEY)


def generate_and_save_summary(user_track):
    try:
        tasks = Task.objects.filter(user_learning_track=user_track, status="completed").order_by("id")
        if not tasks.exists():
            user_track.summary = "No progress yet."
            user_track.save(update_fields=['summary'])
            return user_track.summary

        progress_data = "\n".join(
            f"Title: {t.task.split('### Title:')[1].splitlines()[0].strip() if '### Title:' in t.task else 'Unknown'}\n"
            f"Grade: {t.grade}/5\n"
            f"Review: {t.review.strip()}"
            for t in tasks if t.grade is not None
        )

        prompt = (
            "Please summarize my progress.\n"
            "Here is the detailed progress so far:\n"
            f"{progress_data}\n\n"
            "Write a short summary (3–5 lines) that captures my overall progress, "
            "strengths, and areas I need to improve.\n"
            "Speak directly to me (second person). Start the summary with 'You...'.\n"
            "Do NOT repeat individual task details. Be clear and motivating.\n"
            "VERY IMPORTANT:\n"
            "- Do NOT include greetings, follow-ups or titles, just clean review."
        )

        chat_response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        concise_summary = chat_response.choices[0].message.content.strip()

        user_track.summary = concise_summary
        user_track.save(update_fields=['summary'])

        return user_track.summary

    except Exception as e:
        logging.error(f"Summary generation failed: {e}")
        return None